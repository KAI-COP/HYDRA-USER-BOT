from utils.misc import edit_or_reply
import aiohttp
import ast
import asyncio
import contextlib
import difflib
import functools
import importlib
import inspect
import io
import logging
import os
import re
import shutil
import sys
import time
import types
import typing
import uuid
from collections import ChainMap
from importlib.machinery import ModuleSpec
from urllib.parse import urlparse
from telethon.tl.types import DocumentAttributeFilename

logger = logging.getLogger(__name__)

# Глобальный словарь для хранения временных модулей
temp_modules = {}

# --- Simplified Internal Components for Hydra Compatibility ---

class Module:
    """Mock base class for modules."""
    def __init__(self):
        self.strings = {}
        self.commands = {}
        self.inline_handlers = {}
        self.__class__.__name__ = "DummyModule"
        self.__origin__ = "<string>"
        self.config = {}

    def __getattr__(self, name):
        if name in self.strings:
            return self.strings[name]
        return super().__getattribute__(name)

class Library(Module):
    """Mock class for libraries."""
    pass

class LoadError(Exception):
    """Custom exception for module loading errors."""
    pass

class SelfUnload(Exception):
    """Custom exception for self-unloading modules."""
    pass

class SelfSuspend(Exception):
    """Custom exception for self-suspending modules."""
    pass

class CoreOverwriteError(Exception):
    """Custom exception for core module overwrite attempts."""
    def __init__(self, target, type="module"):
        super().__init__(f"Core overwrite error: {target} type {type}")
        self.target = target
        self.type = type

class CoreUnloadError(Exception):
    """Custom exception for core module unload attempts."""
    pass

class ScamDetectionError(Exception):
    """Custom exception for detected scam modules."""
    pass

class RegexMock:
    """Mock for regex objects used to find requirements."""
    def search(self, text):
        match = re.search(r"# ?requires: ?(.+)", text)
        if match:
            return [match.group(1)]
        return None

VALID_PIP_PACKAGES = RegexMock()

class RemoteStorage:
    """Mock for remote storage interaction."""
    def __init__(self, client):
        self._client = client

    async def preload(self, modules):
        logger.debug("Preloading modules (mock): %s", modules)

    async def fetch(self, url, auth=None):
        import requests
        res = await asyncio.get_event_loop().run_in_executor(None, requests.get, url, auth)
        res.raise_for_status()
        return res.text.encode()

class MockMain:
    """Mock for main application object."""
    def __init__(self):
        self.__version__ = (1, 0, 0)

main = MockMain()

class MockGeek:
    """Mock for compatibility layer."""
    def compat(self, doc):
        return doc

geek = MockGeek()

class MockTranslator:
    """Mock for module translator."""
    async def load_module_translations(self, pack_url):
        logger.debug(f"Loading translations for {pack_url} (mock)")
        return None

class MockAllModules:
    """Mock for the central module manager."""
    def __init__(self):
        self.modules = []
        self.libraries = []
        self.aliases = {}
        self.secure_boot = False
        self.translator = MockTranslator()

    def add_aliases(self, new_aliases):
        self.aliases.update(new_aliases)

    def add_alias(self, alias, cmd_name, *args):
        self.aliases[alias] = f"{cmd_name} {' '.join(args)}"
        return True

    def lookup(self, name):
        for mod in self.modules:
            mod_name = getattr(mod, 'name', None) or mod.__class__.__name__
            if mod_name == name or (hasattr(mod, 'strings') and mod.strings.get("name") == name):
                return mod
        if name == "settings":
            return MockSettings()
        raise ValueError(f"Module {name} not found (mock)")

    async def register_module(self, spec, module_name, origin, save_fs=False):
        module = Module()
        module.__origin__ = origin
        module.__class__.__name__ = module_name.split(".")[-1]
        module.strings["name"] = module_name.split(".")[-1]
        try:
            module.__doc__ = inspect.getdoc(eval(compile(spec.loader.get_source(module_name), '<string>', 'exec')))
        except Exception:
            module.__doc__ = "No docstring found."
        self.modules.append(module)
        logger.debug(f"Registered module (mock): {module_name}")
        return module

    async def unload_module(self, module_name):
        original_len = len(self.modules)
        self.modules = [mod for mod in self.modules if mod.__class__.__name__ != module_name]
        if len(self.modules) < original_len:
            logger.debug(f"Unloaded module (mock): {module_name}")
            return [module_name]
        raise CoreUnloadError(f"Module {module_name} not found for unload")

    def send_config_one(self, instance):
        logger.debug(f"Sent config to module (mock): {instance.__class__.__name__}")

    async def send_ready_one(self, instance, no_self_unload=False, from_dlmod=False):
        logger.debug(f"Sent ready to module (mock): {instance.__class__.__name__}")

    async def register_all(self, no_external=True):
        logger.debug("Registered all modules (mock)")
        return []

