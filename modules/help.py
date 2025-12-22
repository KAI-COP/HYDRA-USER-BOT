"""
📚 Smart Help - Умная справочная система
"""

from utils.misc import edit_or_reply, rate_limit
import difflib

class SmartHelp:
    """Умная система справки с автоматическим сбором данных"""

    def __init__(self):
        self.command_usage = {}

    def get_modules_help(self):
        """Получает актуальный modules_help из loader"""
        import utils.loader
        return utils.loader.modules_help

    def log_usage(self, cmd):
        if cmd not in self.command_usage:
            self.command_usage[cmd] = 0
        self.command_usage[cmd] += 1

    def get_module_category(self, module_name):
        """Определяет категорию модуля"""
        core = ['help', 'loader', 'convert']
        utils = ['superping', 'terminal', 'serverinfo', 'sysinfo']
        management = ['modulehub', 'start']

        name_lower = module_name.lower()
        if name_lower in core:
            return "⚙️"
        elif name_lower in utils:
            return "🛠"
        elif name_lower in management:
            return "📦"
        else:
            return "🔧"

    async def show_main(self, event):
        """Главная страница - компактная"""
        from config import prefix

        modules_help = self.get_modules_help()

        if not modules_help:
            await edit_or_reply(event, "❌ No modules loaded")
            return

        self.log_usage("help")

        # Группируем модули
        total_commands = sum(len(cmds) for cmds in modules_help.values())

        # Сортируем модули по категориям
        mods_list = []
        for module_name, commands in modules_help.items():
            emoji = self.get_module_category(module_name)
            mods_list.append((emoji, module_name, len(commands)))

        mods_list.sort(key=lambda x: (x[0], x[1]))

        # Компактный вывод
        text = f"**📚 Hydra Help**\n\n"
        text += f"**📊 Stats:** `{len(modules_help)}` modules • `{total_commands}` commands • prefix `{prefix}`\n\n"

        # Модули компактно в одну строку
        text += "**📦 Modules:**\n"
        for emoji, name, count in mods_list:
            text += f"{emoji} `{name}` ({count}) • "

        # Убираем последний разделитель
        text = text.rstrip(" • ")

        text += f"\n\n**💡 Usage:**\n"
        text += f"• `{prefix}help all` - list all commands\n"
        text += f"• `{prefix}help <module>` - module info\n"
        text += f"• `{prefix}help <cmd>` - command info\n"
        text += f"• `{prefix}find <query>` - search\n"

        await edit_or_reply(event, text)

    async def show_all(self, event):
        """Все команды"""
        from config import prefix

        modules_help = self.get_modules_help()

        if not modules_help:
            await edit_or_reply(event, "❌ No modules loaded")
            return

        self.log_usage("help_all")

        text = f"**📚 All Commands**\n\n"

        for module_name in sorted(modules_help.keys()):
            commands = modules_help[module_name]
            emoji = self.get_module_category(module_name)

            text += f"**{emoji} {module_name}** (`{len(commands)}`)\n"

            for cmd, desc in sorted(commands.items()):
                # Компактный формат
                short_desc = desc[:50] + "..." if len(desc) > 50 else desc
                text += f"  `{prefix}{cmd}` - {short_desc}\n"

            text += "\n"

        text += f"**Total:** `{sum(len(c) for c in modules_help.values())}` commands"

        await edit_or_reply(event, text)

    async def show_module(self, event, module_name):
        """Информация о модуле"""
        from config import prefix

        modules_help = self.get_modules_help()

        # Поиск модуля
        exact_module = None

        if module_name in modules_help:
            exact_module = module_name
        else:
            matches = difflib.get_close_matches(module_name, modules_help.keys(), n=1, cutoff=0.6)
            if matches:
                exact_module = matches[0]

        if not exact_module:
            text = f"❌ **Module not found:** `{module_name}`\n\n"
            text += "**📦 Available:**\n"

            # Компактный список
            mods = list(sorted(modules_help.keys()))
            for i in range(0, len(mods), 3):
                row = mods[i:i+3]
                text += "  " + " • ".join([f"`{m}`" for m in row]) + "\n"

            text += f"\n💡 Use `{prefix}help` to see all"
            await edit_or_reply(event, text)
            return

        self.log_usage(f"help_{exact_module}")

        commands = modules_help[exact_module]
        emoji = self.get_module_category(exact_module)

        text = f"**{emoji} {exact_module}**\n\n"
        text += f"**Commands:** `{len(commands)}`\n\n"

        for cmd, desc in sorted(commands.items()):
            text += f"**`{prefix}{cmd}`**\n{desc}\n\n"

        text += f"💡 Try: `{prefix}{list(commands.keys())[0]}`"

        await edit_or_reply(event, text)

    async def show_command(self, event, command_name):
        """Информация о команде"""
        from config import prefix

        modules_help = self.get_modules_help()

        # Поиск команды
        found = []
        for module_name, commands in modules_help.items():
            if command_name in commands:
                found.append({
                    'module': module_name,
                    'description': commands[command_name]
                })

        if not found:
            # Похожие команды
            all_commands = []
            for commands in modules_help.values():
                all_commands.extend(commands.keys())

            matches = difflib.get_close_matches(command_name, all_commands, n=3, cutoff=0.6)

            text = f"❌ **Command not found:** `{command_name}`\n\n"

            if matches:
                text += "**🔍 Did you mean?**\n"
                for match in matches:
                    text += f"  • `{prefix}{match}`\n"
            else:
                text += f"💡 Use `{prefix}help all` to see all commands"

            await edit_or_reply(event, text)
            return

        self.log_usage(f"cmd_{command_name}")

        if len(found) == 1:
            item = found[0]
            emoji = self.get_module_category(item['module'])

            text = f"**📝 `{prefix}{command_name}`**\n\n"
            text += f"**Module:** {emoji} `{item['module']}`\n\n"
            text += f"**Description:**\n{item['description']}\n\n"
            text += f"**Quick access:**\n"
            text += f"  • `{prefix}{command_name}` - run\n"
            text += f"  • `{prefix}help {item['module']}` - module help"
        else:
            text = f"**📝 `{prefix}{command_name}`**\n\n"
            text += f"**Found in {len(found)} modules:**\n\n"

            for item in found:
                emoji = self.get_module_category(item['module'])
                text += f"**{emoji} {item['module']}**\n{item['description']}\n\n"

        await edit_or_reply(event, text)

    async def search_commands(self, event, query):
        """Поиск команд"""
        from config import prefix

        modules_help = self.get_modules_help()

        query_lower = query.lower()
        results = []

        for module_name, commands in modules_help.items():
            for cmd, desc in commands.items():
                if query_lower in cmd.lower() or query_lower in desc.lower():
                    results.append({
                        'module': module_name,
                        'command': cmd,
                        'description': desc
                    })

        if not results:
            text = f"❌ **No results for:** `{query}`\n\n"
            text += f"💡 Try different keywords or `{prefix}help all`"
            await edit_or_reply(event, text)
            return

        self.log_usage(f"search_{query}")

        text = f"**🔍 Search:** `{query}` (`{len(results)}` found)\n\n"

        # Группируем по модулям
        by_module = {}
        for r in results:
            if r['module'] not in by_module:
                by_module[r['module']] = []
            by_module[r['module']].append(r)

        for module_name in sorted(by_module.keys()):
            emoji = self.get_module_category(module_name)
            items = by_module[module_name]

            text += f"**{emoji} {module_name}**\n"

            for item in items[:3]:
                short_desc = item['description'][:40] + "..." if len(item['description']) > 40 else item['description']
                text += f"  `{prefix}{item['command']}` - {short_desc}\n"

            if len(items) > 3:
                text += f"  ...and {len(items) - 3} more\n"

            text += "\n"

        await edit_or_reply(event, text)

