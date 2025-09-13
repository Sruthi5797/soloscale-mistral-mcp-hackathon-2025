import * as tf from '@tensorflow/tfjs';
import { POINTS, CLASS_NO } from './constants.js';

const MODEL_URL = process.env.POSE_CLASSIFIER_URL
  ?? 'https://models.s3.jp-tok.cloud-object-storage.appdomain.cloud/model.json';

let modelPromise: Promise<tf.LayersModel> | null = null;

export async function loadModel(): Promise<tf.LayersModel> {
  if (!modelPromise) {
    modelPromise = tf.loadLayersModel(MODEL_URL);
  }
  return modelPromise;
}

// --- Preprocessing from YogaSmart (ported) ---

function get_center_point(landmarks: tf.Tensor2D, leftIdx: number, rightIdx: number) {
  const left = tf.gather(landmarks, leftIdx, 0);   // shape [2]
  const right = tf.gather(landmarks, rightIdx, 0); // shape [2]
  return tf.add(tf.mul(left, 0.5), tf.mul(right, 0.5)); // [2]
}

function get_pose_size(landmarks: tf.Tensor2D, torsoSizeMultiplier = 2.5) {
  const hipsCenter = get_center_point(landmarks, POINTS.LEFT_HIP, POINTS.RIGHT_HIP);
  const shouldersCenter = get_center_point(landmarks, POINTS.LEFT_SHOULDER, POINTS.RIGHT_SHOULDER);
  const torsoSize = tf.norm(tf.sub(shouldersCenter, hipsCenter));

  let poseCenter = get_center_point(landmarks, POINTS.LEFT_HIP, POINTS.RIGHT_HIP); // [2]
  poseCenter = tf.expandDims(poseCenter, 0); // [1,2]
  poseCenter = tf.tile(poseCenter, [17, 1]); // [17,2]

  const d = tf.sub(landmarks, poseCenter); // [17,2]
  const maxDist = tf.max(tf.norm(d, 'euclidean', 1)); // scalar
  return tf.maximum(tf.mul(torsoSize, torsoSizeMultiplier), maxDist);
}

function normalize_pose_landmarks(landmarks: tf.Tensor2D) {
  let poseCenter = get_center_point(landmarks, POINTS.LEFT_HIP, POINTS.RIGHT_HIP); // [2]
  poseCenter = tf.expandDims(poseCenter, 0); // [1,2]
  poseCenter = tf.tile(poseCenter, [17, 1]); // [17,2]
  let shifted = tf.sub(landmarks, poseCenter); // [17,2]

  const poseSize = get_pose_size(landmarks); // scalar
  return tf.div(shifted, poseSize) as tf.Tensor2D; // [17,2]
}

function landmarks_to_embedding(landmarks: tf.Tensor2D) {
  const norm = normalize_pose_landmarks(landmarks); // [17,2]
  const emb = tf.reshape(norm, [1, 34]); // [1,34]
  return emb;
}

/**
 * Classify from raw landmarks: landmarks must be 17x2 (xy) in image coordinates.
 * Returns sorted scores + best pose.
 */
export async function classifyLandmarks(
  landmarksArray: number[][],
  threshold = 0.8
) {
  if (!Array.isArray(landmarksArray) || landmarksArray.length !== 17) {
    throw new Error('landmarks must be 17x2 array');
  }
  const model = await loadModel();

  const landmarks = tf.tensor2d(landmarksArray, [17, 2]); // [17,2]
  const input = landmarks_to_embedding(landmarks);        // [1,34]
  const logits = model.predict(input) as tf.Tensor;       // [1, C]
  const scores = await logits.array() as number[][];
  input.dispose(); logits.dispose(); landmarks.dispose();

  const probs = scores[0]; // [C]
  // Build name->score map from CLASS_NO
  const entries = Object.entries(CLASS_NO).map(([name, idx]) => [name, probs[idx] ?? 0] as const);
  entries.sort((a, b) => b[1] - a[1]);

  const [bestName, bestScore] = entries[0];
  return {
    top: { name: bestName, score: bestScore },
    scores: Object.fromEntries(entries),
    passed: bestScore >= threshold,
    threshold
  };
}
export async function predictPose(input: { imageUrl?: string; imageB64?: string }) {
  // TODO: run your TFJS pipeline here and produce a result
  // For now, a stub so the route works:
  return {
    top: { name: "WarriorII", score: 0.93 },
    scores: { WarriorII: 0.93, Tree: 0.02, Cobra: 0.01 },
    passed: 0.93 >= 0.8,
    threshold: 0.8,
  };
}