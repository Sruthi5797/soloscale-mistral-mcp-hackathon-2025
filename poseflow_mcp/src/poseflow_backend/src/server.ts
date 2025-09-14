import express from 'express';
import cors from 'cors';
import { z } from 'zod';
import { classifyLandmarks, loadModel } from './pose.js';

const app = express();
app.use(cors());
app.use(express.json({ limit: '10mb', strict: true }));

// Info/health
app.get('/', (_req, res) =>
  res.json({ ok: true, service: 'poseflow-backend', routes: ['/health', '/warmup', '/classify', '/pose/predict'] })
);
app.get('/health', (_req, res) => res.json({ ok: true }));

// Warm model (optional)
app.post('/warmup', async (_req, res) => {
  await loadModel();
  res.json({ ok: true, warmed: true });
});

// Schemas
const Pair = z.tuple([z.number(), z.number()]);
const Landmarks = z.array(Pair).length(17);
const Threshold = z.number().min(0).max(1).default(0.8);

const ClassifyBody = z.object({
  landmarks: Landmarks,
  threshold: Threshold.optional(),
});

const PredictBody = z
  .object({
    landmarks: Landmarks.optional(),
    imageUrl: z.string().url().optional(),  // not implemented path
    imageB64: z.string().min(1).optional(), // not implemented path
    threshold: Threshold.optional(),
  })
  .refine((b) => !!b.landmarks || !!b.imageUrl || !!b.imageB64, {
    message: 'Provide either `landmarks` OR (`imageUrl` | `imageB64`).',
    path: ['landmarks'],
  });

// Routes
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

app.post('/pose/predict', async (req, res) => {
  const parsed = PredictBody.safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ error: 'bad_request', details: parsed.error.errors });

  const { landmarks, imageUrl, imageB64, threshold } = parsed.data;
  try {
    if (landmarks) {
      const out = await classifyLandmarks(landmarks, threshold ?? 0.8);
      return res.json(out);
    }
    return res.status(501).json({
      error: 'not_implemented',
      message:
        'Server-side image → landmarks not implemented. Send `landmarks`, or add detection then call classifyLandmarks(landmarks).',
      received: { hasImageUrl: !!imageUrl, hasImageB64: !!imageB64 },
    });
  } catch (e: any) {
    console.error('predict error:', e);
    return res.status(500).json({ error: 'inference_failed', message: e?.message ?? String(e) });
  }
});

// Start
const port = Number(process.env.PORT || 4000);
app.listen(port, '0.0.0.0', () => console.log(`poseflow-backend listening on :${port}`));

export default app;