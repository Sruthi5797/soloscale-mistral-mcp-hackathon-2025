# src/poseflow_mcp/local_http.py
from __future__ import annotations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from mcp.server.fastmcp import FastMCP
from . import adapter, mp_estimator, notifications  # use your real modules

# Reuse the MCP instance if you want, or make a new one:
mcp = FastMCP("soloscale_poseflow_local")

app = FastAPI(title="Poseflow local sanity")
app.mount("/mcp", mcp.streamable_http_app())

class ImgIn(BaseModel):
    image_url: Optional[str] = None
    image_b64: Optional[str] = None

@app.get("/")
def root():
    return {"ok": True}

# Add any quick endpoints you need…