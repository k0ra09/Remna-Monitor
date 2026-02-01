import time
import psutil
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Создаем пул потоков для тяжелых задач
executor = ThreadPoolExecutor()

async def system_metrics():
    # Запускаем блокирующую функцию cpu_percent в отдельном потоке
    loop = asyncio.get_running_loop()
    cpu = await loop.run_in_executor(executor, psutil.cpu_percent, 0.5)

    return {
        "cpu_percent": cpu,
        "ram_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage("/").percent,
        "uptime_sec": int(time.time() - psutil.boot_time()),
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
        "system": await system_metrics(), # Теперь это await
        "services": await service_checks()
    }
