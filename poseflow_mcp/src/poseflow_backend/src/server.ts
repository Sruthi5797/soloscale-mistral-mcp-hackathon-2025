import express from "express";
import cors from "cors";
import { z } from "zod";
import { classifyLandmarks, loadModel } from "./pose.js";

const app = express();
app.use(cors());
app.use(express.json({ limit: "10mb", strict: true }));

// ---------- Health / Info ----------
app.get("/", (_req, res) =>
  res.json({ ok: true, service: "poseflow-backend", routes: ["/health", "/warmup", "/classify", "/pose/predict"] })
);
app.get("/health", (_req, res) => res.json({ ok: true }));

// ---------- Warm model (optional) ----------
app.post("/warmup", async (_req, res) => {
  await loadModel();
  res.json({ ok: true, warmed: true });
});

// ---------- Schemas ----------
const Pair = z.tuple([z.number(), z.number()]);
const LandmarksSchema = z.array(Pair).length(17); // 17 keypoints [[x,y],...]
const Threshold = z.number().min(0).max(1).default(0.8);

const ClassifyBody = z.object({
  landmarks: LandmarksSchema,
  threshold: Threshold.optional(),
});

// Accept EITHER landmarks OR imageUrl/imageB64
const PredictBody = z
  .object({
    // Option A: precomputed landmarks (preferred)
    landmarks: LandmarksSchema.optional(),
    // Option B: image for server-side detection (not yet implemented)
    imageUrl: z.string().url().optional(),
    imageB64: z.string().min(1).optional(),
    threshold: Threshold.optional(),
  })
  .refine((b) => !!b.landmarks || !!b.imageUrl || !!b.imageB64, {
    message: "Provide either `landmarks` OR (`imageUrl` | `imageB64`).",
    path: ["landmarks"],
  });

// ---------- Routes ----------

/** POST /classify  { landmarks: [[x,y],...17], threshold? } */
app.post("/classify", async (req, res) => {
  const parsed = ClassifyBody.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ error: "bad_request", details: parsed.error.errors });
  }
  try {
    const { landmarks, threshold } = parsed.data;
    const out = await classifyLandmarks(landmarks, threshold ?? 0.8);
    return res.json(out);
  } catch (e: any) {
    console.error("classify error:", e);
    return res.status(500).json({ error: "inference_failed", message: e?.message ?? String(e) });
  }
});

/** GET /pose/predict (mini docs) */
app.get("/pose/predict", (_req, res) =>
  res.json({
    ok: true,
    usage: "POST /pose/predict with either {landmarks:[[x,y]x17], threshold?} OR {imageUrl|imageB64, threshold?}",
  })
);

/** POST /pose/predict
 * Body: { landmarks? | imageUrl? | imageB64?, threshold? }
 * If landmarks are provided, we classify immediately.
 * If only image is provided, we currently return 501 until detection is wired.
 */
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

    // TODO: implement server-side detection (MoveNet) from image → landmarks.
    // For hackathon stability, respond clearly for now:
    return res.status(501).json({
      error: "not_implemented",
      message:
        "Server-side image → landmarks is not implemented yet. Send `landmarks`, or implement detection then call classifyLandmarks(landmarks).",
      received: { hasImageUrl: !!imageUrl, hasImageB64: !!imageB64 },
    });
  } catch (e: any) {
    console.error("predict error:", e);
    return res.status(500).json({ error: "inference_failed", message: e?.message ?? String(e) });
  }
});

// ---------- Start ----------
const port = Number(process.env.PORT || 4000);
app.listen(port, "0.0.0.0", () => {
  console.log(`poseflow_backend listening on http://localhost:${port}`);
});

export default app;