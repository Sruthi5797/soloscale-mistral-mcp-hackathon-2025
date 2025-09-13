from __future__ import annotations
import os, json
from typing import Optional, Tuple
import urllib.request

POSEFLOW_BACKEND_URL = os.getenv("POSEFLOW_BACKEND_URL", "http://127.0.0.1:8787")

def predict_pose_using_asanaai(image_url: Optional[str]=None, image_b64: Optional[str]=None) -> Tuple[str, float]:
    # renamed to poseflow_backend in concept; keeping function name to avoid ref churn
    if not image_url:
        raise ValueError("image_url required for backend v0")
    payload = json.dumps({"image_url": image_url}).encode("utf-8")
    req = urllib.request.Request(
        f"{POSEFLOW_BACKEND_URL}/predict",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        pose = data.get("pose", "Unknown")
        conf = float(data.get("confidence", 0.0))
        return pose, conf