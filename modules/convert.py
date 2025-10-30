from utils.misc import edit_or_reply
import aiohttp
import json
import os
import re
import random

class AIConverter:
    def __init__(self):
        self.supported_services = {
            "google": {
                "name": "Google Gemini",
                "url": "https://generativelanguage.googleapis.com/v1beta/models/",
                "key_required": True,
                "models": [
                    "gemini-2.0-flash",
                    "gemini-1.5-flash",
                    "gemini-1.5-pro"
                ]
            },
            "openrouter": {
                "name": "OpenRouter",
                "url": "https://openrouter.ai/api/v1/chat/completions",
                "key_required": True,
                "models": [
                    "google/gemini-2.0-flash-exp:free",
                    "google/gemini-flash-1.5:free",
                    "meta-llama/llama-3.3-70b-instruct:free"
                ]
            }
        }
        self.api_keys = {}

    def load_keys(self):
        try:
            if os.path.exists("ai_keys.json"):
                with open("ai_keys.json", "r", encoding='utf-8') as f:
                    self.api_keys = json.load(f)
        except Exception:
            self.api_keys = {}

    def save_keys(self):
        try:
            with open("ai_keys.json", "w", encoding='utf-8') as f:
                json.dump(self.api_keys, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    async def make_ai_request(self, service, source_code, user_request=""):
        try:
            if service not in self.api_keys:
                return f"❌ API ключ не установлен. Используй .set_key {service} <твой_ключ>"

            api_key = self.api_keys[service]

            base_prompt = """КОНВЕРТАЦИЯ ИЗ HIKKA В HYDRA USERBOT!

HIKKA → HYDRA КОНВЕРСИЯ:

1. ИМПОРТЫ:
   HIKKA: from .. import loader, utils
   HYDRA: from utils.misc import edit_or_reply

2. КЛАСС И ДЕКОРАТОРЫ:
   HIKKA: @loader.tds + class KsenonAFKMod(loader.Module)
   HYDRA: НЕТ КЛАССОВ! Только функции

3. КОМАНДЫ:
   HIKKA: @loader.command + async def afk(self, message)
   HYDRA: @command(pattern=".afk") + async def afk_handler(event)

4. ОТВЕТЫ:
   HIKKA: await utils.answer(message, text)
   HYDRA: await edit_or_reply(event, text)

5. БАЗА ДАННЫХ:
   HIKKA: self._db.set/get(name, key, value)
   HYDRA: db.set/get("module_name", key, value)

6. WATCHER:
   HIKKA: async def watcher(self, message)
   HYDRA: @watcher(outgoing=False) + async def watcher_handler(event)

СТРУКТУРА HYDRA:

from utils.misc import edit_or_reply
import asyncio, time, datetime, logging
from collections import defaultdict

# Глобальные переменные
answered_users = set()
chat_messages = defaultdict(list)

# Команды
@command(pattern=".afk")
async def afk_handler(event):
    if not event.out:
        return
    try:
        args = event.pattern_match.group(1)
        db.set("afk", "status", True)
        await edit_or_reply(event, "✅ AFK включен")
    except Exception as e:
        await edit_or_reply(event, f"❌ Ошибка: {e}")

# Watcher
@watcher(outgoing=False)
async def afk_watcher(event):
    if not isinstance(event, types.Message):
        return

modules_help = {
    "afk": [
        {".afk": "Включить AFK"},
        {".unafk": "Выключить AFK"}
    ]
}

ВЕРНИ ТОЛЬКО КОД ДЛЯ HYDRA!"""

            if user_request:
                prompt = f"{base_prompt}\n\nЗАПРОС: {user_request}\n\nКОД HIKKA:\n```python\n{source_code}\n```"
            else:
                prompt = f"{base_prompt}\n\nКОД HIKKA:\n```python\n{source_code}\n```"

            if service == "google":
                models = self.supported_services[service]["models"]
                for model in models:
                    url = f"{self.supported_services[service]['url']}{model}:generateContent?key={api_key}"
                    data = {
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"maxOutputTokens": 8000, "temperature": 0.1}
                    }
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.post(url, json=data, timeout=90) as response:
                                if response.status == 200:
                                    result = await response.json()
                                    return result["candidates"][0]["content"]["parts"][0]["text"]
                    except Exception:
                        continue
                return "❌ Все модели недоступны"

            elif service == "openrouter":
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com",
                    "X-Title": "Hydra Userbot"
                }
                models = self.supported_services[service]["models"]
                for model in models:
                    data = {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 8000,
                        "temperature": 0.1
                    }
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.post(self.supported_services[service]["url"], headers=headers, json=data, timeout=60) as response:
                                if response.status == 200:
                                    result = await response.json()
                                    return result["choices"][0]["message"]["content"]
                    except Exception:
                        continue
                return "❌ Все модели недоступны"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"

    def extract_code(self, response):
        try:
            code_blocks = re.findall(r'```python\s*(.*?)\s*```', response, re.DOTALL)
            if code_blocks:
                return code_blocks[0].strip()
            code_blocks = re.findall(r'```\s*(.*?)\s*```', response, re.DOTALL)
            if code_blocks:
                return code_blocks[0].strip()
            return response.strip()
        except Exception:
            return response

converter = AIConverter()
converter.load_keys()

