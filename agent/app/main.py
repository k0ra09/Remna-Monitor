import os
import time
import socket
import psutil
from fastapi import FastAPI, Request, HTTPException

import asyncio
from app.register import register

asyncio.create_task(register())
AGENT_NAME = os.getenv("AGENT_NAME", socket.gethostname())
AGENT_TOKEN = os.getenv("AGENT_TOKEN")

app = FastAPI()


# ---------- AUTH ----------
def check_auth(request: Request):
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {AGENT_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")


# ---------- SYSTEM METRICS ----------
def get_system_metrics():
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "ram_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "uptime_sec": int(time.time() - psutil.boot_time()),
    }


# ---------- STATUS ----------
@app.get("/status")
def status(request: Request):
    check_auth(request)

    return {
        "node": AGENT_NAME,
        "status": "ok",
        "time": int(time.time()),
        "system": get_system_metrics()
    }


# ---------- STARTUP ----------
@app.on_event("startup")
def on_startup():
    # автрегистр при старте агента
    register()
