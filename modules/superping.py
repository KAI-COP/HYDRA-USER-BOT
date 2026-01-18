import time, asyncio, psutil, platform
from datetime import datetime
from utils.misc import edit_or_reply, rate_limit

ping_history = []

class Sys:
    @staticmethod
    def get_info():
        mem = psutil.virtual_memory()
        return {
            "cpu": f"{psutil.cpu_percent()}%",
            "ram": f"{psutil.percent(mem.used, mem.total)}%",
            "uptime": datetime.fromtimestamp(psutil.boot_time()).strftime("%H:%M")
        }

    @staticmethod
    def bar(p, l=10):
        f = int(l * p / 100)
        return '█' * f + '░' * (l - f)

def get_stats():
    if not ping_history: return None
    p = [x["ms"] for x in ping_history]
    return {"min": min(p), "max": max(p), "avg": sum(p)/len(p)}

@rate_limit(10, 30)
async def ping_handler(event):
    start = time.perf_counter()
    msg = await edit_or_reply(event, "<code>⚡...</code>", parse_mode='HTML')
    ms = round((time.perf_counter() - start) * 1000, 2)
    ping_history.append({"ms": ms, "timestamp": time.time()})
    if len(ping_history) > 50: ping_history.pop(0)

    color = "🟢" if ms < 150 else "🟡" if ms < 400 else "🔴"
    s = get_stats()
    
    res = f"<b>⚡ HYDRA PING</b>\n\n"
    res += f"{color} <b>Latency:</b> <code>{ms}ms</code>\n"
    res += f"📊 <b>Avg:</b> <code>{s['avg']:.1f}ms</code> | <b>Max:</b> <code>{s['max']:.1f}ms</code>"
    await msg.edit(res, parse_mode='HTML')

@rate_limit(5, 30)
async def sping_handler(event):
    start = time.perf_counter()
    msg = await edit_or_reply(event, "<code>🛰️...</code>", parse_mode='HTML')
    i = Sys.get_info()
    ms = round((time.perf_counter() - start) * 1000, 2)
    
    res = f"<b>⚡ HYDRA SYSTEM</b>\n\n"
    res += f"🛰️ <b>Ping:</b> <code>{ms}ms</code>\n"
    res += f"⚙️ <b>CPU:</b> <code>{i['cpu']}</code> | <b>RAM:</b> <code>{i['ram']}</code>\n"
    res += f"⏱️ <b>Boot:</b> <code>{i['uptime']}</code>\n"
    res += f"🐍 <b>Py:</b> <code>{platform.python_version()}</code>"
    await msg.edit(res, parse_mode='HTML')

@rate_limit(5, 60)
async def monitor_handler(event):
    msg = await edit_or_reply(event, "<b>📊 Monitoring...</b>", parse_mode='HTML')
    for _ in range(5):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        text = f"<b>📊 LIVE MONITOR</b>\n\n"
        text += f"<b>CPU:</b> <code>{cpu}%</code> {Sys.bar(cpu)}\n"
        text += f"<b>RAM:</b> <code>{ram}%</code> {Sys.bar(ram)}"
        await msg.edit(text, parse_mode='HTML')
        await asyncio.sleep(1.5)
    await msg.edit(text + "\n\n✅ <i>Done</i>", parse_mode='HTML')

modules_help = {
    "superping": {
        "ping": "Quick ping stats",
        "sping": "System + Ping report",
        "monitor": "Live CPU/RAM (5s)"
    }
}