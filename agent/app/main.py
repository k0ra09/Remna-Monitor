import os
import time
import socket
import asyncio
from fastapi import FastAPI, Request, HTTPException

from app.register import register_loop
from app.metrics import collect_metrics

AGENT_NAME = os.getenv("AGENT_NAME", socket.gethostname())
AGENT_TOKEN = os.getenv("AGENT_TOKEN")

app = FastAPI()


# ---------- AUTH ----------
def check_auth(request: Request):
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {AGENT_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")


# ---------- STATUS ----------
@app.get("/status")
async def status(request: Request):
    check_auth(request)
    
    # Используем обновленную функцию метрик
    metrics = await collect_metrics()
    
    return {
        "node": AGENT_NAME,
        "status": "ok",
        **metrics # Распаковываем time, system, services
    }


# ---------- STARTUP ----------
@app.on_event("startup")
async def on_startup():
    # Запускаем цикл регистрации в фоне
    asyncio.create_task(register_loop())
