// src/pose.ts
import * as tf from '@tensorflow/tfjs';
import * as posedetection from '@tensorflow-models/pose-detection';
import { createCanvas, loadImage, Image } from 'canvas';
import fetch from 'node-fetch'; // <-- ensure this is in package.json

import { POINTS, CLASS_NO } from './constants.js';

/** ===== Backend init (CPU) =====
 * CPU backend is the most portable on Spaces. It's slower than WASM/WebGL,
 * but with LIGHTNING + downscaling it stays well within the request timeout.
 */
let backendReady: Promise<void> | null = null;
export async function ensureWasmBackend() {
  if (!backendReady) {
    backendReady = (async () => {
      await tf.setBackend('cpu');
      await tf.ready();
    })();
  }
  return backendReady;
}

// One-shot initializer you can call at startup/warmup
export async function initTf() {
  await ensureWasmBackend();
  await Promise.all([loadModel(), getDetector()]);
}

/** ===== Classifier model (unchanged) ===== */
const MODEL_URL =
  process.env.POSE_CLASSIFIER_URL ??
  'https://models.s3.jp-tok.cloud-object-storage.appdomain.cloud/model.json';

let modelPromise: Promise<tf.LayersModel> | null = null;
export async function loadModel(): Promise<tf.LayersModel> {
  if (!modelPromise) {
    modelPromise = tf.loadLayersModel(MODEL_URL);
  }
  return modelPromise;
}

/** ===== MoveNet (use LIGHTNING for speed) ===== */
let detectorPromise: Promise<posedetection.PoseDetector> | null = null;
async function getDetector(): Promise<posedetection.PoseDetector> {
  if (!detectorPromise) {
    await ensureWasmBackend();
    detectorPromise = posedetection.createDetector(
      posedetection.SupportedModels.MoveNet,
      {
        modelType: posedetection.movenet.modelType.SINGLEPOSE_LIGHTNING, // faster than THUNDER
      }
    );
  }
  return detectorPromise;
}

/** ===== Helpers ===== */

// Fetch an image with a timeout, then load via canvas
async function fetchImageWithTimeout(url: string, ms = 8000): Promise<Image> {
  const ctrl = new AbortController();
  const id = setTimeout(() => ctrl.abort(), ms);
  try {
    const r = await fetch(url, { signal: ctrl.signal });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const buf = Buffer.from(await r.arrayBuffer());
    return await loadImage(buf);
  } finally {
    clearTimeout(id);
  }
}

// Downscale while keeping aspect ratio (important for speed)
function toResizedCanvas(img: Image, maxSide = 512) {
  let { width: w, height: h } = img;
  const scale = Math.min(1, maxSide / Math.max(w, h));
  const W = Math.max(1, Math.round(w * scale));
  const H = Math.max(1, Math.round(h * scale));
  const canvas = createCanvas(W, H);
  const ctx = canvas.getContext('2d');
  ctx.drawImage(img, 0, 0, W, H);
  return canvas;
}

// Image/B64 -> Canvas (downscaled)
async function loadImageToCanvas(input: { imageUrl?: string; imageB64?: string }) {
  let img: Image;
  if (input.imageUrl) {
    img = await fetchImageWithTimeout(input.imageUrl, 8000);
  } else if (input.imageB64) {
    const buf = Buffer.from(input.imageB64, 'base64');
    img = await loadImage(buf);
  } else {
    throw new Error('Provide imageUrl or imageB64');
  }
  return toResizedCanvas(img, 512);
}

// Promise timeout helper
function withTimeout<T>(p: Promise<T>, ms = 8000, msg = 'Timed out') {
  return Promise.race<T>([
    p,
    new Promise<T>((_, rej) => setTimeout(() => rej(new Error(msg)), ms)),
  ]);
}

