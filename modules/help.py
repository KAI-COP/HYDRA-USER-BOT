from utils.misc import edit_or_reply, rate_limit
from config import prefix

def get_modules():
    import utils.loader
    return utils.loader.modules_help

@rate_limit(5, 30)
async def modules_handler(event):
    """📦 List modules"""
    mods = get_modules()
    
    res = f"<b>🛠 HYDRA MODULES</b>\n\n"
    res += "<blockquote>" + " • ".join(f"<code>{m}</code>" for m in sorted(mods.keys())) + "</blockquote>\n"
    res += f"\nℹ️ <i>Use <code>{prefix}help [module]</code> for details</i>"
    
    await edit_or_reply(event, res, parse_mode='HTML')

@rate_limit(5, 30)
async def help_handler(event):
    """📚 Show help for module or command"""
    args = event.text.split(maxsplit=1)
    mods = get_modules()

    if len(args) < 2:
        return await modules_handler(event)

    query = args[1].lower()
    
    if query in mods:
        res = f"<b>📦 Module:</b> <code>{query}</code>\n\n"
        for cmd, desc in mods[query].items():
            res += f"• <code>{prefix}{cmd}</code>: <i>{desc}</i>\n"
        return await edit_or_reply(event, res, parse_mode='HTML')

    found = []
    for m, cmds in mods.items():
        for c, d in cmds.items():
            if query in c or query in d.lower():
                found.append((c, d))

    if found:
        res = f"<b>🔍 Search:</b> <code>{query}</code>\n\n"
        for c, d in found[:10]:
            res += f"• <code>{prefix}{c}</code>: <i>{d}</i>\n"
        await edit_or_reply(event, res, parse_mode='HTML')
    else:
        await edit_or_reply(event, f"❌ <b>No results for:</b> <code>{query}</code>", parse_mode='HTML')

@rate_limit(5, 30)
async def find_handler(event):
    """🔍 Shortcut for search"""
    await help_handler(event)

modules_help = {
    "help": {
        "help": "List modules or search command",
        "find": "Search for specific command"
    }
}