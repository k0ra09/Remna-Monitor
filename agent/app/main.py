from fastapi import FastAPI, Header, HTTPException
import os

from app.metrics import collect_metrics

app = FastAPI()

AGENT_NAME = os.getenv("AGENT_NAME", "node-unknown")
AGENT_TOKEN = os.getenv("AGENT_TOKEN", "")


@app.get("/status")
async def status(authorization: str | None = Header(default=None)):
    if authorization != f"Bearer {AGENT_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    data = await collect_metrics()

    return {
        "node": AGENT_NAME,
        "status": "ok",
        **data
    }
