import express from "express";
import fetch from "node-fetch";
import sharp from "sharp";
import * as tf from "@tensorflow/tfjs-node";
import * as posenet from "@tensorflow-models/posenet";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const app = express();
app.use(express.json({ limit: "10mb" }));

let NET;
async function getNet() {
  if (!NET) {
    NET = await posenet.load({
      architecture: "MobileNetV1",
      outputStride: 16,
      inputResolution: { width: 257, height: 257 },
      multiplier: 0.75
    });
    console.log("[poseflow-backend] PoseNet loaded");
  }
  return NET;
}

// load reference pose vectors
const REF_PATH = path.join(__dirname, "poses.ref.json");
let REFS = {};
try {
  REFS = JSON.parse(fs.readFileSync(REF_PATH, "utf8"));
  console.log("[poseflow-backend] loaded poses.ref.json with labels:", Object.keys(REFS));
} catch (e) {
  console.warn("[poseflow-backend] poses.ref.json missing, returning Unknown");
  REFS = {};
}

async function tensorFromImage({ image_url, image_b64 }) {
  let buf;
  if (image_b64) {
    buf = Buffer.from(image_b64, "base64");
  } else if (image_url) {
    const r = await fetch(image_url);
    if (!r.ok) throw new Error(`fetch failed: ${r.status}`);
    buf = Buffer.from(await r.arrayBuffer());
  } else {
    throw new Error("Provide image_url or image_b64");
  }

  const out = await sharp(buf).resize(257, 257, { fit: "inside" }).removeAlpha().raw().toBuffer({ resolveWithObject: true });
  const { data, info } = out;
  return tf.tensor3d(data, [info.height, info.width, info.channels], "int32");
}

function flattenKeypoints(kps) {
  return kps.flatMap(kp => [kp.position.x / 257, kp.position.y / 257, kp.score ?? 1]);
}

function cosine(a, b) {
  if (!a.length || !b.length || a.length !== b.length) return 0;
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    na += a[i] * a[i];
    nb += b[i] * b[i];
  }
  return dot / (Math.sqrt(na) * Math.sqrt(nb) + 1e-9);
}

app.get("/health", (_req, res) => res.json({ ok: true }));

app.post("/infer", async (req, res) => {
  try {
    const { image_url, image_b64 } = req.body || {};
    if (!image_url && !image_b64) return res.status(400).json({ error: "Provide image_url or image_b64" });

    const net = await getNet();
    const img = await tensorFromImage({ image_url, image_b64 });
    const pose = await net.estimateSinglePose(img, { flipHorizontal: false });
    img.dispose();

    const feat = flattenKeypoints(pose.keypoints);

    let best = { label: "Unknown", sim: 0.0 };
    for (const [label, ref] of Object.entries(REFS)) {
      const s = cosine(feat, ref);
      if (s > best.sim) best = { label, sim: s };
    }

    res.json({
      pose: best.label,
      confidence: Number(best.sim.toFixed(3)),
      keypoints: pose.keypoints.map(k => ({ part: k.part, x: k.position.x, y: k.position.y, s: k.score }))
    });
  } catch (e) {
    console.error("[/infer] error:", e);
    res.status(500).json({ error: "inference_error" });
  }
});

const PORT = process.env.POSEFLOW_BACKEND_PORT || 4000;
app.listen(PORT, () => console.log(`[poseflow-backend] listening on :${PORT}`));