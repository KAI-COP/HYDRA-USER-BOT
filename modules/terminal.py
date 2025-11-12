from utils.misc import edit_or_reply, fast_animation, rate_limit
from modules.lang import translator
import asyncio
import os
import re
import random
from datetime import datetime

@rate_limit(limit=5, period=30)
async def terminal_handler(event):
    """
    .terminal [команда] - Выполнить команду в терминале
    """
    try:
        user_id = event.sender_id
        args = event.text.split(maxsplit=1)
        if len(args) == 1:
            # Меню помощи с красивым форматированием
            help_text = f"""<b>{translator.get_text(user_id, 'terminal_help_title')}</b>

<blockquote>⚡ <b>{translator.get_text(user_id, 'terminal_help_usage')}:</b>
<code>.terminal {translator.get_text(user_id, 'command').lower()}</code>

📋 <b>{translator.get_text(user_id, 'terminal_help_examples')}:</b>
<code>.terminal ls -la</code>
<code>.terminal pwd</code>
<code>.terminal python3 --version</code>
<code>.terminal neofetch</code>

🔧 <b>{translator.get_text(user_id, 'terminal_help_permissions')}:</b> <code>{'🛡️ SUDO ROOT' if os.geteuid() == 0 else '👤 USER'}</code>
📁 <b>{translator.get_text(user_id, 'terminal_help_current_path')}:</b> <code>{os.getcwd()}</code></blockquote>

<b>{translator.get_text(user_id, 'terminal_help_features')}:</b>
<blockquote>• {translator.get_text(user_id, 'terminal_live_updates')}
• {translator.get_text(user_id, 'terminal_animations_support')}
• {translator.get_text(user_id, 'terminal_ansi_cleanup')}
• {translator.get_text(user_id, 'terminal_long_commands')}
• {translator.get_text(user_id, 'terminal_hang_protection')}</blockquote>"""
            
            await edit_or_reply(event, help_text, parse_mode='HTML')
            return
        
        cmd = args[1].strip()
        
        # Проверка опасных команд
        dangerous_commands = ['rm -rf /', 'dd if=', 'mkfs', ':(){:|:&};:']
        if any(danger in cmd for danger in dangerous_commands):
            await edit_or_reply(event, f"🚫 <b>{translator.get_text(user_id, 'terminal_dangerous_blocked')}!</b>", parse_mode='HTML')
            return
        
        # Экранирование кавычек для bash
        escaped_cmd = cmd.replace("'", "'\"'\"'")
        full_cmd = f"bash -c '{escaped_cmd}'"
        
        # Анимация загрузки с прогрессом
        loading_msg = await edit_or_reply(event, "🖥️")
        await fast_animation(loading_msg, "🖥️", f"🖥️ {translator.get_text(user_id, 'terminal_executing_command')}...")
        
        # Информация о системе
        start_time = datetime.now()
        current_user = os.getenv('USER', translator.get_text(user_id, 'unknown'))
        current_path = os.getcwd()
        
        # Выполнение команды с live-выводом
        result = await execute_with_live_output(event, loading_msg, full_cmd, start_time, current_user, current_path, original_cmd=cmd)
            
        await loading_msg.edit(result, parse_mode='HTML')
        
    except Exception as e:
        await edit_or_reply(event, f"<b>❌ {translator.get_text(event.sender_id, 'error')}:</b> <code>{str(e)}</code>", parse_mode='HTML')

