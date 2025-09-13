from __future__ import annotations
from typing import Optional, Tuple
import numpy as np, cv2, base64, urllib.request

try:
    import mediapipe as mp
except Exception:
    mp = None

def _read_image_bgr(image_url: Optional[str]=None, image_b64: Optional[str]=None):
    if image_b64:
        arr = np.frombuffer(base64.b64decode(image_b64), dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image_url:
        with urllib.request.urlopen(image_url) as resp:
            data = resp.read()
        arr = np.frombuffer(data, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    raise ValueError("Provide image_url or image_b64")

def angle(lm, a, b, c) -> float:
    import math
    def to_xy(i): return np.array([lm[i].x, lm[i].y])
    A, B, C = to_xy(a), to_xy(b), to_xy(c)
    BA, BC = A - B, C - B
    cosang = np.dot(BA, BC) / (np.linalg.norm(BA)*np.linalg.norm(BC) + 1e-8)
    cosang = np.clip(cosang, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosang)))

def predict_pose_fallback(image_url: Optional[str]=None, image_b64: Optional[str]=None) -> Tuple[str,float]:
    if mp is None:
        return ("Unknown", 0.0)
    img = _read_image_bgr(image_url, image_b64)
    with mp.solutions.pose.Pose(static_image_mode=True) as pose:
        res = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if not res.pose_landmarks:
            return ("NoPerson", 0.0)
        lm = res.pose_landmarks.landmark
        left_knee  = angle(lm, 23, 25, 27)
        right_knee = angle(lm, 24, 26, 28)
        left_elbow  = angle(lm, 11, 13, 15)
        right_elbow = angle(lm, 12, 14, 16)
        elbows_straight = (left_elbow > 160 and right_elbow > 160)
        front_knee_bent = (left_knee < 120 or right_knee < 120)
        if elbows_straight and front_knee_bent:
            return ("WarriorII", 0.75)
        if elbows_straight and left_knee > 165 and right_knee > 165:
            return ("Mountain", 0.7)
        return ("Unknown", 0.4)
