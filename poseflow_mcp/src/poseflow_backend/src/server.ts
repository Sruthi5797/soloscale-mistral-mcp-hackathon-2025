// src/server.ts
import express from 'express';
import cors from 'cors';
import { z } from 'zod';
import {
  classifyLandmarks,
  loadModel,
  initTf,
  detectLandmarksFromImage,
} from "./pose.js";

const app = express();
app.use(cors());
app.use(express.json({ limit: '10mb', strict: true }));

// ---------------- Pose catalog (5 poses) ----------------
const ASSETS_BASE =
  process.env.POSE_ASSETS_BASE ??
  "https://huggingface.co/spaces/Mr-Saab29/poseflow_backend/resolve/main/file/assets";

export const POSES = ["Warrior", "Cobra", "Tree", "Triangle", "Dog"] as const;
type PoseName = typeof POSES[number];

const REF_IMAGES: Record<PoseName, string> = {
  Cobra:    `${ASSETS_BASE}/cobra.jpg`,
  Dog:      `${ASSETS_BASE}/dog.jpg`,
  Triangle: `${ASSETS_BASE}/traingle.jpg`, // note: file is spelled "traingle.jpg"
  Tree:     `${ASSETS_BASE}/tree.jpg`,
  Warrior:  `${ASSETS_BASE}/warrior.jpg`,
};

// ---------------- Info / health ----------------
app.get('/', (_req, res) =>
  res.json({
    ok: true,
    service: 'poseflow-backend',
    routes: ['/health', '/warmup', '/poses', '/classify', '/pose/predict', '/pose/verify'],
  })
);
app.get('/health', (_req, res) => res.json({ ok: true }));

// List the available poses and their reference URLs (for your UI)
app.get('/poses', (_req, res) => {
  res.json({
    poses: POSES.map((p) => ({ name: p, referenceUrl: REF_IMAGES[p] })),
  });
});

// ---------------- Warmup ----------------
app.post("/warmup", async (_req, res) => {
  try {
    await initTf();      // init backend + load model
    return res.json({ ok: true, warmed: true });
  } catch (e: any) {
    console.error("warmup error:", e);
    return res.status(500).json({ ok: false, error: "warmup_failed", message: e?.message ?? String(e) });
  }
});

// ---------------- Schemas ----------------
const Pair = z.tuple([z.number(), z.number()]);
const Landmarks = z.array(Pair).length(17);
const Threshold = z.number().min(0).max(1).default(0.8);

const ClassifyBody = z.object({
  landmarks: Landmarks,
  threshold: Threshold.optional(),
});

const PredictBody = z.object({
  landmarks: Landmarks.optional(),
  imageUrl: z.string().url().optional(),
  imageB64: z.string().min(1).optional(),
  threshold: Threshold.optional(),
}).refine((b) => !!b.landmarks || !!b.imageUrl || !!b.imageB64, {
  message: 'Provide either `landmarks` OR (`imageUrl` | `imageB64`).',
  path: ['landmarks'],
});

// User chooses a pose and uploads an image; we verify that pose’s probability
const VerifyBody = z.object({
  expectedPose: z.enum(POSES),
  imageUrl: z.string().url().optional(),
  imageB64: z.string().min(1).optional(),
  threshold: Threshold.optional(),
}).refine((b) => !!b.imageUrl || !!b.imageB64, {
  message: 'Provide `imageUrl` or `imageB64`.',
  path: ['imageUrl'],
});

// ---------------- Routes ----------------
app.post('/classify', async (req, res) => {
  const parsed = ClassifyBody.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: 'bad_request', details: parsed.error.errors });
  try {
    const { landmarks, threshold } = parsed.data;
    const out = await classifyLandmarks(landmarks, threshold ?? 0.8);
    res.json(out);
  } catch (e: any) {
    console.error('classify error:', e);
    res.status(500).json({ error: 'inference_failed', message: e?.message ?? String(e) });
  }
});

app.get('/pose/predict', (_req, res) =>
  res.json({ ok: true, usage: 'POST /pose/predict {landmarks:[[x,y]x17], threshold?} or {imageUrl|imageB64}' })
);

app.post("/pose/predict", async (req, res) => {
  const parsed = PredictBody.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ error: "bad_request", details: parsed.error.errors });
  }
  const { landmarks, imageUrl, imageB64, threshold } = parsed.data;

  try {
    if (landmarks) {
      const out = await classifyLandmarks(landmarks, threshold ?? 0.8);
      return res.json(out);
    }
    if (imageUrl || imageB64) {
      const lm = await detectLandmarksFromImage({ imageUrl, imageB64 });
      const out = await classifyLandmarks(lm, threshold ?? 0.8);
      return res.json(out);
    }
    return res.status(400).json({ error: "bad_request", message: "Provide landmarks or imageUrl/imageB64" });
  } catch (e: any) {
    console.error("predict error:", e);
    return res.status(500).json({ error: "inference_failed", message: e?.message ?? String(e) });
  }
});

// NEW: verify a specific pose using the classifier probability for that pose
app.post("/pose/verify", async (req, res) => {
  const parsed = VerifyBody.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ error: "bad_request", details: parsed.error.errors });
  }
  const { expectedPose, imageUrl, imageB64, threshold } = parsed.data;
  const th = threshold ?? 0.8;

  try {
    const landmarks = await detectLandmarksFromImage({ imageUrl, imageB64 });
    const result = await classifyLandmarks(landmarks, th);

    const expectedScore = Number(result.scores?.[expectedPose] ?? 0);
    const passed = expectedScore >= th;

    return res.json({
      ok: true,
      expectedPose,
      referenceUrl: REF_IMAGES[expectedPose],
      threshold: th,
      passed,
      expectedScore,
      top: result.top,
      scores: result.scores,
    });
  } catch (e: any) {
    console.error("verify error:", e);
    return res.status(500).json({ error: "inference_failed", message: e?.message ?? String(e) });
  }
});

// ---------------- Start ----------------
const port = Number(process.env.PORT || 7860);

initTf()
  .catch((e) => console.warn("initTf failed (will lazily init later):", e))
  .finally(() => {
    app.listen(port, "0.0.0.0", () => {
      console.log(`poseflow_backend listening on http://0.0.0.0:${port}`);
    });
  });

export default app;