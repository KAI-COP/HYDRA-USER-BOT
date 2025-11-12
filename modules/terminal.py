from utils.misc import edit_or_reply, rate_limit
import asyncio
import time

@rate_limit(limit=5, period=60)
async def terminal_handler(event):
    """
    .terminal [команда] - Выполнить команду в терминале
    """
    try:
        args = event.text.split(maxsplit=1)
        if len(args) == 1:
            help_text = f"""<b>🖥️ Terminal</b>

<blockquote>⚡ <b>Использование:</b>
<code>.terminal команда</code>

📋 <b>Примеры:</b>
<code>.terminal ls -la</code>
<code>.terminal pwd</code>
<code>.terminal python3 --version</code></blockquote>

<blockquote>🎯 <i>Умное обновление: интервалы 0.4-5 сек</i>
<i>Не рекомендуем использовать быстрые анимации</i></blockquote>"""
            
            await edit_or_reply(event, help_text, parse_mode='HTML')
            return
        
        cmd = args[1].strip()
        
        # Проверка опасных команд
        dangerous_commands = ['rm -rf /', 'dd if=', 'mkfs', ':(){:|:&};:']
        if any(danger in cmd for danger in dangerous_commands):
            await edit_or_reply(event, "🚫 <b>Опасная команда заблокирована!</b>", parse_mode='HTML')
            return
        
        # Экранирование кавычек для bash
        escaped_cmd = cmd.replace("'", "'\"'\"'")
        full_cmd = f"bash -c '{escaped_cmd}'"
        
        # Анимация загрузки
        loading_msg = await edit_or_reply(event, "🖥️")
        
        # Информация о системе
        start_time = time.time()
        current_user = os.getenv('USER', 'unknown')
        current_path = os.getcwd()
        
        # Выполнение команды с умными интервалами
        result = await execute_with_smart_updates(event, loading_msg, full_cmd, start_time, current_user, current_path, original_cmd=cmd)
            
        await loading_msg.edit(result, parse_mode='HTML')
        
    except Exception as e:
        await edit_or_reply(event, f"<b>❌ Ошибка:</b> <code>{str(e)}</code>", parse_mode='HTML')

async def execute_with_smart_updates(event, message, cmd, start_time, user, path, original_cmd=None):
    """Выполнение команды с умными интервалами обновления"""
    
    if original_cmd is None:
        original_cmd = cmd
    
    # Создаем процесс
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE
    )
    
    # Переменные для обновления
    current_output = ""
    current_stderr = ""
    last_update_time = start_time
    update_count = 0
    MAX_UPDATES = 50  # Уменьшили максимальное количество обновлений
    
    # Определяем начальный интервал на основе типа команды
    base_interval = await get_smart_interval(original_cmd)
    current_interval = base_interval
    
    async def update_display(final=False):
        """Обновление отображения с умными интервалами"""
        nonlocal last_update_time, update_count, current_interval
        
        current_time = time.time()
        execution_time = current_time - start_time
        
        # Умное определение интервала
        if execution_time > 30:  # Если команда выполняется долго
            current_interval = 5.0  # Увеличиваем интервал до 5 сек
        elif execution_time > 15:
            current_interval = 3.0
        elif execution_time > 5:
            current_interval = 1.5
        else:
            current_interval = base_interval
        
        # Проверяем, прошло ли достаточно времени с последнего обновления
        time_since_last_update = current_time - last_update_time
        if (time_since_last_update >= current_interval or final) and update_count < MAX_UPDATES:
            
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
                current_interval
            )
            
            try:
                await message.edit(result, parse_mode='HTML')
                last_update_time = current_time
                if not final:
                    update_count += 1
            except Exception as e:
                # Если получили ошибку флуда, увеличиваем интервал
                if "wait" in str(e).lower():
                    current_interval = min(current_interval * 1.5, 10.0)  # Макс 10 сек
                print(f"Update error: {e}")
    
    async def read_stream(stream, is_stdout=True):
        """Чтение потока с умными обновлениями"""
        nonlocal current_output, current_stderr
        
        buffer = ""
        last_chunk_time = time.time()
        
        while True:
            try:
                chunk = await stream.read(512)
                if not chunk:
                    if buffer:
                        # Обновляем перед завершением
                        if is_stdout:
                            current_output = buffer
                        else:
                            current_stderr = buffer
                        await update_display()
                    break
                    
                text = chunk.decode('utf-8', errors='replace')
                buffer += text
                
                # Обработка carriage return
                if '\r' in buffer:
                    lines = buffer.split('\r')
                    buffer = lines[-1]
                
                # Обновляем соответствующий вывод
                if is_stdout:
                    current_output = buffer
                else:
                    current_stderr = buffer
                
                # Обновляем дисплей только если прошло достаточно времени
                current_time = time.time()
                if current_time - last_chunk_time >= current_interval:
                    await update_display()
                    last_chunk_time = current_time
                
            except Exception as e:
                break
    
    async def get_smart_interval(command):
        """Определяет умный интервал обновления на основе команды"""
        command_lower = command.lower()
        
        # Быстрые команды - частые обновления
        if any(cmd in command_lower for cmd in ['ls', 'pwd', 'whoami', 'echo', 'date']):
            return 0.8
        
        # Команды с прогрессом - средние обновления
        if any(cmd in command_lower for cmd in ['wget', 'curl', 'pip install', 'apt', 'yum']):
            return 1.5
        
        # Долгие команды - редкие обновления
        if any(cmd in command_lower for cmd in ['compile', 'build', 'make', 'npm install']):
            return 3.0
        
        # Команды с выводом в реальном времени
        if any(cmd in command_lower for cmd in ['tail -f', 'log', 'monitor']):
            return 2.0
        
        # По умолчанию
        return 1.2
    
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
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    return format_final_output(original_cmd, process.returncode, final_stdout, final_stderr, execution_time, user, path)

