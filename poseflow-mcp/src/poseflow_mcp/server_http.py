from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from .server import mcp, record_pose, celebrate_if_correct, send_to_teacher, session_next_or_end, ask_send_teacher

app = FastAPI(title="Poseflow MCP (HTTP)")
app.mount("/mcp", mcp.streamable_http_app())

@app.get("/")
def root():
    return {"name": "soloscale_poseflow", "status": "ok", "mcp": "/mcp"}

# --- REST helpers (handy for quick local/Alpic sanity checks) ---

class ImgIn(BaseModel):
    image_url: Optional[str] = None
    image_b64: Optional[str] = None

class CelebrateIn(BaseModel):
    pose: str
    confidence: float
    threshold: Optional[float] = None

class SendIn(BaseModel):
    pose: str
    student_id: str
    teacher_email: Optional[str] = None
    slack_webhook: Optional[str] = None

class NextIn(BaseModel):
    choice: str = "next"

@app.post("/record")
def rec(inp: ImgIn):
    if not (inp.image_url or inp.image_b64):
        raise HTTPException(400, "Provide image_url or image_b64")
    return record_pose(image_url=inp.image_url, image_b64=inp.image_b64)

@app.post("/celebrate")
def cel(inp: CelebrateIn):
    return {"message": celebrate_if_correct(inp.pose, inp.confidence, inp.threshold)}

@app.get("/ask")
def ask(pose: str, student_id: str):
    return {"message": ask_send_teacher(pose, student_id)}

@app.post("/send")
async def send(inp: SendIn):
    return await send_to_teacher(inp.pose, inp.student_id, inp.teacher_email, inp.slack_webhook)

@app.post("/next")
def nxt(inp: NextIn):
    return {"message": session_next_or_end(inp.choice)}