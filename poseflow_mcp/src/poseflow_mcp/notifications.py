from __future__ import annotations
import os, smtplib, ssl, httpx
from email.mime.text import MIMEText

def send_email(subject: str, body: str, to_email: str) -> str:
    host = os.getenv("SMTP_HOST"); port = int(os.getenv("SMTP_PORT","587"))
    user = os.getenv("SMTP_USER"); pwd = os.getenv("SMTP_PASS")
    from_email = os.getenv("FROM_EMAIL","no-reply@yoga-mcp.app")
    if not (host and user and pwd and to_email):
        return "Email not configured"
    msg = MIMEText(body, "plain", "utf-8"); msg["Subject"] = subject; msg["From"] = from_email; msg["To"] = to_email
    ctx = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.starttls(context=ctx); server.login(user, pwd); server.sendmail(from_email, [to_email], msg.as_string())
    return "Email sent"

async def send_slack(webhook: str, text: str) -> str:
    if not webhook: return "Slack not configured"
    async with httpx.AsyncClient(timeout=15) as cx:
        r = await cx.post(webhook, json={"text": text}); r.raise_for_status()
    return "Slack sent"