/** ===== Image -> 17×2 normalized landmarks ===== */
export async function detectLandmarksFromImage(input: { imageUrl?: string; imageB64?: string }): Promise<number[][]> {
  const canvas = await loadImageToCanvas(input);
  const detector = await getDetector();

  // Guard estimatePoses with an 8s timeout
  const poses = await withTimeout(
    detector.estimatePoses(canvas as any, { flipHorizontal: false }),
    8000,
    'pose detection timed out'
  );

  if (!poses.length || !poses[0].keypoints || poses[0].keypoints.length < 17) {
    throw new Error('No pose detected');
  }

  const kp = poses[0].keypoints.slice(0, 17);
  const w = canvas.width, h = canvas.height;
  const landmarks = kp.map((k) => [k.x / w, k.y / h]);
  return landmarks;
}

/** ===== Preprocess + Classify (same as before) ===== */
function get_center_point(landmarks: tf.Tensor2D, leftIdx: number, rightIdx: number) {
  const left = tf.gather(landmarks, leftIdx, 0);
  const right = tf.gather(landmarks, rightIdx, 0);
  return tf.add(tf.mul(left, 0.5), tf.mul(right, 0.5));
}

function get_pose_size(landmarks: tf.Tensor2D, torsoSizeMultiplier = 2.5) {
  const hipsCenter = get_center_point(landmarks, POINTS.LEFT_HIP, POINTS.RIGHT_HIP);
  const shouldersCenter = get_center_point(landmarks, POINTS.LEFT_SHOULDER, POINTS.RIGHT_SHOULDER);
  const torsoSize = tf.norm(tf.sub(shouldersCenter, hipsCenter));

  let poseCenter = get_center_point(landmarks, POINTS.LEFT_HIP, POINTS.RIGHT_HIP);
  poseCenter = tf.expandDims(poseCenter, 0);
  poseCenter = tf.tile(poseCenter, [17, 1]);

  const d = tf.sub(landmarks, poseCenter);
  const maxDist = tf.max(tf.norm(d, 'euclidean', 1));
  return tf.maximum(tf.mul(torsoSize, torsoSizeMultiplier), maxDist);
}

function normalize_pose_landmarks(landmarks: tf.Tensor2D) {
  let poseCenter = get_center_point(landmarks, POINTS.LEFT_HIP, POINTS.RIGHT_HIP);
  poseCenter = tf.expandDims(poseCenter, 0);
  poseCenter = tf.tile(poseCenter, [17, 1]);
  const shifted = tf.sub(landmarks, poseCenter);
  const poseSize = get_pose_size(landmarks);
  return tf.div(shifted, poseSize) as tf.Tensor2D;
}

function landmarks_to_embedding(landmarks: tf.Tensor2D) {
  const norm = normalize_pose_landmarks(landmarks);
  return tf.reshape(norm, [1, 34]);
}

export async function classifyLandmarks(landmarksArray: number[][], threshold = 0.8) {
  await ensureWasmBackend(); // make sure backend is ready

  if (!Array.isArray(landmarksArray) || landmarksArray.length !== 17) {
    throw new Error('landmarks must be 17x2 array');
  }
  const model = await loadModel();

  const landmarks = tf.tensor2d(landmarksArray, [17, 2]);
  const input = landmarks_to_embedding(landmarks);
  const logits = model.predict(input) as tf.Tensor;
  const scores = (await logits.array()) as number[][];
  input.dispose(); logits.dispose(); landmarks.dispose();

  const probs = scores[0];
  const entries = Object.entries(CLASS_NO).map(([name, idx]) => [name, probs[idx] ?? 0] as const);
  entries.sort((a, b) => b[1] - a[1]);

  const [bestName, bestScore] = entries[0];
  return {
    top: { name: bestName, score: bestScore },
    scores: Object.fromEntries(entries),
    passed: bestScore >= threshold,
    threshold,
  };
}

// For compatibility with older callers
export async function predictPose(input: { imageUrl?: string; imageB64?: string }) {
  const landmarks = await detectLandmarksFromImage(input);
  return classifyLandmarks(landmarks, 0.8);
}