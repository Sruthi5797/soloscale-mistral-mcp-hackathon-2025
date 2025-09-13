from __future__ import annotations
from typing import Optional, Tuple

# Implement this to call the AsanaAi repo
def predict_pose_using_asanaai(image_url: Optional[str]=None, image_b64: Optional[str]=None) -> Tuple[str,float]:
    """Return (pose_name, confidence) using the AsanaAi repo's predictor."""
    raise NotImplementedError("Wire AsanaAi predictor here")
