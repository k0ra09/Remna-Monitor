import os
import time
import httpx

REMNAWAVE_API = os.getenv("REMNAWAVE_API")
REMNANODE_API = os.getenv("REMNANODE_API")


async def fetch_api(url: str | None):
    if not url:
        return {
            "enabled": False,
            "status": "disabled"
        }

    try:
        async with httpx.AsyncClient(timeout=2) as client:
            resp = await client.get(url)
            resp.raise_for_status()

            return {
                "enabled": True,
                "status": "ok",
                "data": resp.json()
            }

    except Exception as e:
        return {
            "enabled": True,
            "status": "error",
            "error": str(e)
        }


async def collect_metrics():
    return {
        "time": int(time.time()),
        "remnawave": await fetch_api(REMNAWAVE_API),
        "remnanode": await fetch_api(REMNANODE_API)
    }
