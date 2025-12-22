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
                wait_time = int(period - (current_time - _rate_limits[user_id][0]))
                
                # Красивое сообщение о лимите
                # translator импортирован глобально
                limit_message = f"""
<b>⏰ {translator.get_text(user_id, 'rate_limit_exceeded')}</b>

<blockquote>🚫 <b>{translator.get_text(user_id, 'limit_reached')}</b>
⏱️ <b>{translator.get_text(user_id, 'wait_time')}:</b> <code>{wait_time}{translator.get_text(user_id, 'seconds')}</code>
📊 <b>{translator.get_text(user_id, 'current_usage')}:</b> <code>{len(_rate_limits[user_id])}/{limit}</code>
🕒 <b>{translator.get_text(user_id, 'period')}:</b> <code>{period}{translator.get_text(user_id, 'seconds')}</code></blockquote>

<b>💡 {translator.get_text(user_id, 'rate_limit_tip')}</b>
<blockquote>• {translator.get_text(user_id, 'slow_down_commands')}
• {translator.get_text(user_id, 'wait_before_retry')}
• {translator.get_text(user_id, 'contact_admin_if_issue')}</blockquote>

<blockquote>🔒 {translator.get_text(user_id, 'anti_spam_protection')}</blockquote>
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
    # Фильтруем только актуальные использования
    recent_uses = [
        timestamp for timestamp in _rate_limits[user_id]
        if current_time - timestamp < 120  # 2 минуты период по умолчанию
    ]
    
    return {
        'current_usage': len(recent_uses),
        'max_limit': 20,
        'period': 120,
        'reset_in': int(120 - (current_time - recent_uses[0])) if recent_uses else 0
    }


# --- Простой Translator (замена modules.lang) ---

class SimpleTranslator:
    """Упрощенный переводчик - возвращает ключ как есть (английский)"""

    def get_text(self, user_id, key):
        """Возвращает текст по ключу (без перевода)"""
        # Словарь с базовыми текстами
        texts = {
            # Общие
            "loading": "Loading...",
            "error": "Error",
            "success": "Success",
            "yes": "Yes",
            "no": "No",
            "unknown": "Unknown",
            "notset": "Not set",
            "seconds": "s",

            # Rate limit
            "rate_limit_exceeded": "Rate Limit Exceeded",
            "limit_reached": "Limit reached",
            "wait_time": "Wait time",
            "current_usage": "Current usage",
            "period": "Period",
            "slow_down_commands": "Slow down with commands",
            "wait_before_retry": "Wait before retrying",
            "contact_admin_if_issue": "Contact admin if issue persists",
            "anti_spam_protection": "Anti-spam protection",
            "uses": "uses",

            # Help
            "nomodulesloaded": "No modules loaded",
            "modules": "Modules",
            "commands": "Commands",
            "prefix": "Prefix",
            "helptitle": "Help",
            "overview": "Overview",
            "mainmodules": "Main Modules",
            "usermodules": "User Modules",
            "quickhelp": "Quick Help",
            "all": "all",
            "modulehelp": "module help",
            "commandhelp": "command help",
            "searchcommands": "search commands",
            "language": "Language",
            "currentlanguagedisplay": "Current language",
            "usecommandforhelp": "Use command for help",
            "poweredby": "Powered by",
            "nomodulesfound": "No modules found",
            "allcommands": "All Commands",
            "total": "Total",
            "completecommandreference": "Complete command reference",
            "module": "Module",
            "notfound": "not found",
            "availablemodules": "Available modules",
            "use": "Use",
            "tosee": "to see",
            "moduledetails": "Module Details",
            "usage": "Usage",
            "try": "Try",
            "command": "Command",
            "navigation": "Navigation",
            "mainmenu": "main menu",
            "documentation": "documentation",
            "and": "and",
            "didyoumean?": "Did you mean?",
            "forcommands": "for commands",
            "notfound": "not found",
            "description": "Description",
            "related": "Related",
            "available": "available",
            "in": "in",
            "multiple": "multiple",
            "no": "No",
            "statistics": "Statistics",
            "core": "Core",
            "usercustom": "User/Custom",
            "top": "Top",
            "popularcommands": "Popular Commands",
            "lastupdated": "Last updated",
            "systemstatistics": "System statistics",
            "found": "Found",
            "results": "results",
            "nosearchresults": "No search results for",
            "tryotherterms": "Try other terms",
            "searchresults": "Search results",
            "foryourquery": "for your query",
            "nousagedatayet": "No usage data yet",
            "commandswillappearhereblockquote": "Commands will appear here",
            "nocommandusagedata": "No command usage data",
            "mostfrequentlyusedcommands": "Most frequently used commands",
            "specifysearchterm": "Specify search term",
            "searchcommandsbynameordescription": "Search commands by name or description",
            "moreresults": "more results",

            # Terminal
            "terminalhelptitle": "Terminal Help",
            "terminalhelpusage": "Usage",
            "terminalhelpexamples": "Examples",
            "terminalhelppermissions": "Permissions",
            "terminalhelpcurrentpath": "Current Path",
            "terminalhelpfeatures": "Features",
            "terminalliveupdates": "Live updates",
            "terminalanimationssupport": "Animations support",
            "terminalansicleanup": "ANSI cleanup",
            "terminallongcommands": "Long commands",
            "terminalhangprotection": "Hang protection",
            "terminaldangerous": "Dangerous command",
            "terminalexecutingcommand": "Executing command",
            "terminalgatheringinfo": "Gathering info...",
            "terminalenvironment": "Terminal environment",
            "terminalshell": "Shell",
            "terminalterminal": "Terminal",
            "terminalhomedirectory": "Home directory",
            "terminalpermissions": "Permissions",
            "terminalavailablecommands": "Available commands",
            "executecommandinterminal": "Execute command in terminal",
            "terminalcurrentdirectory": "Current directory",
            "terminaldirectorycontents": "Directory contents",
            "terminalenvironmentvariables": "Environment variables",
            "terminalfullpath": "Full path",
            "terminaldirectoryinfo": "Directory info",
            "terminalexists": "Exists",
            "terminalwritable": "Writable",
            "terminalreadable": "Readable",
            "terminalquickcommands": "Quick commands",
            "terminaldirectorycontent": "Directory content",
            "path": "Path",
            "terminalscanningdirectory": "Scanning directory...",
            "terminalfolders": "folders",
            "terminalfiles": "files",
            "terminalfolderslist": "Folders List",
            "terminalfileslist": "Files List",
            "bytes": "bytes",
            "terminalemptydirectory": "Empty directory",
            "terminalusefordetails": "Use for details",
            "terminalcleaner": "Terminal Cleaner",
            "status": "Status",
            "terminalclearedstatus": "Cleared",
            "terminalfreedspace": "Freed space",
            "terminaloptimization": "Optimization",
            "terminalcachecleard": "Cache cleared",
            "terminalrecommendations": "Recommendations",
            "terminalclearsession": "Clear session",
            "terminalclearhistory": "Clear history",
            "terminalfullcleanup": "Full cleanup",
            "terminalsymboliccleanup": "Symbolic cleanup",
            "terminalusesystemcommands": "Use system commands",
            "terminalcompleted": "Completed",
            "terminalinprogress": "In progress",
            "terminalupdatescount": "updates",
            "terminallive": "Terminal Live",
            "time": "Time",
            "user": "User",
            "exitcode": "Exit code",
            "stdout": "Output",
            "stderr": "Errors",
            "waitingoutput": "Waiting for output...",
            "terminalresult": "Terminal Result",
            "terminalsuccess": "Success",
            "terminalfailed": "Failed",
            "executiontime": "Execution time",
            "output": "Output",
            "outputtruncated": "Output truncated",
            "errorstruncated": "Errors truncated",
            "nooutput": "No output",
            "terminalcompletedwithcode": "Completed with code",

            # Server Info
            "servertitle": "Server Info",
            "os": "OS",
            "architecture": "Architecture",
            "pythonversion": "Python Version",
            "directory": "Directory",
            "memory": "Memory",
            "notavailable": "Not available",
            "totalmemory": "Total memory",
            "availablememory": "Available memory",
            "usage": "Usage",
            "disk": "Disk",
            "totaldisk": "Total disk",
            "useddisk": "Used disk",
            "freedisk": "Free disk",
            "cpu": "CPU",
            "cores": "Cores",
            "install psutil": "Install psutil",
            "serverhardwareinfo": "Server hardware info",
            "system": "System",
            "info": "Info",
            "platform": "Platform",
            "implementation": "Implementation",
            "current": "Current",
            "hostname": "Hostname",
            "basicsysteminfo": "Basic system info",
            "formoreinfo": "For more info",

            # Start
            "version": "Version",
            "username": "Username",
            "developers": "Developers",
        }

        return texts.get(key, key)

    def get_current_language(self, user_id):
        """Возвращает текущий язык (всегда en)"""
        return "en"

# Создаем глобальный экземпляр translator
translator = SimpleTranslator()
