import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery

from app.config import BOT_TOKEN
from app.keyboards import main_menu, back_menu
from app.agents import fetch_all_agents

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "🧠 Remna Monitor\n\nВыбери действие:",
        reply_markup=main_menu()
    )


@dp.callback_query(F.data == "status")
async def status(callback: CallbackQuery):
    agents = await fetch_all_agents()

    lines = ["📊 *Общий статус*\n"]
    for a in agents:
        emoji = "🟢" if a.get("status") == "ok" else "🔴"
        name = a.get("node", "unknown")
        lines.append(f"{emoji} {name}")

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=back_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()


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


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