async def set_key_handler(event):
    try:
        if not event.out:
            return
        args = event.text.split(maxsplit=2)
        if len(args) < 3:
            await edit_or_reply(event, "❌ Использование: .set_key <сервис> <ключ>")
            return
        service = args[1].lower()
        api_key = args[2]
        if service not in converter.supported_services:
            await edit_or_reply(event, f"❌ Сервисы: {', '.join(converter.supported_services.keys())}")
            return
        converter.api_keys[service] = api_key
        converter.save_keys()
        await edit_or_reply(event, f"✅ Ключ для {converter.supported_services[service]['name']} установлен")
    except Exception as e:
        await edit_or_reply(event, f"❌ Ошибка: {str(e)}")

async def show_keys_handler(event):
    try:
        if not event.out:
            return
        if not converter.api_keys:
            await edit_or_reply(event, "❌ Ключи не установлены")
            return
        text = "🔑 Ключи:\n"
        for service, key in converter.api_keys.items():
            text += f"• {converter.supported_services[service]['name']}: `{key[:10]}...`\n"
        await edit_or_reply(event, text)
    except Exception as e:
        await edit_or_reply(event, f"❌ Ошибка: {str(e)}")

async def convert_handler(event):
    try:
        if not event.out:
            return
        reply = await event.get_reply_message()
        if reply and reply.media and reply.file and reply.file.name.endswith('.py'):
            args = event.text.split(maxsplit=1)
            service = "google"
            user_request = "Конвертируй из Hikka в Hydra"
            if len(args) > 1:
                parts = args[1].split(maxsplit=1)
                service = parts[0].lower()
                if len(parts) > 1:
                    user_request = parts[1]
            if service not in converter.supported_services:
                await edit_or_reply(event, f"❌ Сервисы: {', '.join(converter.supported_services.keys())}")
                return
            if service not in converter.api_keys:
                await edit_or_reply(event, f"❌ Установи ключ: .set_key {service} <ключ>")
                return
            await edit_or_reply(event, f"📥 Скачиваю файл...")
            file_path = await reply.download_media()
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            os.remove(file_path)
            await edit_or_reply(event, "🔄 Конвертирую...")
            response = await converter.make_ai_request(service, source_code, user_request)
            if response.startswith("❌"):
                await edit_or_reply(event, response)
                return
            converted_code = converter.extract_code(response)
            if not converted_code.strip():
                await edit_or_reply(event, "❌ Не удалось извлечь код")
                return
            original_filename = reply.file.name
            converted_filename = f"hydra_{original_filename}"
            with open(converted_filename, 'w', encoding='utf-8') as f:
                f.write(converted_code)
            caption = f"✅ Конвертирован\nСервис: {converter.supported_services[service]['name']}\nФайл: {original_filename}"
            if user_request:
                caption += f"\nЗапрос: {user_request}"
            await event.client.send_file(event.chat_id, converted_filename, caption=caption, force_document=True)
            await event.delete()
            os.remove(converted_filename)
        else:
            await edit_or_reply(event, "❌ Ответьте на .py файл")
    except Exception as e:
        await edit_or_reply(event, f"❌ Ошибка: {str(e)}")

async def fix_handler(event):
    try:
        if not event.out:
            return
        reply = await event.get_reply_message()
        if not reply or not reply.media or not reply.file.name.endswith('.py'):
            await edit_or_reply(event, "❌ Ответьте на .py файл")
            return
        args = event.text.split(maxsplit=1)
        user_request = "Исправь ошибки для Hydra"
        if len(args) > 1:
            user_request = args[1]
        service = "google"
        if service not in converter.api_keys:
            await edit_or_reply(event, f"❌ Установи ключ: .set_key {service} <ключ>")
            return
        await edit_or_reply(event, "📥 Скачиваю файл...")
        file_path = await reply.download_media()
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        os.remove(file_path)
        await edit_or_reply(event, "🔧 Исправляю...")
        response = await converter.make_ai_request(service, source_code, user_request)
        if response.startswith("❌"):
            await edit_or_reply(event, response)
            return
        fixed_code = converter.extract_code(response)
        if not fixed_code.strip():
            await edit_or_reply(event, "❌ Не удалось извлечь код")
            return
        original_filename = reply.file.name
        fixed_filename = f"fixed_{original_filename}"
        with open(fixed_filename, 'w', encoding='utf-8') as f:
            f.write(fixed_code)
        await event.client.send_file(event.chat_id, fixed_filename, caption=f"✅ Исправлен\nФайл: {original_filename}", force_document=True)
        await event.delete()
        os.remove(fixed_filename)
    except Exception as e:
        await edit_or_reply(event, f"❌ Ошибка: {str(e)}")

async def services_handler(event):
    try:
        if not event.out:
            return
        text = "🤖 Сервисы:\n"
        for service_id, service_info in converter.supported_services.items():
            has_key = "✅" if service_id in converter.api_keys else "❌"
            text += f"• {service_info['name']} ({service_id}) {has_key}\n"
        text += "\n🔄 Команды:\n.set_key <сервис> <ключ>\n.convert [запрос]\n.fix [запрос]\n.show_keys\n.services"
        await edit_or_reply(event, text)
    except Exception as e:
        await edit_or_reply(event, f"❌ Ошибка: {str(e)}")

modules_help = {
    "ai_converter": {
        "set_key": "<сервис> <ключ> - Установить ключ",
        "show_keys": "Показать ключи",
        "convert": "[запрос] - Конвертировать файл (ответьте)",
        "fix": "[запрос] - Исправить файл (ответьте)",
        "services": "Список сервисов"
    }
}
