"""
🚀 ModuleHub - Инновационный загрузчик модулей нового поколения
"""

import aiohttp
import ast
import importlib.util
import logging
import os
import re
import sys
import time
import asyncio
import hashlib
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from utils.misc import edit_or_reply, rate_limit
from telethon import events

logger = logging.getLogger(__name__)

MODULES_DIR = Path("modules")
BACKUP_DIR = Path("modules/.backups")
METADATA_FILE = Path("modules/.metadata.json")

loaded_modules = {}
module_metadata = {}
module_stats = {"total_installed": 0, "successful": 0, "failed": 0}

def load_metadata():
    global module_metadata
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                module_metadata = json.load(f)
        except:
            module_metadata = {}
    else:
        module_metadata = {}

def save_metadata():
    METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(module_metadata, f, indent=2, ensure_ascii=False)

class ModuleAnalyzer:
    @staticmethod
    def analyze(code, url=""):
        analysis = {
            "safe": True, "type": "unknown", "name": None,
            "version": "1.0.0", "author": "Unknown", "description": "",
            "commands": [], "dependencies": [], "warnings": [],
            "errors": [], "score": 100, "features": []
        }

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            analysis["safe"] = False
            analysis["errors"].append(f"Syntax: {e}")
            analysis["score"] = 0
            return analysis

        imports, functions, classes = set(), [], []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
            elif isinstance(node, ast.FunctionDef):
                functions.append(node.name)
                if node.name.endswith('_handler'):
                    analysis["commands"].append(node.name[:-8])
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

        code_lower = code.lower()
        if 'hikka' in code_lower:
            analysis["type"] = "hikka"
        elif 'ftg' in code_lower or 'friendly' in code_lower:
            analysis["type"] = "ftg"
        elif '_handler' in code:
            analysis["type"] = "native"
        else:
            analysis["type"] = "custom"

        match = re.search(r'modules_help\s*=\s*\{\s*["\']([^"\']+)["\']', code)
        if match:
            analysis["name"] = match.group(1)
        elif analysis["commands"]:
            analysis["name"] = analysis["commands"][0]
        elif url:
            analysis["name"] = os.path.basename(urlparse(url).path).replace('.py', '')
        else:
            analysis["name"] = f"module_{int(time.time())}"

        for pattern in [r'__version__\s*=\s*["\']([^"\']+)["\']',
                       r'version\s*=\s*["\']([^"\']+)["\']']:
            match = re.search(pattern, code)
            if match:
                analysis["version"] = match.group(1)
                break

        for pattern in [r'__author__\s*=\s*["\']([^"\']+)["\']',
                       r'author\s*=\s*["\']([^"\']+)["\']']:
            match = re.search(pattern, code)
            if match:
                analysis["author"] = match.group(1)
                break

        analysis["description"] = code[:200].replace('\n', ' ').strip()

        for match in re.finditer(r'#\s*requires?:\s*(.+)', code, re.I):
            deps = [d.strip() for d in re.split(r'[,\s]+', match.group(1)) if d.strip()]
            analysis["dependencies"].extend(deps)
        analysis["dependencies"] = list(set(analysis["dependencies"]))

        dangerous = {'subprocess': 15, 'os': 10, 'shutil': 10, 'pickle': 20}
        for imp in imports:
            if imp in dangerous:
                analysis["score"] -= dangerous[imp]
                analysis["warnings"].append(f"⚠️ {imp}")

        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ['eval', 'exec']:
                    analysis["score"] -= 25
                    analysis["warnings"].append(f"⚠️ {node.func.id}()")

        if analysis["score"] < 50:
            analysis["safe"] = False

        if 'async def' in code:
            analysis["features"].append("⚡Async")
        if analysis["commands"]:
            analysis["features"].append("🎮Commands")
        if 'aiohttp' in code:
            analysis["features"].append("🌐Network")

        return analysis