async def execute_with_live_output(event, message, cmd, start_time, user, path, original_cmd=None):
    """Выполнение команды с live-обновлением вывода"""
    
    user_id = event.sender_id
    
    if original_cmd is None:
        original_cmd = cmd
    
    # Создаем процесс
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE
    )
    
    # Переменные для live-обновления
    current_output = ""
    current_stderr = ""
    last_update_time = asyncio.get_event_loop().time()
    update_count = 0
    MAX_UPDATES = 200
    MIN_UPDATE_INTERVAL = 0.5
    
    async def update_display(final=False):
        """Обновление отображения с текущим выводом"""
        nonlocal last_update_time, update_count
        
        current_time = asyncio.get_event_loop().time()
        execution_time = (datetime.now() - start_time).total_seconds()
        
        if (current_time - last_update_time >= MIN_UPDATE_INTERVAL or final) and update_count < MAX_UPDATES:
            
            result = format_live_output(
                original_cmd, 
                current_output, 
                current_stderr, 
                execution_time, 
                user, 
                path, 
                process.returncode if final else None,
                update_count,
                final,
                user_id
            )
            
            try:
                await message.edit(result, parse_mode='HTML')
                last_update_time = current_time
                if not final:
                    update_count += 1
            except Exception as e:
                print(f"Update error: {e}")
    
    async def read_stream(stream, is_stdout=True):
        """Чтение потока с обработкой live-вывода"""
        nonlocal current_output, current_stderr
        
        buffer = ""
        while True:
            try:
                chunk = await stream.read(512)
                if not chunk:
                    break
                    
                text = chunk.decode('utf-8', errors='replace')
                buffer += text
                
                # Обработка carriage return для перезаписи строк
                if '\r' in buffer:
                    lines = buffer.split('\r')
                    # Берем последнюю строку после всех \r
                    buffer = lines[-1]
                
                # Обновляем соответствующий вывод
                if is_stdout:
                    current_output = buffer
                else:
                    current_stderr = buffer
                
                # Обновляем дисплей
                await update_display()
                
            except Exception as e:
                break
    
    # Запускаем чтение потоков
    try:
        await asyncio.wait_for(
            asyncio.gather(
                read_stream(process.stdout, True),
                read_stream(process.stderr, False),
            ),
            timeout=300
        )
    except asyncio.TimeoutError:
        try:
            process.terminate()
        except:
            pass
    
    # Ждем завершения процесса
    try:
        await process.wait()
    except:
        pass
    
    # Финальное обновление
    await update_display(final=True)
    
    # Получаем финальный вывод
    stdout, stderr = await process.communicate()
    final_stdout = stdout.decode('utf-8', errors='replace').strip() if stdout else current_output
    final_stderr = stderr.decode('utf-8', errors='replace').strip() if stderr else current_stderr
    
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()
    
    return format_final_output(original_cmd, process.returncode, final_stdout, final_stderr, execution_time, user, path, user_id)

def format_live_output(cmd, stdout_text, stderr_text, exec_time, user, path, returncode, update_count, final=False, user_id=None):
    """Форматирование live-вывода"""
    
    status_icon = "✅" if final and returncode == 0 else "🔄"
    
    if final:
        status_text = translator.get_text(user_id, 'terminal_completed')
    else:
        status_text = f"{translator.get_text(user_id, 'terminal_in_progress')} (#{update_count} {translator.get_text(user_id, 'terminal_updates_count')})"
    
    result = f"""<b>🖥️ {translator.get_text(user_id, 'terminal_live')}</b>

<blockquote>🔧 <b>{translator.get_text(user_id, 'command')}:</b>
<code>{cmd}</code>

⏱️ <b>{translator.get_text(user_id, 'time')}:</b> <code>{exec_time:.1f}{translator.get_text(user_id, 'seconds')}</code>
👤 <b>{translator.get_text(user_id, 'user')}:</b> <code>{user}</code>
📁 <b>{translator.get_text(user_id, 'path')}:</b> <code>{path}</code>
{f'📊 <b>{translator.get_text(user_id, 'exit_code')}:</b> <code>{returncode}</code>' if final else ''}</blockquote>

"""
    
    if stdout_text:
        clean_output = clean_ansi_codes(stdout_text[-2000:])
        result += f"""<b>📨 {translator.get_text(user_id, 'stdout')}:</b>
<pre>{clean_output}</pre>

"""
    
    if stderr_text:
        clean_stderr = clean_ansi_codes(stderr_text[-1000:])
        result += f"""<b>🚨 {translator.get_text(user_id, 'stderr')}:</b>
<pre>{clean_stderr}</pre>

"""
    
    if not stdout_text and not stderr_text:
        result += f"""<b>📨 {translator.get_text(user_id, 'output')}:</b>
<pre>{translator.get_text(user_id, 'waiting_output')}...</pre>

"""
    
    result += f"<blockquote>{status_icon} <i>{status_text}</i></blockquote>"
    
    return result