allmodules = MockAllModules()

class MockDB:
    """Mock for database interaction."""
    def __init__(self):
        self._data = {}

    def get(self, module_name, key, default=None):
        return self._data.get(module_name, {}).get(key, default)

    def set(self, module_name, key, value):
        if module_name not in self._data:
            self._data[module_name] = {}
        self._data[module_name][key] = value

    def save(self):
        logger.debug("DB saved (mock)")

_db = MockDB()

class MockInline:
    """Mock for inline handling system."""
    def __init__(self):
        self.bot_username = "hydra_bot"
        self.init_complete = True

    async def form(self, text, event, reply_markup):
        await edit_or_reply(event, text + "\n(Inline form not fully supported, simplified to text.)")
        return True

class MockStringLoader:
    """Mock for loading modules from a string."""
    def __init__(self, data, fullname):
        self.data = data.encode() if isinstance(data, str) else data

class MockSettings:
    """Mock for settings module."""
    def __init__(self):
        self.config = {}

# --- Main Command Handlers ---

async def loadmod_handler(event):
    """Загрузить модуль в ОЗУ для тестирования"""
    try:
        if not event.out:
            return
            
        reply = await event.get_reply_message()
        
        # Если ответ на текстовое сообщение с кодом
        if reply and reply.text:
            code = reply.text
            module_name = f"temp_module_{reply.id}"
            
        # Если ответ на файл .py
        elif reply and reply.document:
            # Проверяем что это Python файл по расширению
            file_name = getattr(reply.document.attributes[0], 'file_name', None) if reply.document.attributes else None
            if not file_name or not file_name.endswith('.py'):
                await edit_or_reply(event, "❌ Файл должен быть Python файлом (.py)")
                return
                
            # Скачиваем файл
            file_path = await reply.download_media()
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='utf-8-sig') as f:
                        code = f.read()
                except Exception as e:
                    await edit_or_reply(event, f"❌ Ошибка чтения файла: {e}")
                    return
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)  # Удаляем временный файл
            
            module_name = f"temp_file_module_{reply.id}"
            
        else:
            await edit_or_reply(event, "❌ Ответьте на сообщение с кодом Python или на .py файл")
            return
        
        # Проверяем безопасность кода
        safety_check = await check_code_safety(code)
        if not safety_check["safe"]:
            await edit_or_reply(event, f"❌ Опасный код обнаружен:\n{safety_check['reason']}")
            return
        
        # Загружаем модуль в память
        result = await load_module_to_memory(module_name, code)
        
        if result["success"]:
            temp_modules[module_name] = {
                "code": code,
                "module": result["module"],
                "commands": result["commands"]
            }
            
            response = f"✅ Модуль `{module_name}` загружен в ОЗУ!\n"
            response += f"📦 Команд загружено: {len(result['commands'])}\n"
            if result["commands"]:
                response += "🔧 Доступные команды:\n"
                for cmd in result["commands"]:
                    response += f"• `.{cmd}`\n"
            response += f"⚠️ Модуль временный и будет удален после перезагрузки"
            
            await edit_or_reply(event, response)
        else:
            await edit_or_reply(event, f"❌ Ошибка загрузки:\n```{result['error']}```")
            
    except Exception as e:
        await edit_or_reply(event, f"❌ Ошибка: {e}")

