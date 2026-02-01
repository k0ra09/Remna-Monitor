import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery

from app.registry import register_agent, load_agents
from app.keyboards import main_menu, back_menu
from app.config import BOT_TOKEN, AGENT_TOKEN

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
    agents = load_agents()

    if not agents:
        await callback.message.edit_text("Нет серверов")
        await callback.answer()
        return

    text = ["🖥 Серверы\n"]
    for a in agents:
        sys = a.get("system", {})
        text.append(
            f"{a['name']}\n"
            f"CPU: {sys.get('cpu_percent','?')}%\n"
            f"RAM: {sys.get('ram_percent','?')}%\n"
            f"Disk: {sys.get('disk_percent','?')}%\n"
        )

    await callback.message.edit_text(
        "\n".join(text),
        reply_markup=back_menu()
    )
    await callback.answer()


@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    await callback.message.edit_text(
        "🧠 Remna Monitor\n\nВыбери действие:",
        reply_markup=main_menu()
    )
    await callback.answer()


# ---------- HTTP ----------

async def register_handler(request):
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {AGENT_TOKEN}":
        return web.json_response({"error": "unauthorized"}, status=401)

    data = await request.json()
    register_agent(data)
    return web.json_response({"status": "ok"})


async def start_bot(app: web.Application):
    asyncio.create_task(dp.start_polling(bot))


def create_app():
    app = web.Application()
    app.router.add_post("/register", register_handler)
    app.on_startup.append(start_bot)
    return app


if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=9000)