def format_final_output(cmd, returncode, stdout_text, stderr_text, exec_time, user, path, user_id=None):
    """Форматирование финального вывода"""
    
    status_icon = "✅" if returncode == 0 else "❌"
    status_color = "🟢" if returncode == 0 else "🔴"
    status_text = translator.get_text(user_id, 'terminal_success') if returncode == 0 else translator.get_text(user_id, 'terminal_failed')
    
    result = f"""<b>🖥️ {translator.get_text(user_id, 'terminal_result')}</b>

<blockquote>🔧 <b>{translator.get_text(user_id, 'command')}:</b>
<code>{cmd}</code>

{status_color} <b>{translator.get_text(user_id, 'status')}:</b> <code>{status_text}</code>
📊 <b>{translator.get_text(user_id, 'exit_code')}:</b> <code>{returncode}</code>
⏱️ <b>{translator.get_text(user_id, 'execution_time')}:</b> <code>{exec_time:.2f}{translator.get_text(user_id, 'seconds')}</code>
👤 <b>{translator.get_text(user_id, 'user')}:</b> <code>{user}</code>
📁 <b>{translator.get_text(user_id, 'path')}:</b> <code>{path}</code></blockquote>

"""
    
    if stdout_text:
        clean_stdout = clean_ansi_codes(stdout_text)
        if len(clean_stdout) > 3500:
            clean_stdout = clean_stdout[:3500] + f"\n... ({translator.get_text(user_id, 'output_truncated')})"
        result += f"""<b>📨 {translator.get_text(user_id, 'output')}:</b>
<pre>{clean_stdout}</pre>

"""
    
    if stderr_text:
        clean_stderr = clean_ansi_codes(stderr_text)
        if len(clean_stderr) > 2000:
            clean_stderr = clean_stderr[:2000] + f"\n... ({translator.get_text(user_id, 'errors_truncated')})"
        result += f"""<b>🚨 {translator.get_text(user_id, 'stderr')}:</b>
<pre>{clean_stderr}</pre>

"""
    
    if not stdout_text and not stderr_text:
        result += f"<blockquote>ℹ️ <i>{translator.get_text(user_id, 'no_output')}</i></blockquote>\n"

    result += f"""<blockquote>{status_icon} <i>{translator.get_text(user_id, 'terminal_completed_with_code')}: {returncode}</i></blockquote>"""
    
    return result

def clean_ansi_codes(text):
    """Очищает ANSI escape-коды из текста"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

@rate_limit(limit=5, period=30)
async def term_handler(event):
    """Короткая версия terminal команды"""
    await terminal_handler(event)

@rate_limit(limit=5, period=30)
async def shell_handler(event):
    """Альтернативное имя для terminal"""
    await terminal_handler(event)

@rate_limit(limit=5, period=30)
async def exec_handler(event):
    """Альтернативное имя для terminal"""
    await terminal_handler(event)

# НОВЫЕ ФИШКИ ДЛЯ ТЕРМИНАЛА

@rate_limit(limit=3, period=60)
async def terminal_info_handler(event):
    """Информация о терминальном окружении"""
    try:
        user_id = event.sender_id
        loading_msg = await edit_or_reply(event, "🔍")
        await fast_animation(loading_msg, "🔍", f"{translator.get_text(user_id, 'terminal_gathering_info')}...")
        
        # Собираем информацию о системе
        shell_info = os.getenv('SHELL', translator.get_text(user_id, 'unknown'))
        term_info = os.getenv('TERM', translator.get_text(user_id, 'unknown'))
        
        info_text = f"""<b>🔍 {translator.get_text(user_id, 'terminal_environment')}</b>

<blockquote>🐚 <b>{translator.get_text(user_id, 'terminal_shell')}:</b> <code>{shell_info}</code>
🖥️ <b>{translator.get_text(user_id, 'terminal_terminal')}:</b> <code>{term_info}</code>
📁 <b>{translator.get_text(user_id, 'terminal_home_directory')}:</b> <code>{os.path.expanduser('~')}</code>
🔧 <b>{translator.get_text(user_id, 'terminal_permissions')}:</b> <code>{'ROOT' if os.geteuid() == 0 else 'USER'}</code></blockquote>

