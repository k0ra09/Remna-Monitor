import os
import socket
import asyncio
from fastapi import FastAPI, Request, HTTPException

from app.register import register_loop
from app.metrics import collect_metrics

AGENT_NAME = os.getenv("AGENT_NAME", socket.gethostname())
AGENT_TOKEN = os.getenv("AGENT_TOKEN")

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    asyncio.create_task(register_loop())


def check_auth(request: Request):
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {AGENT_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/status")
async def status(request: Request):
    check_auth(request)
    
    metrics = await collect_metrics()
    
    return {
        "node": AGENT_NAME,
        "status": "ok",
        **metrics
    }
