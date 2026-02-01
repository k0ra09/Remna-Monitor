import time
import psutil
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

async def system_metrics():
    loop = asyncio.get_running_loop()
    
    # 1. Запоминаем счетчики сети (Start)
    net_start = psutil.net_io_counters()
    t1 = time.time()

    # 2. Ждем 1 секунду для замера CPU (в отдельном потоке, не блокируя агента)
    # Увеличили интервал до 1.0 для точности замера скорости
    cpu = await loop.run_in_executor(executor, psutil.cpu_percent, 1.0)

    # 3. Снимаем счетчики сети снова (End)
    net_end = psutil.net_io_counters()
    t2 = time.time()

    # 4. Считаем разницу и переводим в Мбит/с (Megabits per second)
    # (bytes * 8) / 1,000,000 / seconds
    dt = t2 - t1 if (t2 - t1) > 0 else 1.0
    
    rx_mbit = ((net_end.bytes_recv - net_start.bytes_recv) * 8) / 1_000_000 / dt
    tx_mbit = ((net_end.bytes_sent - net_start.bytes_sent) * 8) / 1_000_000 / dt

    return {
        "cpu_percent": cpu,
        "ram_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "uptime_sec": int(time.time() - psutil.boot_time()),
        "network": {
            "rx_mbit": round(rx_mbit, 2), # Входящая (Download)
            "tx_mbit": round(tx_mbit, 2)  # Исходящая (Upload)
        }
    }


async def check_tcp(host: str, port: int, timeout: float = 1.5):
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout
        )
        writer.close()
        await writer.wait_closed()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def service_checks():
    return {
        "remnanode": {
            "port": 61002,
            **await check_tcp("127.0.0.1", 61002)
        },
        "internal_rest": {
            "port": 61001,
            **await check_tcp("127.0.0.1", 61001)
        },
        "core": {
            "port": 61000,
            **await check_tcp("127.0.0.1", 61000)
        }
    }


async def collect_metrics():
    return {
        "time": int(time.time()),
        "system": await system_metrics(),
        "services": await service_checks()
    }
