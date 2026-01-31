import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiohttp import web

from app.config import BOT_TOKEN, AGENT_TOKEN
from app.keyboards import main_menu, back_menu
from app.agents import fetch_all_agents
from app.registry import register_agent

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ---------- TELEGRAM ----------
@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "🧠 Remna Monitor\n\nВыбери действие:",
        reply_markup=main_menu()
    )


@dp.callback_query(F.data == "nodes")
async def nodes(callback: CallbackQuery):
    agents = await fetch_all_agents()

    lines = ["🖥 *Серверы*\n"]
    for a in agents:
        sys = a.get("system", {})
        lines.append(
            f"*{a.get('node')}*\n"
            f"CPU: {sys.get('cpu_percent', '?')}%\n"
            f"RAM: {sys.get('ram_percent', '?')}%\n"
            f"Disk: {sys.get('disk_percent', '?')}%\n"
        )

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=back_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.message.edit_text(
        "🧠 Remna Monitor\n\nВыбери действие:",
        reply_markup=main_menu()
    )
    await callback.answer()


# ---------- HTTP REGISTRATION ----------
async def register_handler(request):
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {AGENT_TOKEN}":
        return web.Response(status=401)

    data = await request.json()

    register_agent({
        "name": data["name"],
        "url": data["url"]
    })

    return web.json_response({"status": "ok"})


async def start_http():
    app = web.Application()
    app.router.add_post("/register", register_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 9000)
    await site.start()


async def main():
    asyncio.create_task(start_http())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
