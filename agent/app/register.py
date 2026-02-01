import os
import aiohttp
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

BOT_URL = os.getenv("BOT_URL")
AGENT_NAME = os.getenv("AGENT_NAME")
AGENT_PORT = os.getenv("AGENT_PORT", "8000")
AGENT_TOKEN = os.getenv("AGENT_TOKEN")


def get_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


async def register_loop():
    payload = {
        "name": AGENT_NAME,
        "url": f"http://{get_ip()}:{AGENT_PORT}",
    }

    headers = {
        "Authorization": f"Bearer {AGENT_TOKEN}"
    }

    logging.info(f"🚀 Запуск агента {AGENT_NAME}. Бот: {BOT_URL}")

    while True:
        try:
            if not BOT_URL:
                logging.error("BOT_URL не задан!")
                await asyncio.sleep(10)
                continue

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{BOT_URL}/register",
                    json=payload,
                    headers=headers,
                    timeout=5
                ) as resp:
                    if resp.status == 200:
                        logging.info(f"✅ Успешный пинг бота")
                    else:
                        logging.warning(f"⚠️ Бот ответил кодом: {resp.status}")
        except Exception as e:
            logging.error(f"❌ Ошибка подключения к боту: {e}")
        
        await asyncio.sleep(60)
