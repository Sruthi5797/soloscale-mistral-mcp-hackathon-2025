"""
soloscale_poseflow — MCP Server (template style) with /pose proxy
"""

from __future__ import annotations
import os
import requests
from typing import Optional, Dict, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

# ---- NEW: proxy & child-process imports ----
import asyncio
import subprocess
from fastapi import Request, Response
import httpx

# ---------- helper imports (with safe fallbacks) ----------
try:
    from src.poseflow_mcp.notifications import send_email, send_slack  # type: ignore
except Exception:
    async def send_slack(webhook: str, text: str) -> Dict[str, Any]:
        return {"ok": True, "webhook": webhook, "text": text}

    def send_email(subject: str, body: str, to_email: str) -> Dict[str, Any]:
        return {"ok": True, "to": to_email, "subject": subject, "body": body}

# ---------- MCP server ----------
PORT = int(os.environ.get("PORT", "3000"))
mcp = FastMCP("soloscale_poseflow", port=PORT, stateless_http=True, debug=True)

# Get the underlying FastAPI app (so we can add routes / lifecycle hooks)
app = mcp.streamable_http_app()

# ---------- Backend selection ----------
# If POSEFLOW_BACKEND_URL is set, we call that URL directly (no child / no proxy).
# Otherwise, we spawn the Node backend locally on 4000 and proxy /pose/* to it.
REMOTE_BACKEND = os.environ.get("POSEFLOW_BACKEND_URL")
NODE_PORT = int(os.environ.get("BACKEND_PORT", "4000"))
NODE_DIR = os.path.join(os.path.dirname(__file__), "src", "poseflow_backend")
NODE_CMD = ["node", "dist/server.js"]  # assumes you've built TS -> dist

# Where record_pose will send requests:
if REMOTE_BACKEND:
    POSE_API = REMOTE_BACKEND.rstrip("/")
else:
    # Default to calling the SAME MCP app (port 3000), which will proxy /pose/* → 4000
    POSE_API = f"http://127.0.0.1:{PORT}"

node_proc: subprocess.Popen | None = None

# ---------- Only spawn+proxy if NO remote backend ----------
if not REMOTE_BACKEND:
    @app.on_event("startup")
    async def _start_node():
        """Spawn Node backend but don't block MCP readiness."""
        global node_proc
        try:
            env = os.environ.copy()
            env["PORT"] = str(NODE_PORT)
            node_proc = subprocess.Popen(
                NODE_CMD,
                cwd=NODE_DIR,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            print(f"[poseflow] spawned node backend on :{NODE_PORT}")
        except Exception as e:
            print(f"[poseflow] WARN failed to start Node backend: {e}")

        # best-effort warm check in the background (does NOT block MCP)
        async def _wait_health():
            for _ in range(50):
                try:
                    async with httpx.AsyncClient() as client:
                        r = await client.get(f"http://127.0.0.1:{NODE_PORT}/health", timeout=0.5)
                        if r.status_code == 200:
                            print("[poseflow] node backend healthy")
                            return
                except Exception:
                    pass
                await asyncio.sleep(0.2)
            print("[poseflow] WARN node backend did not report healthy in time")

        asyncio.create_task(_wait_health())

    @app.on_event("shutdown")
    def _stop_node():
        global node_proc
        if node_proc and node_proc.poll() is None:
            try:
                node_proc.terminate()
                print("[poseflow] node backend terminated")
            except Exception:
                pass

    # Proxy any /pose/* calls to the node backend on 4000
    @app.api_route("/pose/{rest:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def proxy_pose(rest: str, request: Request):
        target = f"http://127.0.0.1:{NODE_PORT}/pose/{rest}"
        body = await request.body()
        headers = dict(request.headers)
        headers.pop("host", None)

        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method=request.method,
                url=target,
                content=body if body else None,
                headers=headers,
                timeout=30.0,
            )
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers={"content-type": resp.headers.get("content-type", "application/json")},
        )

# Pose backend base (either remote URL or the MCP itself for proxy)
STATE = {"threshold": 0.8}

# ---------------- internal helpers ----------------
def _recommend(pose: str, score: float, threshold: float) -> str:
    """Human-friendly coaching based on similarity score."""
    if score >= max(threshold, 0.9):
        return f"🎉 Bravo! {pose} looks great. Hold for 3 slow breaths."
    if score >= threshold:
        return f"Nice {pose}. Micro-adjust: lengthen spine and keep shoulders relaxed."
    if score >= threshold - 0.1:
        return f"You're close to {pose}. Try aligning hips and press evenly through the feet."
    return f"Keep adjusting toward {pose}. Start with foundation: stance width and knee tracking."

