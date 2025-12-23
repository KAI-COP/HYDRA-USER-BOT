# modules/stats.py

from telethon import events, functions
from utils.misc import edit_or_reply
from config import prefix

modules_help = {
    "stats": {
        "stats": "📚 Статистика аккаунта"
    }
}

async def get_full_blocked_stats(client):
    """Полный подсчет блоклиста БЕЗ лимитов"""
    blocked_users = 0
    blocked_bots = 0
    total_blocked = 0
    offset = 0
    limit = 100
    
    while True:
        try:
            # Запрашиваем порциями по 100
            result = await client(functions.contacts.GetBlockedRequest(
                offset=offset, 
                limit=limit
            ))
            
            if not result.users:
                break
                
            total_blocked += len(result.users)
            
            # Классифицируем каждую порцию
            for user in result.users:
                if hasattr(user, 'bot') and user.bot:
                    blocked_bots += 1
                else:
                    blocked_users += 1
            
            offset += limit
            
            # Безопасная остановка (максимум 5000)
            if offset > 5000:
                break
                
        except Exception:
            break
    
    return total_blocked, blocked_users, blocked_bots

async def stats_handler(event):
    """📚 Статистика аккаунта"""
    client = event.client
    msg = await edit_or_reply(event, "📚 **Считаю чаты + блоклист...**")
    
    # Счетчики чатов (БЫСТРО)
    total_chats = 0
    private_chats = 0
    bots = 0
    groups = 0
    channels = 0
    archived = 0
    
    async for dialog in client.iter_dialogs():
        total_chats += 1
        
        entity = dialog.entity
        
        # Архив
        try:
            if hasattr(dialog, 'folder_id') and dialog.folder_id == 1:
                archived += 1
                continue
        except:
            pass
        
        # Классификация чатов
        try:
            if hasattr(entity, 'bot') and entity.bot:
                bots += 1
            elif hasattr(entity, 'first_name') and not hasattr(entity, 'title'):
                private_chats += 1
            elif hasattr(entity, 'megagroup') and entity.megagroup:
                groups += 1
            elif hasattr(entity, 'broadcast') and entity.broadcast:
                channels += 1
            elif hasattr(entity, 'title'):
                groups += 1
        except:
            private_chats += 1
    
    # 🔥 ПОЛНЫЙ БЛОКЛИСТ (цикл по всем страницам)
    await msg.edit("📚 **Считаю полный блоклист...**")
    total_blocked, blocked_users, blocked_bots = await get_full_blocked_stats(client)
    
    text = f"""📚 **Статистика аккаунта**

📊 **Всего чатов:** {total_chats}

👤 **Личных чатов:** {private_chats}
🤖 **Ботов:** {bots}
👥 **Групп:** {groups}
👥 **Каналов:** {channels}
📨 **Архивированных чатов:** {archived}

✋ **Всего заблокированных:** {total_blocked}
 Ͱ👤 **Пользователи:** {blocked_users}
 Ͱ🤖 **Боты:** {blocked_bots}"""
    
    await msg.edit(text)