# Глобальный экземпляр
help_system = SmartHelp()

@rate_limit(limit=10, period=30)
async def help_handler(event):
    """📚 Show help"""
    args = event.text.split()

    if len(args) == 1:
        await help_system.show_main(event)
    elif len(args) == 2:
        arg = args[1].lower()

        if arg == "all":
            await help_system.show_all(event)
        else:
            # Модуль или команда?
            modules_help = help_system.get_modules_help()
            is_command = any(arg in commands for commands in modules_help.values())

            if is_command:
                await help_system.show_command(event, arg)
            else:
                await help_system.show_module(event, arg)
    else:
        query = ' '.join(args[1:])
        await help_system.search_commands(event, query)

@rate_limit(limit=5, period=30)
async def modules_handler(event):
    """📦 List modules"""
    await help_system.show_main(event)

@rate_limit(limit=10, period=30)
async def find_handler(event):
    """🔍 Search commands"""
    args = event.text.split(maxsplit=1)

    if len(args) < 2:
        from config import prefix
        text = f"**🔍 Search**\n\n"
        text += f"**Usage:** `{prefix}find <query>`\n\n"
        text += f"**Example:**\n"
        text += f"  `{prefix}find ping` - search 'ping'\n"
        text += f"  `{prefix}find system` - search 'system'\n\n"
        text += "Searches in commands and descriptions"

        await edit_or_reply(event, text)
        return

    await help_system.search_commands(event, args[1])

# Справка
modules_help = {
    "help": {
        "help": "Show help menu",
        "help <module>": "Module information",
        "help <command>": "Command information",
        "help all": "List all commands",
        "modules": "Show all modules",
        "find <query>": "Search commands"
    }
}