# 1) Set threshold ------------------------------------------------------
@mcp.tool(title="Set Threshold", description="Set success threshold for pose achievement (0.0–1.0).")
def set_threshold(value: float = Field(description="0.0–1.0 threshold")) -> Dict[str, float]:
    v = max(0.0, min(1.0, float(value)))
    STATE["threshold"] = v
    return {"threshold": v}

# 2) Record + Feedback (pose + celebrate/adjust in one) -----------------
@mcp.tool(
    title="Record Pose",
    description=(
        "Classify a pose via poseflow_backend. Prefer sending `landmarks` (17x2). "
        "Image inputs are accepted but server-side detection may not be implemented."
    ),
)
def record_pose(
    landmarks: Optional[list[list[float]]] = Field(default=None, description="17x2 array of (x,y) keypoints"),
    image_url: Optional[str] = Field(default=None, description="Public image URL (optional)"),
    image_b64: Optional[str] = Field(default=None, description="Base64-encoded image (optional)"),
    threshold: Optional[float] = Field(default=None, description="Override threshold (0.0–1.0)."),
) -> Dict[str, Any]:
    th = float(threshold) if threshold is not None else float(STATE["threshold"])

    if not (landmarks or image_url or image_b64):
        return {"error": "Provide `landmarks` or `image_url`/`image_b64`"}

    payload: Dict[str, Any] = {"threshold": th}
    if landmarks:
        payload["landmarks"] = landmarks
    if image_url:
        payload["imageUrl"] = image_url
    if image_b64:
        payload["imageB64"] = image_b64

    try:
        r = requests.post(f"{POSE_API}/pose/predict", json=payload, timeout=30)
        data = r.json()
    except Exception as e:
        return {"error": "backend_unreachable", "details": str(e), "backend": POSE_API}

    if r.status_code != 200:
        # e.g., { error: "not_implemented", ... } for image-only path
        return {"error": "backend_error", "status": r.status_code, "data": data}

    try:
        pose = data["top"]["name"]
        score = float(data["top"]["score"])
        passed = bool(data.get("passed"))
    except Exception:
        return {"error": "unexpected_backend_shape", "data": data}

    rec = _recommend(pose, score, th)
    return {
        "pose": pose,
        "similarity": round(score, 3),
        "passed": passed,
        "threshold_used": th,
        "recommendation": rec,
        "scores": data.get("scores", {}),
    }

# 3) Ask + Send to teacher (combined) -----------------------------------
@mcp.tool(
    title="Notify Teacher",
    description=(
        "Ask to send (preview) or send the result to a teacher via email/Slack. "
        "Use confirm=false to get the confirmation prompt; set confirm=true to actually send."
    ),
)
async def notify_teacher(
    pose: str = Field(description="Pose name"),
    student_id: str = Field(description="Student identifier"),
    teacher_email: Optional[str] = Field(default=None, description="Teacher email address"),
    slack_webhook: Optional[str] = Field(default=None, description="Slack webhook URL"),
    confirm: bool = Field(default=False, description="If true, perform sending; if false, return confirmation prompt."),
) -> Dict[str, Any]:
    destinations = {"teacher_email": teacher_email, "slack_webhook": slack_webhook}
    has_destination = any(destinations.values())

    preview_text = f"Student {student_id} completed {pose} successfully."

    if not confirm:
        return {
            "action": "preview",
            "message": (
                "Do you want me to send this result to your Yoga teacher?"
                if has_destination
                else "No destination provided. Add teacher_email and/or slack_webhook to send."
            ),
            "payload": {
                "pose": pose,
                "student_id": student_id,
                "teacher_email": teacher_email,
                "slack_webhook": slack_webhook,
                "text": preview_text,
                "confirm": True,
            },
        }

    if not has_destination:
        return {"error": "No destination configured. Provide teacher_email and/or slack_webhook."}

    status: Dict[str, Any] = {"sent": {}}
    if teacher_email:
        status["sent"]["email"] = send_email(
            subject=f"{student_id} - {pose} achieved",
            body=preview_text,
            to_email=teacher_email,
        )
    if slack_webhook:
        status["sent"]["slack"] = await send_slack(slack_webhook, preview_text)

    status["ok"] = True
    return status

# 4) Next or End ---------------------------------------------------------
@mcp.tool(title="Next Or End", description="Choose next pose or end session.")
def session_next_or_end(
    choice: str = Field(default="next", description="Accepts 'next' or 'end'."),
) -> str:
    return "Okay—loading the next pose." if choice.lower().startswith("n") \
           else "Great session today. That’s it for now."

# ---------- Run (template style) ----------
if __name__ == "__main__":
    mcp.run(transport="streamable-http")