from utils.misc import edit_or_reply, fast_animation
from modules.lang import translator
import asyncio
import os

async def terminal_handler(event):
    try:
        args = event.text.split(maxsplit=1)
        if len(args) == 1:
            text = f"""<b>︎︎ ︎ ⁠⁠⁠︎ ︎  ︎︎ ︎ ⁠⁠⁠︎ ︎  ︎︎ ︎ ⁠⁠⁠︎ ︎  ︎︎ ︎ ⁠⁠⁠︎❌ {translator.get_text(event.sender_id, 'error')}</b>

<b>🚫 {translator.get_text(event.sender_id, 'usage')}:</b>
<blockquote expandable><code>.terminal &lt;{translator.get_text(event.sender_id, 'command')}&gt;</code></blockquote>

<b>💡 {translator.get_text(event.sender_id, 'examples')}:</b>
<blockquote expandable><code>.terminal ls -la</code>
<code>.terminal pwd</code></blockquote>

<blockquote expandable>💻 {translator.get_text(event.sender_id, 'execute_system_commands_safely')}</blockquote>"""
            
            await edit_or_reply(event, text, parse_mode='HTML')
            return
        
        loading_msg = await edit_or_reply(event, "💻")
        await fast_animation(loading_msg, "💻", f"💻 {translator.get_text(event.sender_id, 'executing')}...")
        
        cmd = args[1]
        
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        result = f"""<b>︎︎ ︎ ⁠⁠⁠︎ ︎  ︎︎ ︎ ⁠⁠⁠︎ ︎  ︎︎ ︎ ⁠⁠⁠︎ ︎  ︎︎ ︎ ⁠⁠⁠︎💻 {translator.get_text(event.sender_id, 'terminal_title')}</b>

<b>🔧 {translator.get_text(event.sender_id, 'command')}:</b>
<blockquote expandable><code>{cmd}</code></blockquote>

<b>📤 {translator.get_text(event.sender_id, 'exit_code')}:</b> <code>{process.returncode}</code>

"""

        if stdout:
            stdout_text = stdout.decode().strip()
            if len(stdout_text) > 800:
                stdout_text = stdout_text[:800] + "..."
            result += f"""<b>📤 {translator.get_text(event.sender_id, 'stdout')}:</b>
<blockquote expandable><pre>{stdout_text}</pre></blockquote>
"""

        if stderr:
            stderr_text = stderr.decode().strip()
            if len(stderr_text) > 400:
                stderr_text = stderr_text[:400] + "..."
            result += f"""<b>📥 {translator.get_text(event.sender_id, 'stderr')}:</b>
<blockquote expandable><pre>{stderr_text}</pre></blockquote>
"""

        if not stdout and not stderr:
            result += f"<b>✅ {translator.get_text(event.sender_id, 'success_exec')}</b>\n"

        result += f"""\n<blockquote expandable>⚡ {translator.get_text(event.sender_id, 'command_executed')} {translator.get_text(event.sender_id, 'with_exit_code')}: <code>{process.returncode}</code></blockquote>"""
            
        await loading_msg.edit(result, parse_mode='HTML')
        
    except Exception as e:
        await edit_or_reply(event, f"<b>❌ {translator.get_text(event.sender_id, 'error')}:</b> {str(e)}", parse_mode='HTML')

async def term_handler(event):
    await terminal_handler(event)

async def shell_handler(event):
    await terminal_handler(event)

async def exec_handler(event):
    await terminal_handler(event)

modules_help = {
    "terminal": {
        "terminal [command]": "Выполнить команду в терминале",
        "term [command]": "Короткая версия terminal",
        "shell [command]": "Выполнить shell команду",
        "exec [command]": "Выполнить системную команду"
    }
}