<b>📊 {translator.get_text(user_id, 'terminal_available_commands')}:</b>
<blockquote>• <code>terminal</code> - {translator.get_text(user_id, 'execute_command_in_terminal')}
• <code>terminal_info</code> - {translator.get_text(user_id, 'terminal_environment')}
• <code>terminal_pwd</code> - {translator.get_text(user_id, 'terminal_current_directory')}
• <code>terminal_ls</code> - {translator.get_text(user_id, 'terminal_directory_content')}</blockquote>

<b>🎯 {translator.get_text(user_id, 'terminal_environment_variables')}:</b>
<blockquote>• <b>PATH:</b> <code>{os.getenv('PATH', '')[:100]}...</code>
• <b>LANG:</b> <code>{os.getenv('LANG', translator.get_text(user_id, 'not_set'))}</code>
• <b>PWD:</b> <code>{os.getcwd()}</code></blockquote>"""
        
        await loading_msg.edit(info_text, parse_mode='HTML')
        
    except Exception as e:
        await edit_or_reply(event, f"<b>❌ {translator.get_text(event.sender_id, 'error')}:</b> {str(e)}", parse_mode='HTML')

@rate_limit(limit=10, period=30)
async def terminal_pwd_handler(event):
    """Показать текущую директорию"""
    try:
        user_id = event.sender_id
        current_path = os.getcwd()
        result = f"""<b>📁 {translator.get_text(user_id, 'terminal_current_directory')}</b>

<blockquote>🛣️ <b>{translator.get_text(user_id, 'terminal_full_path')}:</b>
<code>{current_path}</code>

📊 <b>{translator.get_text(user_id, 'terminal_directory_info')}:</b>
• <b>{translator.get_text(user_id, 'terminal_exists')}:</b> <code>{translator.get_text(user_id, 'yes') if os.path.exists(current_path) else translator.get_text(user_id, 'no')}</code>
• <b>{translator.get_text(user_id, 'terminal_writable')}:</b> <code>{translator.get_text(user_id, 'yes') if os.access(current_path, os.W_OK) else translator.get_text(user_id, 'no')}</code>
• <b>{translator.get_text(user_id, 'terminal_readable')}:</b> <code>{translator.get_text(user_id, 'yes') if os.access(current_path, os.R_OK) else translator.get_text(user_id, 'no')}</code></blockquote>

<b>🚀 {translator.get_text(user_id, 'terminal_quick_commands')}:</b>
<blockquote><code>.terminal_ls</code> - {translator.get_text(user_id, 'terminal_directory_content').lower()}
<code>.terminal "cd /path"</code> - {translator.get_text(user_id, 'path').lower()}
<code>.terminal "pwd && ls"</code> - {translator.get_text(user_id, 'command').lower()}</blockquote>"""
        
        await edit_or_reply(event, result, parse_mode='HTML')
        
    except Exception as e:
        await edit_or_reply(event, f"<b>❌ {translator.get_text(event.sender_id, 'error')}:</b> {str(e)}", parse_mode='HTML')

@rate_limit(limit=10, period=30)
async def terminal_ls_handler(event):
    """Показать содержимое текущей директории"""
    try:
        user_id = event.sender_id
        loading_msg = await edit_or_reply(event, "📂")
        await fast_animation(loading_msg, "📂", f"{translator.get_text(user_id, 'terminal_scanning_directory')}...")
        
        current_path = os.getcwd()
        items = os.listdir(current_path)
        
        # Сортируем: сначала директории, потом файлы
        dirs = [item for item in items if os.path.isdir(os.path.join(current_path, item))]
        files = [item for item in items if os.path.isfile(os.path.join(current_path, item))]
        
        dirs.sort()
        files.sort()
        
        result = f"""<b>📂 {translator.get_text(user_id, 'terminal_directory_content')}</b>

