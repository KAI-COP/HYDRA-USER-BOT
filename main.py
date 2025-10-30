import asyncio
import logging
import os
import time
from pathlib import Path
import sys

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

import config
from utils.misc import set_start_time

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Время запуска бота
start_time = time.time()
set_start_time(start_time)

def clear_screen():
    """Очистка экрана терминала"""
    os.system('cls' if os.name == 'nt' else 'clear')

def fix_session_file():
    """Исправление поврежденного файла сессии"""
    session_file = "hydra_session.session"
    if os.path.exists(session_file):
        try:
            if os.path.getsize(session_file) < 100:
                os.remove(session_file)
                print("    🔧 Fixed corrupted session file")
        except:
            os.remove(session_file)
            print("    🔧 Fixed corrupted session file")

async def main():
    """Главная функция запуска"""
    clear_screen()
    
    print("""
    ╔══════════════════════════════╗
    ║         HYDRA USERBOT        ║
    ║         Pure Version         ║
    ║          Starting...         ║
    ╚══════════════════════════════╝
    """)
    
    # Исправляем файл сессии если нужно
    fix_session_file()
    
    # Создаем клиент
    client = TelegramClient("hydra_session", config.api_id, config.api_hash)
    
    # Создаем директорию для модулей если не существует
    Path("modules").mkdir(exist_ok=True)
    
    try:
        await client.start()
        
        # Получаем информацию о пользователе
        me = await client.get_me()
        print(f"    ✅ Logged in as @{me.username or me.first_name}")
        
    except SessionPasswordNeededError:
        print("    🔐 Two-factor authentication required")
        password = input("    Enter password: ")
        await client.sign_in(password=password)
        me = await client.get_me()
        print(f"    ✅ Logged in as @{me.username or me.first_name}")
    except Exception as e:
        print(f"    ❌ Failed to start: {e}")
        return
    
    # ЗАГРУЗКА МОДУЛЕЙ
    print("\n    📦 Loading modules...\n")
    
    # Импортируем загрузчик
    from utils.loader import load_all_modules
    
    # Загружаем модули
    success, total = await load_all_modules("modules", client)
    
    print(f"""
    ╔══════════════════════════════╗
    ║       HYDRA STARTED!         ║
    ║    Modules: {success:2d}/{total:2d} loaded       ║
    ║   Prefix: {config.prefix}                    ║
    ║   Type {config.prefix}help for commands    ║
    ╚══════════════════════════════╝
    """)
    
    try:
        print("    🚀 Bot is running... Press Ctrl+C to stop")
        await client.run_until_disconnected()
    except KeyboardInterrupt:
        print("\n    🛑 Stopping...")
    finally:
        await client.disconnect()
        print("    👋 Goodbye!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
