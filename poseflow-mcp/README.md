# Poseflow MCP Starter

A **from-scratch** starter to build an MCP server for Yoga coaching using the AsanaAi repo (or a fallback MediaPipe heuristic).

Flow:
1) **Record the pose** (detect name + confidence)
2) If threshold passed → **Bravo!**
3) Ask to **send to teacher**
4) **Send** (email/Slack), then **Next pose or Finish**

---

## MCP Server Name

`soloscale_poseflow`

---

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Run as stdio MCP
```bash
python -m poseflow_mcp.server stdio
```

### Run as HTTP MCP (for Alpic / Le Chat)
```bash
uvicorn poseflow_mcp.server_http:app --host 0.0.0.0 --port 8765
# MCP endpoint: http://localhost:8765/mcp
```

### Wire in AsanaAi
Clone AsanaAi **next to** this project (sibling folder) or install it as editable:
```bash
git clone https://github.com/Turwash/AsanaAi.git ../AsanaAi
# or
pip install -e ../AsanaAi
```
Then edit `src/poseflow_mcp/adapter.py` → implement `predict_pose_using_asanaai(...)` by importing the real predictor from the AsanaAi repo.

---

## Tools exposed (MCP)
- `record_pose(image_url|image_b64)` → `{pose, confidence}`
- `celebrate_if_correct(pose, confidence, threshold=0.8)` → message
- `ask_send_teacher(pose, student_id)` → message
- `send_to_teacher(pose, student_id, teacher_email?, slack_webhook?)` → status
- `session_next_or_end(choice="next")` → message