async def install_dependencies(deps, msg=None):
    if not deps:
        return {"success": True, "installed": [], "failed": []}

    installed, failed = [], []
    for dep in deps:
        try:
            if msg:
                await msg.edit(f"📦 Installing: `{dep}`...")

            proc = await asyncio.create_subprocess_exec(
                sys.executable, '-m', 'pip', 'install', '-q', dep,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await asyncio.wait_for(proc.communicate(), timeout=60)

            if proc.returncode == 0:
                installed.append(dep)
            else:
                failed.append(dep)
        except:
            failed.append(dep)

    return {"success": len(failed) == 0, "installed": installed, "failed": failed}

async def download_module(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                if resp.status == 200:
                    return {"success": True, "code": await resp.text(), "url": url}
                return {"success": False, "error": f"HTTP {resp.status}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def load_module_dynamic(module_name, file_path, client):
    try:
        from config import prefix

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"modules.{module_name}"] = module
        spec.loader.exec_module(module)
        module.client = client

        handlers = 0
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if callable(attr) and asyncio.iscoroutinefunction(attr):
                if attr_name.endswith('_handler'):
                    cmd = attr_name[:-8]
                    pattern = rf'^{re.escape(prefix)}{cmd}(?:\s|$)'

                    @client.on(events.NewMessage(pattern=pattern, outgoing=True))
                    async def handler(event, func=attr):
                        await func(event)

                    handlers += 1

        if hasattr(module, 'modules_help'):
            from utils.loader import modules_help as mh
            if isinstance(module.modules_help, dict):
                for mod, cmds in module.modules_help.items():
                    if mod not in mh:
                        mh[mod] = {}
                    mh[mod].update(cmds)

        loaded_modules[module_name] = {
            "module": module, "path": str(file_path),
            "handlers": handlers, "loaded_at": time.time()
        }

        return {"success": True, "handlers": handlers}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def install_module(code, url="", msg=None, client=None):
    try:
        if msg:
            await msg.edit("🔍 Analyzing...")

        analysis = ModuleAnalyzer.analyze(code, url)

        if not analysis["safe"]:
            return {"success": False, "error": "Security check failed", "analysis": analysis}

        if analysis["dependencies"]:
            if msg:
                await msg.edit(f"📦 Installing dependencies...")
            dep_result = await install_dependencies(analysis["dependencies"], msg)
            if not dep_result["success"]:
                return {"success": False, "error": f"Deps failed: {', '.join(dep_result['failed'])}", "analysis": analysis}

        MODULES_DIR.mkdir(exist_ok=True)
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        module_name = analysis["name"]
        module_path = MODULES_DIR / f"{module_name}.py"

        if module_path.exists():
            backup = BACKUP_DIR / f"{module_name}_{int(time.time())}.py"
            module_path.rename(backup)

        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(code)

        if msg:
            await msg.edit("⚡ Loading...")

        load_result = await load_module_dynamic(module_name, module_path, client)

        if not load_result["success"]:
            return {"success": False, "error": load_result["error"], "analysis": analysis}

        module_metadata[module_name] = {
            "installed_at": datetime.now().isoformat(),
            "version": analysis["version"],
            "author": analysis["author"],
            "type": analysis["type"],
            "commands": analysis["commands"],
            "score": analysis["score"],
            "hash": hashlib.md5(code.encode()).hexdigest(),
            "url": url,
            "usage_count": 0
        }
        save_metadata()

        module_stats["total_installed"] += 1
        module_stats["successful"] += 1

        return {
            "success": True,
            "module_name": module_name,
            "analysis": analysis,
            "handlers": load_result["handlers"]
        }
    except Exception as e:
        module_stats["failed"] += 1
        return {"success": False, "error": str(e), "analysis": None}

@rate_limit(limit=5, period=60)
async def mhub_handler(event):
    try:
        args = event.text.split(maxsplit=1)
        reply = await event.get_reply_message()
        code, url = None, None

        if len(args) >= 2:
            url = args[1]
        elif reply:
            if reply.document:
                for attr in reply.document.attributes:
                    if hasattr(attr, 'file_name') and attr.file_name.endswith('.py'):
                        msg = await edit_or_reply(event, "📥 Downloading...")
                        path = await reply.download_media()
                        with open(path, 'r', encoding='utf-8') as f:
                            code = f.read()
                        os.remove(path)
                        break
                else:
                    await edit_or_reply(event, "❌ Must be .py file")
                    return
            elif reply.text:
                text = reply.text.strip()
                if text.startswith(('http://', 'https://')):
                    url = text
                else:
                    code = text
        else:
            await edit_or_reply(event, """**🚀 ModuleHub**

**Usage:**
`.mhub <URL>` - install from URL
`.mhub` (reply) - install from msg/file

**Features:**
🔍 AI analysis
🛡️ Security scoring
📦 Auto dependencies
⚡ Hot-reload

**Examples:**
`.mhub https://example.com/mod.py`
`.mhub` - reply to code/file""")
            return

        msg = await edit_or_reply(event, "🚀 Starting...")

        if url and not code:
            await msg.edit(f"📡 Downloading...")
            dl = await download_module(url)
            if not dl["success"]:
                await msg.edit(f"❌ Download failed: {dl['error']}")
                return
            code = dl["code"]

        result = await install_module(code, url or "", msg, event.client)

        if not result["success"]:
            error = f"❌ **Failed**\n\n{result['error']}"
            if result.get("analysis"):
                a = result["analysis"]
                error += f"\n\n🛡️ Score: {a['score']}/100"
            await msg.edit(error)
            return

        a = result["analysis"]
        text = f"""✅ **Module Installed!**

📦 `{result['module_name']}`
📌 v{a['version']} by {a['author']}
🔖 Type: `{a['type']}`
⚡ Commands: `{len(a['commands'])}`"""

        if a['commands']:
            text += "\n📝 Available:\n"
            for cmd in a['commands'][:5]:
                text += f"  • `.{cmd}`\n"

        text += f"\n🛡️ Security: `{a['score']}/100`"

        if a['features']:
            text += f"\n✨ {' '.join(a['features'][:3])}"

        if a['warnings']:
            text += f"\n⚠️ Warnings: {len(a['warnings'])}"

        text += "\n\n🚀 Ready!"

        await msg.edit(text)
    except Exception as e:
        await edit_or_reply(event, f"❌ Error: {e}")

@rate_limit(limit=10, period=60)
async def minfo_handler(event):
    try:
        args = event.text.split()
        load_metadata()

        if len(args) < 2:
            if not module_metadata:
                await edit_or_reply(event, "ℹ️ No modules installed")
                return

            text = f"**📊 Installed ({len(module_metadata)})**\n\n"
            for name, meta in sorted(module_metadata.items(), key=lambda x: x[1]['installed_at'], reverse=True)[:10]:
                text += f"📦 `{name}` v{meta['version']}\n"
                text += f"   🛡️ {meta['score']}/100 | 🎮 {len(meta['commands'])} cmds\n"

            text += "\n💡 `.minfo <name>` for details"
            await edit_or_reply(event, text)
            return

        name = args[1]
        if name not in module_metadata:
            await edit_or_reply(event, f"❌ `{name}` not found")
            return

        m = module_metadata[name]
        text = f"""**📊 {name}**

📌 v{m['version']} by {m['author']}
🔖 Type: `{m['type']}`
🛡️ Score: `{m['score']}/100`
⚡ Commands: `{len(m['commands'])}`"""

        if m['commands']:
            text += "\n📝 "
            for cmd in m['commands'][:5]:
                text += f"`.{cmd}` "

        text += f"\n\n📅 Installed: `{m['installed_at'][:10]}`"
        text += f"\n📊 Usage: `{m['usage_count']}`"

        await edit_or_reply(event, text)
    except Exception as e:
        await edit_or_reply(event, f"❌ {e}")

@rate_limit(limit=5, period=60)
async def mremove_handler(event):
    try:
        args = event.text.split()
        if len(args) < 2:
            await edit_or_reply(event, "Usage: `.mremove <module>`")
            return

        name = args[1]
        load_metadata()

        if name not in module_metadata:
            await edit_or_reply(event, f"❌ `{name}` not found")
            return

        path = MODULES_DIR / f"{name}.py"
        if path.exists():
            path.unlink()

        if f"modules.{name}" in sys.modules:
            del sys.modules[f"modules.{name}"]

        del module_metadata[name]
        save_metadata()

        if name in loaded_modules:
            del loaded_modules[name]

        await edit_or_reply(event, f"✅ `{name}` removed\n⚠️ Restart for full cleanup")
    except Exception as e:
        await edit_or_reply(event, f"❌ {e}")

@rate_limit(limit=3, period=30)
async def mstats_handler(event):
    try:
        load_metadata()

        text = f"""**📈 ModuleHub Stats**

📦 Modules: `{len(module_metadata)}`
✅ Success: `{module_stats['successful']}`
❌ Failed: `{module_stats['failed']}`"""

        if module_metadata:
            avg = sum(m['score'] for m in module_metadata.values()) // len(module_metadata)
            text += f"\n🛡️ Avg Score: `{avg}/100`"

        await edit_or_reply(event, text)
    except Exception as e:
        await edit_or_reply(event, f"❌ {e}")

load_metadata()

modules_help = {
    "modulehub": {
        "mhub <url>": "🚀 Install module (AI analysis, auto-deps)",
        "minfo [name]": "📊 Module info / list",
        "mremove <name>": "🗑️ Remove module",
        "mstats": "📈 Statistics"
    }
}
