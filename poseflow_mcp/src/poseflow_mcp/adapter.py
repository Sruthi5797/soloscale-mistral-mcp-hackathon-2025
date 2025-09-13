import httpx
import os

POSEFLOW_BACKEND = os.getenv("POSEFLOW_BACKEND_URL", "http://localhost:4000")

def predict_pose_using_poseflow(image_url: str | None = None, image_b64: str | None = None):
    payload = {"image_url": image_url, "image_b64": image_b64}
    r = httpx.post(f"{POSEFLOW_BACKEND}/infer", json=payload, timeout=30.0)
    r.raise_for_status()
    data = r.json()
    return data["pose"], data["confidence"] 