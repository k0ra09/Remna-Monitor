import asyncio
import logging
import time
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

# Словарь для хранения последних ошибок по каждому серверу
# Format: {"NodeName": ["Error 1", "Error 2"]}
node_states = {}


# ---------- HELPER ----------
def is_admin(user_id: int) -> bool:
    if ADMIN_ID == 0:
        return True
    return user_id == ADMIN_ID


# ---------- MONITORING TASK ----------

async def monitor_task(bot: Bot):
    """Фоновая задача: проверяет серверы раз в минуту"""
    logging.info("🕵️‍♂️ Умный мониторинг запущен")
    
    while True:
        await asyncio.sleep(60) 
        
        try:
            agents_data = await fetch_all_agents()
            
            # Проходимся по каждому агенту
            for data in agents_data:
                node_name = data['node']
                current_problems = []

                # 1. Если агент недоступен (Status Error)
                if data.get("status") == "error":
                    current_problems.append(f"🚨 <b>Связь потеряна!</b> ({data.get('error')})")
                else:
                    # 2. Проверка ресурсов
                    sys = data.get("system", {})
                    cpu = sys.get("cpu_percent", 0)
                    ram = sys.get("ram_percent", 0)
                    disk = sys.get("disk_percent", 0)
                    
                    if cpu > 85: current_problems.append(f"🔥 Высокая нагрузка CPU: {cpu}%")
                    if ram > 85: current_problems.append(f"🧠 Мало памяти RAM: {ram}%")
                    if disk > 90: current_problems.append(f"💾 Заканчивается диск: {disk}%")
                    
                    # 3. Проверка сервисов
                    services = data.get("services", {})
                    for svc_name, svc_data in services.items():
                        if svc_data.get("status") != "ok":
                            current_problems.append(f"💀 Сервис <b>{svc_name}</b> упал!")

                # --- ЛОГИКА ANTI-SPAM ---
                
                # Получаем прошлые проблемы этого сервера
                last_problems = node_states.get(node_name, [])
                
                # Сортируем, чтобы порядок не влиял на сравнение
                current_problems.sort()
                last_problems.sort()

                # Если список проблем изменился (что-то новое или что-то починилось)
                if current_problems != last_problems:
                    
                    # Если проблем стало больше 0 - шлем алерт
                    if current_problems:
                        if ADMIN_ID:
                            msg = f"⚠️ <b>Проблемы на {node_name}</b>\n\n" + "\n".join(current_problems)
                            try:
                                await bot.send_message(ADMIN_ID, msg, parse_mode="HTML")
                            except Exception as e:
                                logging.error(f"Error sending alert: {e}")
                    
                    # Если проблем стало 0, а раньше были - значит ПОЧИНИЛОСЬ!
                    elif last_problems and not current_problems:
                        if ADMIN_ID:
                            try:
                                await bot.send_message(ADMIN_ID, f"✅ <b>{node_name}</b> полностью восстановился!", parse_mode="HTML")
                            except Exception as e:
                                logging.error(f"Error sending recovery: {e}")

                    # Запоминаем текущее состояние
                    node_states[node_name] = current_problems

        except Exception as e:
            logging.error(f"Ошибка в цикле мониторинга: {e}")


# ---------- TELEGRAM HANDLERS ----------

@dp.message(F.text == "/start")
async def start(message: Message):
    if not is_admin(message.from_user.id):
        return 

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
        net = sys.get("network", {})
        
        text.append(
            f"✅ <b>{a['node']}</b>\n"
            f"├ 🚀 <b>Net:</b> ↓{net.get('rx_mbit', 0)} Mbit  ↑{net.get('tx_mbit', 0)} Mbit\n"
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
    asyncio.create_task(monitor_task(bot))


def create_app():
    app = web.Application()
    app.router.add_post("/register", register_handler)
    app.on_startup.append(start_bot)
    return app


if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=9000)
