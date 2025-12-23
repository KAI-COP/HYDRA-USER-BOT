# modules/cleanup.py

from telethon import events
from telethon.errors import RPCError
from utils.misc import edit_or_reply
from config import prefix
import asyncio
import re

modules_help = {
    "cleanup": {
        "cleanmy": "🧹 Delete ALL your messages in current chat",
        "cleanmyl": "🧹 Delete last 1000 your messages (SAFE)",
        "cleaninfo": "ℹ️ Info about your messages in chat"
    }
}

async def _delete_user_messages(client, chat_id, user_id, limit=None, progress_msg=None):
    """Удаление с прогресс-баром"""
    deleted = 0
    total_scanned = 0
    
    async for msg in client.iter_messages(chat_id, from_user=user_id, limit=limit):
        total_scanned += 1
        try:
            await msg.delete()
            deleted += 1
            
            # Обновляем прогресс каждые 10 сообщений
            if deleted % 10 == 0 and progress_msg:
                percent = (deleted / total_scanned) * 100
                await progress_msg.edit(f"🧹 **Cleaning...** `{deleted}/{total_scanned}` ({percent:.0f}%)")
                
        except RPCError as e:
            if "MESSAGE_DELETE_FORBIDDEN" in str(e):
                if progress_msg:
                    await progress_msg.edit("⚠️ **Some messages too old** - can't delete")
            continue
        except Exception:
            continue
    
    return deleted, total_scanned

# 🔥 РАБОЧИЕ ОБРАБОТЧИКИ С ОТЛАДКОЙ
async def cleanmy_handler(event):
    print("🚀 cleanmy_handler TRIGGERED!")
    print(f"Event text: {event.text}")
    
    client = event.client
    chat = await event.get_chat()
    me = await client.get_me()
    
    msg = await edit_or_reply(event, "🔍 **Scanning your messages...**")
    
    # Полная очистка (может быть долго!)
    deleted, scanned = await _delete_user_messages(
        client, chat.id, me.id, limit=None, progress_msg=msg
    )
    
    status = "✅" if deleted > 0 else "ℹ️"
    await msg.edit(
        f"{status} **Cleanup complete!**\n"
        f"🗑️ **Deleted:** `{deleted}`\n"
        f"📊 **Scanned:** `{scanned}`\n"
        f"💬 **Chat:** `{chat.title or 'DM'}`"
    )

async def cleanmyl_handler(event):
    print("🚀 cleanmyl_handler TRIGGERED!")
    
    client = event.client
    chat = await event.get_chat()
    me = await client.get_me()
    
    LIMIT = 1000
    msg = await edit_or_reply(event, f"🧹 **Safe cleanup** (last `{LIMIT}` msgs)")
    
    deleted, scanned = await _delete_user_messages(
        client, chat.id, me.id, limit=LIMIT, progress_msg=msg
    )
    
    await msg.edit(
        f"✅ **Safe cleanup done!**\n"
        f"🗑️ **Deleted:** `{deleted}` / `{scanned}`\n"
        f"💬 **Chat:** `{chat.title or 'DM'}`"
    )

async def cleaninfo_handler(event):
    """Показывает статистику сообщений"""
    print("ℹ️ cleaninfo_handler TRIGGERED!")
    
    client = event.client
    chat = await event.get_chat()
    me = await client.get_me()
    
    msg = await edit_or_reply(event, "📊 **Counting your messages...**")
    
    # Подсчитываем сообщения
    count = 0
    async for _ in client.iter_messages(chat.id, from_user=me.id, limit=5000):
        count += 1
    
    await msg.edit(
        f"📊 **Your messages in chat:**\n"
        f"💬 **Chat:** `{chat.title or 'DM'}`\n"
        f"📈 **Total:** `{count}`\n\n"
        f"🧹 **Use:**\n"
        f"`{prefix}cleanmyl` - delete last 1000\n"
        f"`{prefix}cleanmy` - delete ALL"
    )

print("🔧 CLEANUP MODULE READY! Commands: cleanmy, cleanmyl, cleaninfo")