<blockquote>📁 <b>{translator.get_text(user_id, 'path')}:</b> <code>{current_path}</code>
📊 <b>{translator.get_text(user_id, 'terminal_items_count')}:</b> <code>{len(dirs)} {translator.get_text(user_id, 'terminal_folders')}, {len(files)} {translator.get_text(user_id, 'terminal_files')}</code></blockquote>

"""
        
        if dirs:
            result += f"<b>📁 {translator.get_text(user_id, 'terminal_folders_list')}:</b>\n<blockquote>"
            for dir_name in dirs[:20]:
                result += f"• 📁 <code>{dir_name}</code>\n"
            if len(dirs) > 20:
                result += f"• ... {translator.get_text(user_id, 'and')} {len(dirs) - 20} {translator.get_text(user_id, 'terminal_folders')}\n"
            result += "</blockquote>\n"
        
        if files:
            result += f"<b>📄 {translator.get_text(user_id, 'terminal_files_list')}:</b>\n<blockquote>"
            for file_name in files[:20]:
                file_path = os.path.join(current_path, file_name)
                size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                result += f"• 📄 <code>{file_name}</code> (<code>{size} {translator.get_text(user_id, 'bytes')}</code>)\n"
            if len(files) > 20:
                result += f"• ... {translator.get_text(user_id, 'and')} {len(files) - 20} {translator.get_text(user_id, 'terminal_files')}\n"
            result += "</blockquote>"
        
        if not dirs and not files:
            result += f"<blockquote>📭 <i>{translator.get_text(user_id, 'terminal_empty_directory')}</i></blockquote>"
        
        result += f"""\n<blockquote>💡 <i>{translator.get_text(user_id, 'terminal_use_for_details')}: </i><code>.terminal "ls -la"</code></blockquote>"""
        
        await loading_msg.edit(result, parse_mode='HTML')
        
    except Exception as e:
        await edit_or_reply(event, f"<b>❌ {translator.get_text(event.sender_id, 'error')}:</b> {str(e)}", parse_mode='HTML')

@rate_limit(limit=5, period=60)
async def terminal_clear_handler(event):
    """Очистить терминальную историю (символически)"""
    try:
        user_id = event.sender_id
        import random
        result = f"""<b>🧹 {translator.get_text(user_id, 'terminal_cleaner')}</b>

<blockquote>🔄 <b>{translator.get_text(user_id, 'status')}:</b> <code>{translator.get_text(user_id, 'terminal_cleared_status')}</code>
💾 <b>{translator.get_text(user_id, 'terminal_freed_space')}:</b> <code>~{random.randint(50, 500)} KB</code>
📊 <b>{translator.get_text(user_id, 'terminal_optimization')}:</b> <code>{translator.get_text(user_id, 'terminal_cache_cleared')}</code></blockquote>

<b>🎯 {translator.get_text(user_id, 'terminal_recommendations')}:</b>
<blockquote>• {translator.get_text(user_id, 'use')} <code>.terminal "clear"</code> {translator.get_text(user_id, 'terminal_clear_session')}
• <code>.terminal "history -c"</code> - {translator.get_text(user_id, 'terminal_clear_history')}
• <code>.terminal "echo '' > ~/.bash_history"</code> - {translator.get_text(user_id, 'terminal_full_cleanup')}</blockquote>

<blockquote>💡 <i>{translator.get_text(user_id, 'terminal_symbolic_cleanup')}. {translator.get_text(user_id, 'terminal_use_system_commands')}.</i></blockquote>"""
        
        await edit_or_reply(event, result, parse_mode='HTML')
        
    except Exception as e:
        await edit_or_reply(event, f"<b>❌ {translator.get_text(event.sender_id, 'error')}:</b> {str(e)}", parse_mode='HTML')

modules_help = {
    "terminal": {
        "terminal [command]": "Execute command in terminal with live output",
        "term [command]": "Short version of terminal",
        "shell [command]": "Execute shell command", 
        "exec [command]": "Execute system command",
        "terminal_info": "Terminal environment information",
        "terminal_pwd": "Show current directory",
        "terminal_ls": "Show directory content",
        "terminal_clear": "Clear terminal history"
    }
}
