"""
🎛 Hydra Start - Красивый стартовый экран
"""

import platform
import time
from utils.misc import edit_or_reply, rate_limit

__version__ = "1.1.0"
STARTED_AT = time.time()

BANNER = "⚡ 𝗛𝗬𝗗𝗥𝗔 𝗨𝗦𝗘𝗥𝗕𝗢𝗧 ⚡"


def format_uptime(seconds: float) -> str:
    d = int(seconds // 86400)
    h = int((seconds % 86400) // 3600)
    m = int((seconds % 3600) // 60)
    if d > 0:
        return f"{d}д {h}ч {m}м"
    if h > 0:
        return f"{h}ч {m}м"
    return f"{m}м"


def safe_get_modules_stats():
    try:
        import utils.loader as ld
        mods = ld.modules_help or {}
        modules_count = len(mods)
        commands_count = sum(len(v) for v in mods.values())
        return modules_count, commands_count
    except Exception:
        return 0, 0


@rate_limit(limit=5, period=30)
async def start_handler(event):
    """Показать стартовый экран с информацией"""
    try:
        from config import prefix
        user = event.sender
        username = (getattr(user, "username", None) or "unknown")
        firstname = (getattr(user, "first_name", None) or "Unknown")
        uid = getattr(user, "id", "unknown")

        os_name = f"{platform.system()} {platform.release()}"
        arch = platform.machine()
        pyver = platform.python_version()
        uptime = format_uptime(time.time() - STARTED_AT)

        mods, cmds = safe_get_modules_stats()

        text = (
            f"{BANNER}\n\n"
            f"🚀 <b>Hydra UserBot запущен</b>\n"
            f"<b>Версия:</b> <code>{__version__}</code> • <b>Префикс:</b> <code>{prefix}</code>\n\n"
            f"👤 <b>Пользователь:</b> {firstname} (@{username})\n"
            f"🆔 <b>ID:</b> <code>{uid}</code>\n\n"
            f"⏱ <b>Аптайм:</b> <code>{uptime}</code>\n\n"
            f"🖥 <b>Система:</b> <code>{os_name}</code>\n"
            f"🏗 <b>Архитектура:</b> <code>{arch}</code>\n"
            f"🐍 <b>Python:</b> <code>{pyver}</code>\n\n"
            f"<i>Разработчики: @global050 @Aubeig</i>"
        )

        await edit_or_reply(event, text, parse_mode="HTML")
    except Exception as e:
        await edit_or_reply(event, f"❌ Ошибка: {e}")


@rate_limit(limit=5, period=30)
async def about_handler(event):
    """Короткая карточка о боте"""
    try:
        from config import prefix
        os_name = f"{platform.system()} {platform.release()}"
        uptime = format_uptime(time.time() - STARTED_AT)
        mods, cmds = safe_get_modules_stats()
        text = (
            f"<b>Hydra UserBot</b> v{__version__}\n"
            f"• Префикс: <code>{prefix}</code>\n"
            f"• Аптайм: <code>{uptime}</code>\n"
            f"• Платформа: <code>{os_name}</code>\n"
            f"• Помощь: <code>{prefix}help</code>"
        )
        await edit_or_reply(event, text, parse_mode="HTML")
    except Exception as e:
        await edit_or_reply(event, f"❌ Ошибка: {e}")


modules_help = {
    "start": {
        "start": "Показать стартовый экран",
        "about": "Короткая карточка о боте"
    }
}
