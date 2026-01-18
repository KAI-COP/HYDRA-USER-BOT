import platform
import os
from utils.misc import edit_or_reply, fast_animation

async def serverinfo_handler(event):
    try:
        loading_msg = await edit_or_reply(event, "🖥")
        await fast_animation(loading_msg, "🖥", "🖥 Loading...")
        
        system_info = f"""<b>🖥 Server Info</b>

<b>💻 OS:</b> <code>{platform.system()} {platform.release()}</code>
<b>🏗 Architecture:</b> <code>{platform.architecture()[0]}</code>
<b>🐍 Python:</b> <code>{platform.python_version()}</code>
<b>📁 Directory:</b> <code>{os.getcwd()}</code>"""

        try:
            import psutil
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_info += f"""
\n<b>⚡ CPU:</b>
<blockquote expandable>- <b>Cores:</b> <code>{psutil.cpu_count(logical=True)}</code>
- <b>Usage:</b> <code>{psutil.cpu_percent(interval=1)}%</code></blockquote>
\n<b>💾 Memory:</b>
<blockquote expandable>- <b>Total:</b> <code>{round(memory.total / (1024**3), 1)} GB</code>
- <b>Available:</b> <code>{round(memory.available / (1024**3), 1)} GB</code>
- <b>Usage:</b> <code>{memory.percent}%</code></blockquote>
\n<b>💽 Disk:</b>
<blockquote expandable>- <b>Total:</b> <code>{round(disk.total / (1024**3), 1)} GB</code>
- <b>Used:</b> <code>{round(disk.used / (1024**3), 1)} GB</code>  
- <b>Free:</b> <code>{round(disk.free / (1024**3), 1)} GB</code>
- <b>Usage:</b> <code>{disk.percent}%</code></blockquote>"""
        except ImportError:
            system_info += "\n\n<b>💡 Tip:</b> Install <code>psutil</code> for more info."

        await loading_msg.edit(system_info, parse_mode='HTML')
    except Exception as e:
        await edit_or_reply(event, f"<b>❌ Error:</b> {str(e)}", parse_mode='HTML')

async def sysinfo_handler(event):
    info = f"""<b>📱 System Info</b>\n
<b>🏗 Platform:</b> <code>{platform.platform()}</code>
<b>🐍 Python:</b> <code>{platform.python_version()}</code>
<b>👤 User:</b> <code>{os.getenv('USER', 'unknown')}</code>
<b>📟 Hostname:</b> <code>{platform.node()}</code>\n
<b>🔧 More:</b> <code>.serverinfo</code>"""
    await edit_or_reply(event, info, parse_mode='HTML')