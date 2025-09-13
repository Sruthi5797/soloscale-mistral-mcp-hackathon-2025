from __future__ import annotations
from typing import Optional
from mcp.server.fastmcp import FastMCP
from .notifications import send_email, send_slack
from .adapter import predict_pose_using_asanaai
from .mp_estimator import predict_pose_fallback

def predict_pose(image_url: Optional[str]=None, image_b64: Optional[str]=None):
    try:
        return predict_pose_using_asanaai(image_url=image_url, image_b64=image_b64)
    except Exception:
        return predict_pose_fallback(image_url=image_url, image_b64=image_b64)

mcp = FastMCP("soloscale_poseflow")  # MCP name

STATE = {"threshold": 0.8}

@mcp.tool(title="Set Confidence Threshold", description="Set the confidence threshold for pose correctness (0.0 to 1.0).")
def set_threshold(value: float) -> dict:
    STATE["threshold"] = max(0.0, min(1.0, float(value))); return {"threshold": STATE["threshold"]}

@mcp.tool(title="Record Pose", description="Analyze the provided image and identify the yoga pose along with confidence level.")
def record_pose(image_url: Optional[str]=None, image_b64: Optional[str]=None) -> dict:
    pose, conf = predict_pose(image_url=image_url, image_b64=image_b64)
    return {"pose": pose, "confidence": round(conf, 3)}

@mcp.tool(title="Celebrate If Correct", description="Celebrate if the detected pose meets or exceeds the confidence threshold.")
def celebrate_if_correct(pose: str, confidence: float, threshold: Optional[float]=None) -> str:
    th = threshold if threshold is not None else STATE["threshold"]
    return "🎉 Bravo! Pose achieved." if confidence >= th else "Keep adjusting—you’re close!"

@mcp.tool(title="Ask to Send to Teacher", description="Ask the user if they want to send their pose result to their Yoga teacher.")
def ask_send_teacher(pose: str, student_id: str) -> str:
    return f"Do you want me to send your {pose} result for student {student_id} to your Yoga teacher?"

@mcp.tool(title="Send to Teacher", description="Send an email or Slack message to the Yoga teacher about the student's pose achievement.")
async def send_to_teacher(pose: str, student_id: str, teacher_email: Optional[str]=None, slack_webhook: Optional[str]=None) -> dict:
    text = f"Student {student_id} completed {pose} successfully. 🙌"
    status = {}
    if teacher_email: status["email"] = send_email(subject=f"{student_id} - {pose} achieved", body=text, to_email=teacher_email)
    if slack_webhook: status["slack"] = await send_slack(slack_webhook, text)
    if not status: status["info"] = "No destination configured"
    status["ok"] = True; return status

@mcp.tool(title="Session Next or End", description="Decide whether to load the next pose or end the session based on user choice.")
def session_next_or_end(choice: str="next") -> str:
    return "Okay—loading the next pose. 🧘" if choice.lower().startswith("n") else "Great session today. That’s it for now. 🌿"

def main():
    import argparse
    parser = argparse.ArgumentParser(); parser.add_argument("transport", nargs="?", default="stdio", choices=["stdio"])
    args = parser.parse_args()
    if args.transport == "stdio":
        import mcp.server.stdio
        mcp.run(mcp.server.stdio.stdio_transport())

if __name__ == "__main__": main()
