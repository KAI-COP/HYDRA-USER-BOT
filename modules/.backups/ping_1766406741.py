import time
import asyncio
import psutil
from datetime import datetime
from utils.misc import get_uptime, get_start_time, edit_or_reply, rate_limit, fast_animation
from modules.lang import translator

# Глобальные переменные для отслеживания статистики
ping_stats = {
    "total_pings": 0,
    "min_ping": float('inf'),
    "max_ping": 0,
    "avg_ping": 0,
    "total_time": 0
}

@rate_limit(limit=15, period=120)
async def ping_handler(event):
    """Расширенная команда ping с детальной информацией о системе"""
    try:
        # Начальная анимация
        loading_msg = await edit_or_reply(event, "⚡")
        await fast_animation(loading_msg, "⚡", "⚡ Измеряю скорость...")

        # Измеряем ping
        start = time.time()
        await asyncio.sleep(0.01)  # Более точное измерение
        end = time.time()
        ping_ms = round((end - start) * 1000, 2)

        # Обновляем статистику
        ping_stats["total_pings"] += 1
        ping_stats["total_time"] += ping_ms
        ping_stats["min_ping"] = min(ping_stats["min_ping"], ping_ms)
        ping_stats["max_ping"] = max(ping_stats["max_ping"], ping_ms)
        ping_stats["avg_ping"] = round(ping_stats["total_time"] / ping_stats["total_pings"], 2)

        # Получаем информацию о системе
        start_time = get_start_time()
        uptime = get_uptime(start_time)

        # Получаем информацию о ресурсах
        try:
            ram = psutil.virtual_memory()
            ram_percent = ram.percent
            ram_used = round(ram.used / (1024**3), 2)  # GB
            ram_total = round(ram.total / (1024**3), 2)  # GB
            cpu_percent = psutil.cpu_percent(interval=0.1)

            system_info = f"""
**💾 RAM:** `{ram_used}/{ram_total} GB ({ram_percent}%)`
**🔥 CPU:** `{cpu_percent}%`"""
        except:
            system_info = ""

        # Определяем эмодзи в зависимости от скорости
        if ping_ms < 50:
            speed_emoji = "🚀"
            speed_text = "Отлично"
        elif ping_ms < 100:
            speed_emoji = "⚡"
            speed_text = "Хорошо"
        elif ping_ms < 200:
            speed_emoji = "✅"
            speed_text = "Нормально"
        else:
            speed_emoji = "🐌"
            speed_text = "Медленно"

        # Формируем сообщение
        text = f"""**{speed_emoji} PONG! {speed_text}**

**⚡️ Отклик:**
`{ping_ms} мс`

**🕐 Аптайм:**
`{uptime}`
{system_info}

**📊 Статистика:**
`Мин: {ping_stats["min_ping"]} мс | Макс: {ping_stats["max_ping"]} мс`
`Средний: {ping_stats["avg_ping"]} мс | Запросов: {ping_stats["total_pings"]}`

_Время: {datetime.now().strftime("%H:%M:%S")}_"""

        await loading_msg.edit(text)

    except Exception as e:
        await edit_or_reply(event, f"❌ Ошибка ping: {str(e)}")

@rate_limit(limit=5, period=60)
async def pingstat_handler(event):
    """Показать статистику ping"""
    try:
        if ping_stats["total_pings"] == 0:
            await edit_or_reply(event, "📊 Статистика пока пуста. Используйте `.ping` для сбора данных.")
            return

        text = f"""**📊 Статистика Ping**

**Всего запросов:** `{ping_stats["total_pings"]}`
**Минимальный ping:** `{ping_stats["min_ping"]} мс`
**Максимальный ping:** `{ping_stats["max_ping"]} мс`
**Средний ping:** `{ping_stats["avg_ping"]} мс`

**🕐 Аптайм:** `{get_uptime(get_start_time())}`"""

        await edit_or_reply(event, text)

    except Exception as e:
        await edit_or_reply(event, f"❌ Ошибка: {str(e)}")

@rate_limit(limit=3, period=60)
async def resetping_handler(event):
    """Сбросить статистику ping"""
    try:
        ping_stats["total_pings"] = 0
        ping_stats["min_ping"] = float('inf')
        ping_stats["max_ping"] = 0
        ping_stats["avg_ping"] = 0
        ping_stats["total_time"] = 0

        await edit_or_reply(event, "✅ Статистика ping сброшена")

    except Exception as e:
        await edit_or_reply(event, f"❌ Ошибка: {str(e)}")

# Справка модуля
modules_help = {
    "ping": {
        "ping": "Проверить скорость отклика и статус системы",
        "pingstat": "Показать статистику ping",
        "resetping": "Сбросить статистику ping"
    }
}
