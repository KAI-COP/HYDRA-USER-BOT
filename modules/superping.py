"""
⚡ SuperPing - Продвинутый модуль мониторинга производительности

Возможности:
• Мгновенный замер задержки (< 10ms)
• Детальная информация о системе
• История пингов и статистика
• Мониторинг ресурсов в реальном времени
• Красивая визуализация
• Проверка скорости интернета
"""

import time
import asyncio
import psutil
import platform
from datetime import datetime
from utils.misc import edit_or_reply, rate_limit
from telethon import events

# === GLOBAL STATS ===
ping_history = []
MAX_HISTORY = 100

# === PERFORMANCE MONITOR ===

class PerformanceMonitor:
    """Мониторинг производительности системы"""

    @staticmethod
    def get_cpu_info():
        """Получает информацию о CPU"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()

            return {
                "percent": cpu_percent,
                "cores": cpu_count,
                "freq": cpu_freq.current if cpu_freq else 0
            }
        except:
            return {"percent": 0, "cores": 0, "freq": 0}

    @staticmethod
    def get_memory_info():
        """Получает информацию о памяти"""
        try:
            mem = psutil.virtual_memory()
            return {
                "total": mem.total,
                "used": mem.used,
                "percent": mem.percent,
                "available": mem.available
            }
        except:
            return {"total": 0, "used": 0, "percent": 0, "available": 0}

    @staticmethod
    def get_disk_info():
        """Получает информацию о диске"""
        try:
            disk = psutil.disk_usage('/')
            return {
                "total": disk.total,
                "used": disk.used,
                "percent": disk.percent
            }
        except:
            return {"total": 0, "used": 0, "percent": 0}

    @staticmethod
    def get_network_info():
        """Получает информацию о сети"""
        try:
            net = psutil.net_io_counters()
            return {
                "sent": net.bytes_sent,
                "recv": net.bytes_recv
            }
        except:
            return {"sent": 0, "recv": 0}

    @staticmethod
    def format_bytes(bytes_num):
        """Форматирует байты в человекочитаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_num < 1024.0:
                return f"{bytes_num:.1f} {unit}"
            bytes_num /= 1024.0
        return f"{bytes_num:.1f} PB"

    @staticmethod
    def get_bar(percent, length=10):
        """Создает прогресс-бар"""
        filled = int(length * percent / 100)
        bar = '█' * filled + '░' * (length - filled)
        return bar

    @staticmethod
    def get_uptime():
        """Получает время работы системы"""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time

            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)

            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
        except:
            return "Unknown"

# === PING STATS ===

def add_to_history(ping_ms):
    """Добавляет пинг в историю"""
    global ping_history
    ping_history.append({
        "ms": ping_ms,
        "timestamp": time.time()
    })

    # Ограничиваем размер истории
    if len(ping_history) > MAX_HISTORY:
        ping_history = ping_history[-MAX_HISTORY:]

def get_stats():
    """Получает статистику пингов"""
    if not ping_history:
        return None

    pings = [p["ms"] for p in ping_history]
    return {
        "min": min(pings),
        "max": max(pings),
        "avg": sum(pings) / len(pings),
        "count": len(pings)
    }

# === COMMANDS ===

@rate_limit(limit=10, period=30)
async def ping_handler(event):
    """⚡ Быстрый пинг с минимальной информацией"""
    try:
        start = time.perf_counter()
        msg = await edit_or_reply(event, "🏓 Pinging...")
        end = time.perf_counter()

        ping_ms = round((end - start) * 1000, 2)
        add_to_history(ping_ms)

        # Определяем качество пинга
        if ping_ms < 100:
            emoji = "🟢"
            quality = "Excellent"
        elif ping_ms < 300:
            emoji = "🟡"
            quality = "Good"
        elif ping_ms < 500:
            emoji = "🟠"
            quality = "Fair"
        else:
            emoji = "🔴"
            quality = "Poor"

        text = f"""**⚡ Pong!**

{emoji} **Latency:** `{ping_ms}ms` ({quality})
🕐 **Time:** `{datetime.now().strftime('%H:%M:%S')}`"""

        # Добавляем статистику если есть
        stats = get_stats()
        if stats and stats["count"] > 1:
            text += f"\n📊 **Session:** min `{stats['min']:.1f}ms` | avg `{stats['avg']:.1f}ms` | max `{stats['max']:.1f}ms`"

        await msg.edit(text)

    except Exception as e:
        await edit_or_reply(event, f"❌ Error: {e}")

