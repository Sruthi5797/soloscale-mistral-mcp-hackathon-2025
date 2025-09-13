from __future__ import annotations
from typing import Optional
from mcp.server.fastmcp import FastMCP
from .notifications import send_email, send_slack
from .adapter import predict_pose_using_asanaai
from .mp_estimator import predict_pose_fallback

def predict_pose(image_url: Optional[str]=None, image_b64: Optional[str]=None):
    # Try AsanaAi first; fallback to MediaPipe heuristics
    try:
        return predict_pose_using_asanaai(image_url=image_url, image_b64=image_b64)
    except Exception:
        return predict_pose_fallback(image_url=image_url, image_b64=image_b64)

# MCP server name for the hackathon
mcp = FastMCP("soloscale_poseflow", port=3000, stateless_http=True, debug=True)

STATE = {"threshold": 0.8}

@mcp.tool(description="Set the confidence threshold (0.0-1.0) for pose correctness celebration")
def set_threshold(value: float) -> dict:
    STATE["threshold"] = max(0.0, min(1.0, float(value)))
    return {"threshold": STATE["threshold"]}

@mcp.tool(title="Record a yoga pose from an image URL or base64-encoded image", description="Returns the predicted pose and confidence score")
def record_pose(image_url: Optional[str]=None, image_b64: Optional[str]=None) -> dict:
    pose, conf = predict_pose(image_url=image_url, image_b64=image_b64)
    return {"pose": pose, "confidence": round(conf, 3)}

@mcp.tool(title="Celebrate if the pose is correct", description="Returns a celebration message if confidence meets/exceeds threshold")
def celebrate_if_correct(pose: str, confidence: float, threshold: Optional[float]=None) -> str:
    th = threshold if threshold is not None else STATE["threshold"]
    return "🎉 Bravo! Pose achieved." if confidence >= th else "Keep adjusting—you’re close!"

@mcp.tool(title="Ask if the user wants to send their result to their Yoga teacher", description="Returns a prompt message")
def ask_send_teacher(pose: str, student_id: str) -> str:
    return f"Do you want me to send your {pose} result for student {student_id} to your Yoga teacher?"

@mcp.tool(title="Send the pose achievement notification to the Yoga teacher via email and/or Slack", description="Returns status of the notifications sent")
async def send_to_teacher(
    pose: str,
    student_id: str,
    teacher_email: Optional[str]=None,
    slack_webhook: Optional[str]=None
) -> dict:
    text = f"Student {student_id} completed {pose} successfully. 🙌"
    status: dict = {}
    if teacher_email:
        status["email"] = send_email(subject=f"{student_id} - {pose} achieved", body=text, to_email=teacher_email)
    if slack_webhook:
        status["slack"] = await send_slack(slack_webhook, text)
    if not status:
        status["info"] = "No destination configured"
    status["ok"] = True
    return status

@mcp.tool(title="Load the next pose or end the session", description="Returns a message indicating the next action")
def session_next_or_end(choice: str="next") -> str:
    return "Okay—loading the next pose. 🧘" if choice.lower().startswith("n") \
           else "Great session today. That’s it for now. 🌿"