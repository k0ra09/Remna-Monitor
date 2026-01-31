import os

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Токен для доступа к агентам
AGENT_TOKEN = os.getenv("AGENT_TOKEN")

# Список агентов через запятую
# пример: http://10.0.0.1:8000,http://10.0.0.2:8000
AGENTS = [
    a.strip()
    for a in os.getenv("AGENTS", "").split(",")
    if a.strip()
]