def format_live_output(cmd, stdout_text, stderr_text, exec_time, user, path, returncode, update_count, final=False, interval=1.0):
    """Форматирование live-вывода с информацией об интервалах"""
    
    status_icon = "✅" if final and returncode == 0 else "🔄"
    
    if final:
        status_text = "Завершено"
    else:
        status_text = f"Выполняется... (обновление каждые {interval:.1f}сек)"
    
    result = f"""<b>🖥️ Terminal Live</b>

<blockquote>🔧 <b>Команда:</b>
<code>{cmd}</code>

⏱️ <b>Время:</b> <code>{exec_time:.1f}сек</code>
🔄 <b>Обновления:</b> <code>{update_count}</code>
📊 <b>Интервал:</b> <code>{interval:.1f}сек</code>
{f'📊 <b>Код выхода:</b> <code>{returncode}</code>' if final else ''}</blockquote>

"""
    
    if stdout_text:
        clean_output = clean_ansi_codes(stdout_text[-1500:])
        result += f"""<b>📨 Вывод:</b>
<pre>{clean_output}</pre>

"""
    
    if stderr_text:
        clean_stderr = clean_ansi_codes(stderr_text[-800:])
        result += f"""<b>🚨 Ошибки:</b>
<pre>{clean_stderr}</pre>

"""
    
    if not stdout_text and not stderr_text:
        result += f"""<b>📨 Вывод:</b>
<pre>Ожидание вывода...</pre>

"""
    
    result += f"<blockquote>{status_icon} <i>{status_text}</i></blockquote>"
    
    return result

def format_final_output(cmd, returncode, stdout_text, stderr_text, exec_time, user, path):
    """Форматирование финального вывода"""
    
    status_icon = "✅" if returncode == 0 else "❌"
    status_color = "🟢" if returncode == 0 else "🔴"
    
    result = f"""<b>🖥️ Terminal Result</b>

<blockquote>🔧 <b>Команда:</b>
<code>{cmd}</code>

{status_color} <b>Статус:</b> <code>{'Успешно' if returncode == 0 else 'Ошибка'}</code>
📊 <b>Код выхода:</b> <code>{returncode}</code>
⏱️ <b>Время выполнения:</b> <code>{exec_time:.2f}сек</code>
👤 <b>Пользователь:</b> <code>{user}</code>
📁 <b>Путь:</b> <code>{path}</code></blockquote>

"""
    
    if stdout_text:
        clean_stdout = clean_ansi_codes(stdout_text)
        if len(clean_stdout) > 3000:
            clean_stdout = clean_stdout[:3000] + "\n... (вывод обрезан)"
        result += f"""<b>📨 Вывод:</b>
<pre>{clean_stdout}</pre>

"""
    
    if stderr_text:
        clean_stderr = clean_ansi_codes(stderr_text)
        if len(clean_stderr) > 1500:
            clean_stderr = clean_stderr[:1500] + "\n... (ошибки обрезаны)"
        result += f"""<b>🚨 Ошибки:</b>
<pre>{clean_stderr}</pre>

"""
    
    if not stdout_text and not stderr_text:
        result += f"<blockquote>ℹ️ <i>Команда выполнена без вывода</i></blockquote>\n"

    result += f"""<blockquote>{status_icon} <i>Команда выполнена с кодом: {returncode}</i></blockquote>"""
    
    return result

def clean_ansi_codes(text):
    """Очищает ANSI escape-коды из текста"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

# Остальные обработчики (term, shell, exec) остаются без изменений
