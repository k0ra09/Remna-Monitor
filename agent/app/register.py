import os
import requests

BOT_URL = os.getenv("BOT_URL")
AGENT_NAME = os.getenv("AGENT_NAME")
AGENT_TOKEN = os.getenv("AGENT_TOKEN")


def get_my_ip():
    return requests.get("https://api.ipify.org", timeout=5).text


def register():
    if not BOT_URL:
        return

    ip = get_my_ip()

    requests.post(
        f"{BOT_URL}/register",
        headers={
            "Authorization": f"Bearer {AGENT_TOKEN}"
        },
        json={
            "name": AGENT_NAME,
            "url": f"http://{ip}:8000"
        },
        timeout=5
    )