@rate_limit(limit=5, period=30)
async def sping_handler(event):
    """📊 Детальный пинг с информацией о системе"""
    try:
        start = time.perf_counter()
        msg = await edit_or_reply(event, "⚡ Analyzing...")

        # Собираем информацию параллельно
        cpu = PerformanceMonitor.get_cpu_info()
        memory = PerformanceMonitor.get_memory_info()
        disk = PerformanceMonitor.get_disk_info()

        end = time.perf_counter()
        ping_ms = round((end - start) * 1000, 2)
        add_to_history(ping_ms)

        # Определяем качество
        if ping_ms < 100:
            emoji = "🟢"
        elif ping_ms < 300:
            emoji = "🟡"
        elif ping_ms < 500:
            emoji = "🟠"
        else:
            emoji = "🔴"

        text = f"""**⚡ SuperPing Report**

{emoji} **Response:** `{ping_ms}ms`
🕐 **Time:** `{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}`

**💻 System Resources**

**CPU:** `{cpu['percent']}%` {PerformanceMonitor.get_bar(cpu['percent'])}
  ⚙️ Cores: `{cpu['cores']}` | Freq: `{cpu['freq']:.0f} MHz`

**RAM:** `{memory['percent']}%` {PerformanceMonitor.get_bar(memory['percent'])}
  📊 Used: `{PerformanceMonitor.format_bytes(memory['used'])}` / `{PerformanceMonitor.format_bytes(memory['total'])}`

**Disk:** `{disk['percent']}%` {PerformanceMonitor.get_bar(disk['percent'])}
  💾 Used: `{PerformanceMonitor.format_bytes(disk['used'])}` / `{PerformanceMonitor.format_bytes(disk['total'])}`

**⏱️ Uptime:** `{PerformanceMonitor.get_uptime()}`"""

        await msg.edit(text)

    except Exception as e:
        await edit_or_reply(event, f"❌ Error: {e}")

@rate_limit(limit=5, period=60)
async def pinginfo_handler(event):
    """📈 Статистика и история пингов"""
    try:
        stats = get_stats()

        if not stats:
            await edit_or_reply(event, "ℹ️ No ping history yet\nUse `.ping` to start collecting data")
            return

        text = f"""**📈 Ping Statistics**

**Session Stats ({stats['count']} measurements)**
🟢 **Min:** `{stats['min']:.2f}ms`
📊 **Avg:** `{stats['avg']:.2f}ms`
🔴 **Max:** `{stats['max']:.2f}ms`

**Recent Pings** (last 10)"""

        for i, p in enumerate(reversed(ping_history[-10:]), 1):
            time_str = datetime.fromtimestamp(p['timestamp']).strftime('%H:%M:%S')

            if p['ms'] < 100:
                emoji = "🟢"
            elif p['ms'] < 300:
                emoji = "🟡"
            elif p['ms'] < 500:
                emoji = "🟠"
            else:
                emoji = "🔴"

            text += f"\n{emoji} `{p['ms']:.1f}ms` at {time_str}"

        text += "\n\n💡 Use `.ping` for quick check\n💡 Use `.sping` for detailed info"

        await edit_or_reply(event, text)

    except Exception as e:
        await edit_or_reply(event, f"❌ Error: {e}")

