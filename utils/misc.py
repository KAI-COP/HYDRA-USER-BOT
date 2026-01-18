import time
from datetime import datetime
from functools import wraps
import asyncio
import json
import os

bot_start_time = None

_rate_limits = {}

SETTINGS_FILE = "user_settings.json"

def load_settings():
    """Загрузить настройки пользователей"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_settings(settings):
    """Сохранить настройки пользователей"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

user_settings = load_settings()

def set_start_time(start_time: float):
    """Установка времени старта бота"""
    global bot_start_time
    bot_start_time = start_time

def get_start_time() -> float:
    """Получение времени старта бота"""
    return bot_start_time

def get_uptime(start_time: float = None) -> str:
    """
    Форматирование uptime в читаемый вид
    """
    if start_time is None:
        start_time = get_start_time()
        if start_time is None:
            return "00:00:00"
    
    uptime_seconds = int(time.time() - start_time)
    return datetime.utcfromtimestamp(uptime_seconds).strftime("%H:%M:%S")

async def edit_or_reply(event, text: str, **kwargs):
    """
    Редактирует сообщение если оно исходящее, иначе отвечает на него
    """
    try:
        if event.out:
            return await event.edit(text, **kwargs)
        else:
            return await event.reply(text, **kwargs)
    except Exception:
        return await event.reply(text, **kwargs)

def rate_limit(limit: int = 20, period: int = 120):
    """
    Декоратор для ограничения использования команд
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(event, *args, **kwargs):
            user_id = event.sender_id
            current_time = time.time()
            
            if user_id not in _rate_limits:
                _rate_limits[user_id] = []
            
            _rate_limits[user_id] = [
                timestamp for timestamp in _rate_limits[user_id]
                if current_time - timestamp < period
            ]
            
            if len(_rate_limits[user_id]) >= limit:
                wait_time = int(period - (current_time - _rate_limits[user_id][0]))
                
                limit_message = f"""
<b>⏰ Rate Limit Exceeded</b>

<blockquote>🚫 <b>Limit reached</b>
⏱️ <b>Wait time:</b> <code>{wait_time}s</code>
📊 <b>Current usage:</b> <code>{len(_rate_limits[user_id])}/{limit}</code>
🕒 <b>Period:</b> <code>{period}s</code></blockquote>

<b>💡 Rate limit tip</b>
<blockquote>• Slow down with commands
• Wait before retrying
• Contact admin if issue persists</blockquote>

<blockquote>🔒 Anti-spam protection</blockquote>
"""
                await edit_or_reply(event, limit_message, parse_mode='HTML')
                return
            
            # Добавляем текущее использование
            _rate_limits[user_id].append(current_time)
            
            return await func(event, *args, **kwargs)
        
        return wrapper
    return decorator

async def fast_animation(message, emoji: str, final_text: str):
    """
    Сверхбыстрая анимация с одним эмодзи
    """
    try:
        await message.edit(emoji)
        await asyncio.sleep(0.05)
        await message.edit(final_text)
    except Exception:
        try:
            await message.edit(final_text)
        except:
            pass

def get_user_setting(user_id, key, default=None):
    """Получить настройку пользователя"""
    return user_settings.get(str(user_id), {}).get(key, default)

def set_user_setting(user_id, key, value):
    """Установить настройку пользователя"""
    user_id = str(user_id)
    if user_id not in user_settings:
        user_settings[user_id] = {}
    user_settings[user_id][key] = value
    return save_settings(user_settings)

def get_rate_limit_info(user_id):
    """Получить информацию о текущих лимитах пользователя"""
    if user_id not in _rate_limits:
        return {
            'current_usage': 0,
            'max_limit': 20,
            'period': 120
        }
    
    current_time = time.time()
    recent_uses = [
        timestamp for timestamp in _rate_limits[user_id]
        if current_time - timestamp < 120  # 2 минуты период 
    ]
    
    return {
        'current_usage': len(recent_uses),
        'max_limit': 20,
        'period': 120,
        'reset_in': int(120 - (current_time - recent_uses[0])) if recent_uses else 0
    }