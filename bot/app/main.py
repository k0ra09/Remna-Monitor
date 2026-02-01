import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery

from app.registry import register_agent
from app.keyboards import main_menu, back_menu
from app.config import BOT_TOKEN, AGENT_TOKEN, ADMIN_ID
from app.agents import fetch_all_agents

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)


# ---------- HELPER ----------
def is_admin(user_id: int) -> bool:
    # Если ADMIN_ID не задан (0), пускаем всех (режим отладки)
    # Если задан, пускаем только админа
    if ADMIN_ID == 0:
        return True
    return user_id == ADMIN_ID


# ---------- MONITORING TASK ----------

async def monitor_task(bot: Bot):
    """Фоновая задача: проверяет серверы раз в минуту"""
    logging.info("🕵️‍♂️ Мониторинг запущен")
    while True:
        await asyncio.sleep(60) # Проверка раз в минуту
        
        try:
            agents_data = await fetch_all_agents()
            for data in agents_data:
                # 1. Если агент недоступен
                if data.get("status") == "error":
                    if ADMIN_ID:
                        await bot.send_message(
                            ADMIN_ID, 
                            f"🚨 <b>ВНИМАНИЕ!</b>\n\nАгент <b>{data['node']}</b> недоступен!\nОшибка: {data.get('error')}",
                            parse_mode="HTML"
                        )
                    continue
                
                # 2. Проверка ресурсов
                sys = data.get("system", {})
                cpu = sys.get("cpu_percent", 0)
                ram = sys.get("ram_percent", 0)
                disk = sys.get("disk_percent", 0)
                
                alerts = []
                if cpu > 85: alerts.append(f"🔥 CPU: {cpu}%")
                if ram > 85: alerts.append(f"🧠 RAM: {ram}%")
                if disk > 90: alerts.append(f"💾 DISK: {disk}%")
                
                # 3. Проверка сервисов
                services = data.get("services", {})
                for svc_name, svc_data in services.items():
                    if svc_data.get("status") != "ok":
                        alerts.append(f"💀 Сервис <b>{svc_name}</b> упал!")

                # Если есть проблемы — шлем сообщение
                if alerts and ADMIN_ID:
                    msg = f"⚠️ <b>Проблемы на {data['node']}</b>\n\n" + "\n".join(alerts)
                    try:
                        await bot.send_message(ADMIN_ID, msg, parse_mode="HTML")
                    except Exception as e:
                        logging.error(f"Не удалось отправить алерт: {e}")

        except Exception as e:
            logging.error(f"Ошибка в цикле мониторинга: {e}")


# ---------- TELEGRAM HANDLERS ----------

@dp.message(F.text == "/start")
async def start(message: Message):
    if not is_admin(message.from_user.id):
        return  # Игнорируем чужаков

    await message.answer(
        "🧠 Remna Monitor\n\nВыбери действие:",
        reply_markup=main_menu()
    )


@dp.callback_query(F.data == "status")
async def status(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    agents_data = await fetch_all_agents()
    
    if not agents_data:
        await callback.message.edit_text("Нет данных о серверах", reply_markup=back_menu())
        return

    total = len(agents_data)
    online = sum(1 for a in agents_data if a.get("status") != "error")
    offline = total - online
    
    text = (
        f"📊 <b>Состояние системы</b>\n\n"
        f"🖥 Всего серверов: <b>{total}</b>\n"
        f"✅ Онлайн: <b>{online}</b>\n"
        f"❌ Офлайн: <b>{offline}</b>"
    )
    
    await callback.message.edit_text(text, reply_markup=back_menu(), parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data == "nodes")
async def nodes(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    agents_data = await fetch_all_agents()

    if not agents_data:
        await callback.message.edit_text("Нет доступных серверов", reply_markup=back_menu())
        return

    text = ["🖥 <b>Детальная статистика</b>\n"]
    for a in agents_data:
        if a.get("status") == "error":
            text.append(f"❌ <b>{a['node']}</b>: ОШИБКА ({a.get('error')})")
            continue

        sys = a.get("system", {})
        text.append(
            f"✅ <b>{a['node']}</b>\n"
            f"├ CPU: {sys.get('cpu_percent','?')}%\n"
            f"├ RAM: {sys.get('ram_percent','?')}%\n"
            f"└ Disk: {sys.get('disk_percent','?')}%"
        )

    await callback.message.edit_text("\n\n".join(text), reply_markup=back_menu(), parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data == "limits")
async def limits(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    text = (
        "⚙️ <b>Текущие лимиты уведомлений:</b>\n\n"
        "🔥 CPU > 85%\n"
        "🧠 RAM > 85%\n"
        "💾 Disk > 90%\n"
        "💀 Падение сервисов"
    )
    await callback.message.edit_text(text, reply_markup=back_menu(), parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data == "back")
async def back(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return

    await callback.message.edit_text(
        "🧠 Remna Monitor\n\nВыбери действие
