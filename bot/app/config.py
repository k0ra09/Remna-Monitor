\import os

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ID Админа для уведомлений
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
except (TypeError, ValueError):
    ADMIN_ID = 0

# Токен для доступа к агентам
AGENT_TOKEN = os.getenv("AGENT_TOKEN")

# Список агентов
AGENTS = [
    a.strip()
    for a in os.getenv("AGENTS", "").split(",")
    if a.strip()
]
