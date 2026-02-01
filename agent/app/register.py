import os
import aiohttp
import asyncio

BOT_URL = os.getenv("BOT_URL")        # http://BOT_IP:9000
AGENT_NAME = os.getenv("AGENT_NAME")
AGENT_PORT = os.getenv("AGENT_PORT", "8000")
AGENT_TOKEN = os.getenv("AGENT_TOKEN")


async def register():
    payload = {
        "name": AGENT_NAME,
        "url": f"http://{get_ip()}:{AGENT_PORT}",
    }

    headers = {
        "Authorization": f"Bearer {AGENT_TOKEN}"
    }

    async with aiohttp.ClientSession() as session:
        try:
            await session.post(
                f"{BOT_URL}/register",
                json=payload,
                headers=headers,
                timeout=5
            )
        except Exception:
            pass


def get_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


if __name__ == "__main__":
    asyncio.run(register())
