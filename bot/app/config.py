import os

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ID Админа для уведомлений
# Преобразуем в int, так как aiogram требует int или str, но лучше int для сравнений
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID"))
except (TypeError, ValueError):
    # Если переменная не задана или не число, ставим заглушку или вызываем ошибку
    print("WARNING: ADMIN_ID not set properly in .env")
    ADMIN_ID = 0

# Токен для доступа к агентам
AGENT_TOKEN = os.getenv("AGENT_TOKEN")

# Список агентов через запятую
AGENTS = [
    a.strip()
    for a in os.getenv("AGENTS", "").split(",")
    if a.strip()
]
