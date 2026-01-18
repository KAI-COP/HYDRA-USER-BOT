import importlib.util
import importlib.machinery
import sys
import os
import asyncio
import re
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

modules_help = {}

async def load_all_modules(directory: str, client):
    
    modules_path = Path(directory)
    if not modules_path.exists():
        print("    ❌ Directory 'modules' not found")
        return 0, 0

    success = 0
    total = 0
    
    # Добавляем путь для импорта
    sys.path.insert(0, str(Path.cwd()))

    for file in modules_path.glob("*.py"):
        if file.stem.startswith("_"):
            continue
            
        total += 1
        module_name = file.stem
        
        if await load_single_module(module_name, file, client):
            success += 1
            print(f"    ✅ {module_name}")
        else:
            print(f"    ❌ {module_name}")

    print(f"    📊 Loaded {success}/{total} modules")
    return success, total

async def load_single_module(module_name: str, file_path: Path, client):
    
    try:
        # Импортируем модуль
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"modules.{module_name}"] = module
        spec.loader.exec_module(module)
        
        module.client = client

        await register_module_handlers(module, module_name, client)

        await register_module_help(module, module_name)

        return True

    except Exception as e:
        logger.error(f"Error loading {module_name}: {e}")
        return False

async def register_module_handlers(module, module_name: str, client):
    """Регистрация обработчиков команд модуля"""
    from telethon import events
    from config import prefix

    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        
        if not callable(attr) or not asyncio.iscoroutinefunction(attr):
            continue

        command_name = None
        if attr_name.endswith('_handler'):
            command_name = attr_name[:-8]  
        elif not attr_name.startswith('_') and len(attr_name) < 20:
            command_name = attr_name

        if command_name:
           
            pattern = rf'^{re.escape(prefix)}{command_name}(?:\s|$)'
            
            @client.on(events.NewMessage(pattern=pattern, outgoing=True))
            async def command_handler(event, cmd_func=attr):
                await cmd_func(event)

async def register_module_help(module, module_name: str):
    """Регистрация справки модуля"""
    try:
        if hasattr(module, 'modules_help'):
            if isinstance(module.modules_help, dict):
                for mod_name, commands in module.modules_help.items():
                    if mod_name not in modules_help:
                        modules_help[mod_name] = {}
                    modules_help[mod_name].update(commands)
                return

        if module_name not in modules_help:
            modules_help[module_name] = {}

        for attr_name in dir(module):
            if not attr_name.startswith('_') and callable(getattr(module, attr_name)):
                if attr_name.endswith('_handler'):
                    cmd_name = attr_name[:-8]
                    modules_help[module_name][cmd_name] = f"Command: {cmd_name}"

    except Exception as e:
        logger.error(f"Error registering help for {module_name}: {e}")