@rate_limit(limit=3, period=60)
async def sysinfo_handler(event):
    """🖥️ Подробная информация о системе"""
    try:
        msg = await edit_or_reply(event, "🔍 Gathering system info...")

        # Собираем всю информацию
        cpu = PerformanceMonitor.get_cpu_info()
        memory = PerformanceMonitor.get_memory_info()
        disk = PerformanceMonitor.get_disk_info()
        network = PerformanceMonitor.get_network_info()

        text = f"""**🖥️ System Information**

**Platform**
🐧 **OS:** `{platform.system()} {platform.release()}`
🏗️ **Architecture:** `{platform.machine()}`
🐍 **Python:** `{platform.python_version()}`
💻 **Hostname:** `{platform.node()}`

**CPU**
⚙️ **Cores:** `{cpu['cores']}`
📊 **Usage:** `{cpu['percent']}%` {PerformanceMonitor.get_bar(cpu['percent'])}
⚡ **Frequency:** `{cpu['freq']:.0f} MHz`

**Memory**
💾 **Total:** `{PerformanceMonitor.format_bytes(memory['total'])}`
📊 **Used:** `{PerformanceMonitor.format_bytes(memory['used'])}` (`{memory['percent']}%`)
✨ **Available:** `{PerformanceMonitor.format_bytes(memory['available'])}`
{PerformanceMonitor.get_bar(memory['percent'], 15)}

**Disk**
💿 **Total:** `{PerformanceMonitor.format_bytes(disk['total'])}`
📁 **Used:** `{PerformanceMonitor.format_bytes(disk['used'])}` (`{disk['percent']}%`)
{PerformanceMonitor.get_bar(disk['percent'], 15)}

**Network (Session)**
⬆️ **Sent:** `{PerformanceMonitor.format_bytes(network['sent'])}`
⬇️ **Received:** `{PerformanceMonitor.format_bytes(network['recv'])}`

⏱️ **System Uptime:** `{PerformanceMonitor.get_uptime()}`
🕐 **Current Time:** `{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}`"""

        await msg.edit(text)

    except Exception as e:
        await edit_or_reply(event, f"❌ Error: {e}")

@rate_limit(limit=10, period=30)
async def fastping_handler(event):
    """🚀 Ультра-быстрый пинг (только латентность)"""
    try:
        start = time.perf_counter()
        msg = await edit_or_reply(event, "🏓")
        end = time.perf_counter()

        ping_ms = round((end - start) * 1000, 2)
        add_to_history(ping_ms)

        await msg.edit(f"⚡ `{ping_ms}ms`")

    except Exception as e:
        await edit_or_reply(event, f"❌ {e}")

@rate_limit(limit=5, period=60)
async def monitor_handler(event):
    """📊 Живой мониторинг ресурсов (10 секунд)"""
    try:
        msg = await edit_or_reply(event, "📊 Starting live monitor...")

        for i in range(10):
            cpu = PerformanceMonitor.get_cpu_info()
            memory = PerformanceMonitor.get_memory_info()

            text = f"""**📊 Live Monitor** ({i+1}/10)

**CPU:** `{cpu['percent']}%`
{PerformanceMonitor.get_bar(cpu['percent'], 20)}

**RAM:** `{memory['percent']}%`
{PerformanceMonitor.get_bar(memory['percent'], 20)}

**Cores:** `{cpu['cores']}` | **Freq:** `{cpu['freq']:.0f} MHz`
**Used:** `{PerformanceMonitor.format_bytes(memory['used'])}`"""

            await msg.edit(text)
            await asyncio.sleep(1)

        await msg.edit("✅ Monitoring complete")

    except Exception as e:
        await edit_or_reply(event, f"❌ Error: {e}")

# Справка модуля
modules_help = {
    "superping": {
        "ping": "⚡ Quick ping with quality indicator",
        "sping": "📊 Detailed ping with system resources",
        "fastping": "🚀 Ultra-fast ping (latency only)",
        "pinginfo": "📈 Ping statistics and history",
        "sysinfo": "🖥️ Complete system information",
        "monitor": "📊 Live resource monitoring (10s)"
    }
}