async def lm_handler(event):
    """Скачать модуль по ссылке или из файла"""
    try:
        if not event.out:
            return
            
        args = event.text.split(maxsplit=1)
        reply = await event.get_reply_message()
        
        # Если есть аргумент - считаем это ссылкой
        if len(args) > 1:
            url = args[1]
            await download_module_from_url(event, url)
            
        # Если есть reply с текстовым кодом
        elif reply and reply.text:
            code = reply.text
            module_name = await extract_module_name(code) or f"module_{reply.id}"
            
            # Создаем папку downloads если нет
            if not os.path.exists('downloads'):
                os.makedirs('downloads')
            
            # Сохраняем в файл для скачивания
            filename = f"downloads/{module_name}.py"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(code)
            
            await event.client.send_file(
                event.chat_id,
                filename,
                caption=f"📥 Модуль `{module_name}.py`",
                reply_to=reply.id
            )
            await event.delete()
            
        # Если есть reply с файлом .py
        elif reply and reply.document:
            # Проверяем что это Python файл по расширению
            file_name = getattr(reply.document.attributes[0], 'file_name', None) if reply.document.attributes else None
            if not file_name or not file_name.endswith('.py'):
                await edit_or_reply(event, "❌ Файл должен быть Python файлом (.py)")
                return
                
            # Скачиваем и пересылаем
            file_path = await reply.download_media()
            
            caption = f"📥 Модуль `{file_name}`"
            await event.client.send_file(
                event.chat_id,
                file_path,
                caption=caption,
                reply_to=reply.id
            )
            if os.path.exists(file_path):
                os.remove(file_path)  # Удаляем временный файл
            await event.delete()
                
        else:
            await edit_or_reply(event, "❌ Использование: `.lm <ссылка>` или ответ на сообщение/файл с кодом")
            
    except Exception as e:
        await edit_or_reply(event, f"❌ Ошибка: {e}")

async def unloadmod_handler(event):
    """Выгрузить временный модуль из ОЗУ"""
    try:
        if not event.out:
            return
            
        args = event.text.split()
        if len(args) != 2:
            # Показать список загруженных модулей
            if temp_modules:
                response = "📦 Загруженные временные модули:\n"
                for name, data in temp_modules.items():
                    response += f"• `{name}` - {len(data['commands'])} команд\n"
                response += "\nДля выгрузки: `.unloadmod <имя>`"
            else:
                response = "❌ Нет загруженных временных модулей"
            await edit_or_reply(event, response)
            return
        
        module_name = args[1]
        if module_name in temp_modules:
            # Удаляем из sys.modules если там есть
            for key in list(sys.modules.keys()):
                if key.startswith(module_name):
                    del sys.modules[key]
            
            # Удаляем из наших временных модулей
            del temp_modules[module_name]
            await edit_or_reply(event, f"✅ Модуль `{module_name}` выгружен из ОЗУ")
        else:
            await edit_or_reply(event, f"❌ Модуль `{module_name}` не найден")
            
    except Exception as e:
        await edit_or_reply(event, f"❌ Ошибка: {e}")

# --- Utility Functions ---

async def check_code_safety(code):
    """Проверка кода на опасные операции"""
    dangerous_keywords = [
        'os.system', 'subprocess', 'eval(', 'exec(', '__import__',
        'open(', 'file(', 'compile(', 'input(', 'reload(',
        'rm -rf', 'del ', 'format(', 'pickle', 'marshal',
        'sys.exit', 'quit(', 'exit(', 'kill', 'shutdown',
        'os.remove', 'os.unlink', 'shutil.rmtree', 'os.rmdir',
        '__builtins__', '__import__', 'globals', 'locals',
        'breakpoint', 'memoryview', 'bytearray', 'super(',
        '().__class__', '().__base__', '.__subclasses__'
    ]
    
    for keyword in dangerous_keywords:
        if keyword in code:
            return {
                "safe": False,
                "reason": f"Обнаружена опасная операция: `{keyword}`"
            }
    
    # Дополнительная проверка через AST
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            # Запрещаем импорт опасных модулей
            if isinstance(node, ast.Import):
                for name in node.names:
                    if name.name in ['os', 'sys', 'subprocess', 'shutil', 'pickle', 'marshal']:
                        return {
                            "safe": False,
                            "reason": f"Запрещенный импорт: `{name.name}`"
                        }
            # Запрещаем вызовы опасных функций
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', 'compile', 'input', 'exit', 'quit']:
                        return {
                            "safe": False,
                            "reason": f"Запрещенный вызов функции: `{node.func.id}`"
                        }
    except SyntaxError:
        # Если код не парсится, это может быть опасно
        return {
            "safe": False,
            "reason": "Синтаксическая ошибка в коде"
        }
    
    return {"safe": True, "reason": ""}

