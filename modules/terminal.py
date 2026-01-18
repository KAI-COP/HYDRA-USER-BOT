from utils.misc import edit_or_reply, fast_animation, rate_limit
import asyncio
import os
import re
import platform
from datetime import datetime

def get_permissions_label():
    """Проверка прав администратора/root (кроссплатформенная)"""
    try:
        if platform.system() == "Windows":
            import ctypes
            return "🛡️ ADMIN" if ctypes.windll.shell32.IsUserAnAdmin() != 0 else "👤 USER"
        else:
            return "🛡️ ROOT" if os.geteuid() == 0 else "👤 USER"
    except AttributeError:
        return "👤 USER"

@rate_limit(limit=5, period=30)
async def terminal_handler(event):
    """
    .terminal [команда] - Выполнить команду в терминале
    """
    try:
        args = event.text.split(maxsplit=1)
        if len(args) == 1:
            help_text = f"""<b>Terminal Help</b>

<blockquote>⚡ <b>Usage:</b>
<code>.terminal command</code>

📋 <b>Examples:</b>
<code>.terminal ls -la</code>
<code>.terminal pwd</code>
<code>.terminal python3 --version</code>

🔧 <b>Permissions:</b> <code>{get_permissions_label()}</code>
📁 <b>Current Path:</b> <code>{os.getcwd()}</code></blockquote>

<b>Features:</b>
<blockquote>• Live updates
• Animations support
• ANSI cleanup
• Long commands
• Hang protection</blockquote>"""
            
            await edit_or_reply(event, help_text, parse_mode='HTML')
            return
        
        cmd = args[1].strip()
        
        # Проверка опасных команд
        dangerous_commands = ['rm -rf /', 'dd if=', 'mkfs', ':(){:|:&};:']
        if any(danger in cmd for danger in dangerous_commands):
            await edit_or_reply(event, "🚫 <b>Dangerous command blocked!</b>", parse_mode='HTML')
            return
        
        # Выбор оболочки в зависимости от ОС
        is_windows = platform.system() == "Windows"
        if is_windows:
            full_cmd = f"cmd /c {cmd}"
        else:
            escaped_cmd = cmd.replace("'", "'\"'\"'")
            full_cmd = f"bash -c '{escaped_cmd}'"
        
        loading_msg = await edit_or_reply(event, "🖥️")
        await fast_animation(loading_msg, "🖥️", "🖥️ Executing command...")
        
        start_time = datetime.now()
        current_user = os.getenv('USERNAME' if is_windows else 'USER', 'unknown')
        current_path = os.getcwd()
        
        result = await execute_with_live_output(event, loading_msg, full_cmd, start_time, current_user, current_path, original_cmd=cmd)
            
        await loading_msg.edit(result, parse_mode='HTML')
        
    except Exception as e:
        await edit_or_reply(event, f"<b>❌ Error:</b> <code>{str(e)}</code>", parse_mode='HTML')

async def execute_with_live_output(event, message, cmd, start_time, user, path, original_cmd=None):
    if original_cmd is None:
        original_cmd = cmd
    
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    current_output = ""
    current_stderr = ""
    last_update_time = asyncio.get_event_loop().time()
    update_count = 0
    
    async def update_display(final=False):
        nonlocal last_update_time, update_count
        current_time = asyncio.get_event_loop().time()
        exec_time = (datetime.now() - start_time).total_seconds()

        if (current_time - last_update_time >= 0.5 or final) and update_count < 100:
            result = format_output_ui(original_cmd, current_output, current_stderr, exec_time, user, path, 
                                     process.returncode if final else None, update_count, final)
            try:
                await message.edit(result, parse_mode='HTML')
                last_update_time = current_time
                if not final:
                    update_count += 1
            except:
                pass
    
    async def read_stream(stream, is_stdout=True):
        nonlocal current_output, current_stderr
        while True:
            chunk = await stream.read(1024)
            if not chunk: break
            text = chunk.decode('utf-8', errors='replace')
            if is_stdout: current_output += text
            else: current_stderr += text
            await update_display()

    try:
        await asyncio.wait_for(asyncio.gather(
            read_stream(process.stdout, True),
            read_stream(process.stderr, False)
        ), timeout=300)
    except asyncio.TimeoutError:
        try: process.terminate()
        except: pass
    
    await process.wait()
    await update_display(final=True)
    return format_output_ui(original_cmd, current_output, current_stderr, 
                           (datetime.now() - start_time).total_seconds(), 
                           user, path, process.returncode, update_count, True)

def format_output_ui(cmd, out, err, exec_time, user, path, code, updates, final):
    icon = "✅" if final and code == 0 else ("❌" if final else "🔄")
    status = "Completed" if final else f"In progress ({updates} updates)"
    
    res = f"<b>🖥️ Terminal {'Result' if final else 'Live'}</b>\n"
    res += f"<blockquote>🔧 <b>Command:</b> <code>{cmd}</code>\n"
    res += f"⏱️ <b>Time:</b> <code>{exec_time:.1f}s</code>\n"
    res += f"👤 <b>User:</b> <code>{user}</code>\n"
    if code is not None: res += f"📊 <b>Exit code:</b> <code>{code}</code>\n"
    res += "</blockquote>\n\n"
    
    if out:
        clean_out = clean_ansi_codes(out[-3000:])
        res += f"<b>📨 Output:</b>\n<pre>{clean_out}</pre>\n\n"
    if err:
        clean_err = clean_ansi_codes(err[-1000:])
        res += f"<b>🚨 Errors:</b>\n<pre>{clean_err}</pre>\n\n"
        
    res += f"<blockquote>{icon} <i>{status}</i></blockquote>"
    return res

def clean_ansi_codes(text):
    return re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])').sub('', text)