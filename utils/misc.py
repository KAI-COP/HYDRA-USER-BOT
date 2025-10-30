"""
Вспомогательные функции для модулей
"""

import time
from datetime import datetime
from functools import wraps
import asyncio
import json
import os

# Глобальное время старта бота
bot_start_time = None

# Система ограничений
_rate_limits = {}

# Система сохранения настроек
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

# Глобальные настройки
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
            
            # Удаляем старые записи
            _rate_limits[user_id] = [
                timestamp for timestamp in _rate_limits[user_id]
                if current_time - timestamp < period
            ]
            
            # Проверяем лимит
            if len(_rate_limits[user_id]) >= limit:
                wait_time = period - (current_time - _rate_limits[user_id][0])
                await edit_or_reply(
                    event,
                    f"⏳ **Rate limit exceeded!**\n"
                    f"Please wait `{int(wait_time)}` seconds\n"
                    f"**Limit:** `{limit}` per `{period}`s"
                )
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
