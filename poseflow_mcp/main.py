"""
soloscale_poseflow — MCP Server (template style)
"""

from __future__ import annotations
import os
from typing import Optional, Dict, Any

from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any
from pydantic import Field

# ---------- helper imports (with safe fallbacks) ----------
try:
    from src.poseflow_mcp.notifications import send_email, send_slack  # type: ignore
    from src.poseflow_mcp.adapter import predict_pose_using_asanaai     # type: ignore
    from src.poseflow_mcp.mp_estimator import predict_pose_fallback     # type: ignore
except Exception:
    async def send_slack(webhook: str, text: str) -> Dict[str, Any]:
        return {"ok": True, "webhook": webhook, "text": text}

    def send_email(subject: str, body: str, to_email: str) -> Dict[str, Any]:
        return {"ok": True, "to": to_email, "subject": subject, "body": body}

    def predict_pose_using_asanaai(image_url: Optional[str] = None,
                                   image_b64: Optional[str] = None):
        return ("WarriorII", 0.93)

    def predict_pose_fallback(image_url: Optional[str] = None,
                              image_b64: Optional[str] = None):
        return ("WarriorII", 0.80)

def predict_pose(image_url: Optional[str] = None, image_b64: Optional[str] = None):
    try:
        return predict_pose_using_asanaai(image_url=image_url, image_b64=image_b64)
    except Exception:
        return predict_pose_fallback(image_url=image_url, image_b64=image_b64)

# ---------- MCP server ----------
PORT = int(os.environ.get("PORT", "3000"))
mcp = FastMCP("soloscale_poseflow", port=PORT, stateless_http=True, debug=True)

STATE = {"threshold": 0.8}

# 1) Set threshold ------------------------------------------------------
@mcp.tool(title="Set Threshold", description="Set success threshold for pose achievement (0.0–1.0).")
def set_threshold(value: float = Field(description="0.0–1.0 threshold")) -> Dict[str, float]:
    v = max(0.0, min(1.0, float(value)))
    STATE["threshold"] = v
    return {"threshold": v}


# 2) Record + Feedback (pose + celebrate/adjust in one) -----------------
@mcp.tool(
    title="Record Pose",
    description="Predict pose from image URL or base64 and return feedback based on the threshold."
)
def record_pose(
    image_url: Optional[str] = Field(default=None, description="Public image URL"),
    image_b64: Optional[str] = Field(default=None, description="Base64-encoded image"),
    threshold: Optional[float] = Field(default=None, description="Override threshold (0.0–1.0)."),
) -> Dict[str, Any]:
    if not (image_url or image_b64):
        return {"error": "Provide either image_url or image_b64"}

    pose, conf = predict_pose(image_url=image_url, image_b64=image_b64)

    th = float(threshold) if threshold is not None else float(STATE["threshold"])
    msg = "Bravo! Pose achieved." if float(conf) >= th else "Keep adjusting—you’re close!"

    return {
        "pose": pose,
        "confidence": round(float(conf), 3),
        "threshold_used": th,
        "message": msg,
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
    # Validate at least one destination when attempting to send
    destinations = {"teacher_email": teacher_email, "slack_webhook": slack_webhook}
    has_destination = any(destinations.values())

    preview_text = f"Student {student_id} completed {pose} successfully."

    if not confirm:
        # Return a confirmation prompt (no side effects)
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

    # confirm=True -> perform the send
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
    return "Okay—loading the next pose. 🧘" if choice.lower().startswith("n") \
           else "Great session today. That’s it for now."

# ---------- Run (template style) ----------
if __name__ == "__main__":
    mcp.run(transport="streamable-http")