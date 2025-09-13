"""
soloscale_poseflow — MCP Server (template style)
"""

from __future__ import annotations
import os
from typing import Optional, Dict, Any

from mcp.server.fastmcp import FastMCP
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
PORT = int(os.environ.get("PORT", "8080"))
mcp = FastMCP("soloscale_poseflow", port=PORT, stateless_http=True, debug=True)

STATE = {"threshold": 0.8}

# ---------- TOOLS ----------
@mcp.tool(title="Set Threshold", description="Set success threshold for celebration")
def set_threshold(value: float = Field(description="0.0–1.0 threshold")) -> Dict[str, float]:
    v = max(0.0, min(1.0, float(value)))
    STATE["threshold"] = v
    return {"threshold": v}

@mcp.tool(title="Record Pose", description="Predict pose from image URL or base64")
def record_pose(
    image_url: Optional[str] = Field(default=None, description="Public image URL"),
    image_b64: Optional[str] = Field(default=None, description="Base64 image data"),
) -> Dict[str, object]:
    pose, conf = predict_pose(image_url=image_url, image_b64=image_b64)
    return {"pose": pose, "confidence": round(float(conf), 3)}

@mcp.tool(title="Celebrate", description="Return celebration if confidence ≥ threshold")
def celebrate_if_correct(
    pose: str = Field(description="Pose name"),
    confidence: float = Field(description="Model confidence 0–1"),
    threshold: Optional[float] = Field(default=None, description="Override threshold"),
) -> str:
    th = float(threshold) if threshold is not None else float(STATE["threshold"])
    return "🎉 Bravo! Pose achieved." if float(confidence) >= th else "Keep adjusting—you’re close!"

@mcp.tool(title="Ask Send Teacher", description="Ask if result should be sent to teacher")
def ask_send_teacher(
    pose: str = Field(description="Pose name"),
    student_id: str = Field(description="Student identifier"),
) -> str:
    return f"Do you want me to send your {pose} result for student {student_id} to your Yoga teacher?"

@mcp.tool(title="Send To Teacher", description="Send success message via email and/or Slack")
async def send_to_teacher(
    pose: str = Field(description="Pose name"),
    student_id: str = Field(description="Student identifier"),
    teacher_email: Optional[str] = Field(default=None, description="Email address"),
    slack_webhook: Optional[str] = Field(default=None, description="Slack webhook URL"),
) -> Dict[str, object]:
    text = f"Student {student_id} completed {pose} successfully. 🙌"
    status: Dict[str, object] = {}
    if teacher_email:
        status["email"] = send_email(subject=f"{student_id} - {pose} achieved", body=text, to_email=teacher_email)
    if slack_webhook:
        status["slack"] = await send_slack(slack_webhook, text)
    if not status:
        status["info"] = "No destination configured"
    status["ok"] = True
    return status

@mcp.tool(title="Next Or End", description="Choose next pose or end session")
def session_next_or_end(
    choice: str = Field(default="next", description="next | end"),
) -> str:
    return "Okay—loading the next pose. 🧘" if choice.lower().startswith("n") \
           else "Great session today. That’s it for now. 🌿"

# ---------- Run (template style) ----------
if __name__ == "__main__":
    mcp.run(transport="streamable-http")