async def load_module_to_memory(module_name, code):
    """Загрузка модуля в оперативную память"""
    try:
        # Создаем новый модуль
        spec = importlib.util.spec_from_loader(module_name, loader=None)
        module = importlib.util.module_from_spec(spec)
        
        # Захватываем вывод для отладки
        output = io.StringIO()
        
        # Выполняем код в контексте модуля
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            exec(code, module.__dict__)
        
        # Регистрируем модуль
        sys.modules[module_name] = module
        
        # Ищем команды в модуле
        commands = []
        for attr_name in dir(module):
            if attr_name.endswith('_handler') and callable(getattr(module, attr_name)):
                command_name = attr_name.replace('_handler', '')
                commands.append(command_name)
        
        return {
            "success": True,
            "module": module,
            "commands": commands,
            "output": output.getvalue()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "commands": []
        }

async def download_module_from_url(event, url):
    """Скачать модуль по URL"""
    try:
        if not url.startswith(('http://', 'https://')):
            await edit_or_reply(event, "❌ Неверный URL")
            return
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                code = await response.text()
        
        module_name = await extract_module_name(code) or "downloaded_module"
        
        # Создаем папку downloads если нет
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
        
        # Сохраняем файл
        filename = f"downloads/{module_name}.py"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(code)
        
        await event.client.send_file(
            event.chat_id,
            filename,
            caption=f"📥 Модуль `{module_name}.py` из {url}",
            reply_to=event.reply_to_msg_id
        )
        await event.delete()
        
    except aiohttp.ClientError as e:
        await edit_or_reply(event, f"❌ Ошибка загрузки: {e}")
    except Exception as e:
        await edit_or_reply(event, f"❌ Ошибка: {e}")

async def extract_module_name(code):
    """Извлечь имя модуля из кода"""
    try:
        # Ищем modules_help для определения имени
        lines = code.split('\n')
        for line in lines:
            if 'modules_help' in line and '=' in line:
                # Пытаемся найти имя модуля в структуре modules_help
                if '{' in line and '}' in line:
                    start = line.find('{') + 1
                    end = line.find(':', start)
                    if end > start:
                        module_name = line[start:end].strip().strip('"\'')
                        return module_name
                # Ищем в следующих строках если структура многострочная
                idx = lines.index(line)
                for i in range(idx + 1, min(idx + 10, len(lines))):
                    next_line = lines[i].strip()
                    if next_line.startswith('"') or next_line.startswith("'"):
                        module_name = next_line.strip('"\': ')
                        if module_name:
                            return module_name
                        break
                    elif ':' in next_line:
                        module_name = next_line.split(':')[0].strip('"\' ')
                        if module_name:
                            return module_name
                        break
    except:
        pass
    
    # Пытаемся найти имя класса или функции
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                return node.name.lower()
            elif isinstance(node, ast.FunctionDef):
                if node.name.endswith('_handler'):
                    return node.name.replace('_handler', '')
    except:
        pass
    
    return None

# Справка модуля
modules_help = {
    "module_loader": {
        "lm": "Скачать модуль: .lm <url> или ответ на сообщение/файл .py",
        "loadmod": "Загрузить модуль в ОЗУ для тестирования (ответ на код Python или .py файл)",
        "unloadmod": "Выгручить временный модуль из ОЗУ"
    }
}
