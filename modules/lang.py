from utils.misc import edit_or_reply, fast_animation, get_user_setting, set_user_setting
import asyncio


class TranslationSystem:
    def __init__(self):
        self.supported_languages = ['ru', 'en']
        self.translations = {
            'ru': {
                # Системные
                'loading': "Загрузка...",
                'error': "Ошибка",
                'success': "Успех",
                'warning': "Предупреждение",
                'info': "Информация",
                'not_found': "Не найдено",
                'access_denied': "Доступ запрещен",
                'rate_limit': "Лимит превышен",
                'not_set': "Не установлен",
                'unknown': "Неизвестно",
                'not_available': "Не доступно",
                'full': "Полная",
                'support': "поддержка",
                'change_language': "Сменить язык",
                'or': "или",
                'and': "и",
                'username': "Имя пользователя",
                'performance': "производительность",
                'metrics': "метрики",
                'powered_by': "Работает на",
                'developers': "Разработчики",
                
                # Заголовки
                'help_title': "СИСТЕМА ПОМОЩИ HYDRA",
                'start_title': "Hydra User Bot", 
                'ping_title': "РЕЗУЛЬТАТЫ PING",
                'server_title': "ИНФОРМАЦИЯ О СЕРВЕРЕ",
                'terminal_title': "ТЕРМИНАЛ",
                'lang_title': "СИСТЕМА ЯЗЫКА",
                'installer_title': "СИСТЕМА УСТАНОВКИ МОДУЛЕЙ",
                
                # Основные тексты
                'version': "Версия",
                'user': "Пользователь", 
                'developer': "Разработчик",
                'response': "Ответ",
                'uptime': "Аптайм",
                'stats': "Статистика",
                'modules': "Модули",
                'commands': "Команды",
                'core_modules': "ОСНОВНЫЕ МОДУЛИ",
                'user_modules': "ПОЛЬЗОВАТЕЛЬСКИЕ МОДУЛИ",
                'usage': "Использование",
                'examples': "Примеры",
                'total': "Всего",
                'available': "Доступно",
                'settings': "Настройки",
                'language': "Язык",
                'current': "Текущий",
                'system': "Система",
                'platform': "Платформа",
                'implementation': "Реализация",
                'hostname': "Имя хоста",
                'for_more_info': "Для дополнительной информации",
                
                # Help система
                'overview': "Обзор",
                'quick_access': "Быстрый доступ", 
                'available_modules': "Доступные модули",
                'module_details': "Подробности модуля",
                'command_help': "Помощь по команде",
                'search_commands': "Поиск команд", 
                'statistics': "Статистика",
                'popular_commands': "Популярные команды",
                'description': "Описание",
                'details': "Подробности",
                'navigation': "Навигация",
                'related': "Связанное",
                
                # Terminal - НОВЫЕ ПЕРЕВОДЫ
                'executing': "Выполнение",
                'command': "Команда",
                'exit_code': "Код выхода",
                'output': "Вывод",
                'success_exec': "Успешно выполнено",
                'stdout': "Стандартный вывод",
                'stderr': "Ошибки",
                'time': "Время",
                'path': "Путь",
                'command_executed': "Команда выполнена",
                'with_exit_code': "с кодом выхода",
                'terminal_live': "Terminal Live",
                'terminal_result': "Terminal Result",
                'status': "Статус",
                'execution_time': "Время выполнения",
                'waiting_output': "Ожидание вывода",
                'command_completed': "Команда выполнена",
                'no_output': "Нет вывода",
                'output_truncated': "вывод обрезан",
                'errors_truncated': "ошибки обрезаны",
                'terminal_help_title': "🖥️ Terminal",
                'terminal_help_usage': "Использование",
                'terminal_help_examples': "Примеры",
                'terminal_help_permissions': "Права",
                'terminal_help_current_path': "Текущий путь",
                'terminal_help_features': "Особенности",
                'terminal_live_updates': "Live-обновление вывода в реальном времени",
                'terminal_animations_support': "Поддержка анимаций и прогресса",
                'terminal_ansi_cleanup': "Убирает цветовой вывод (ANSI codes) для красивого вывода",
                'terminal_long_commands': "Обработка длинных команд",
                'terminal_hang_protection': "Защита от зависаний",
                'terminal_dangerous_blocked': "Опасная команда заблокирована",
                'terminal_executing_command': "Выполняю команду",
                'terminal_scanning_directory': "Сканирую директорию",
                'terminal_gathering_info': "Собираю информацию",
                'terminal_environment': "Terminal Environment",
                'terminal_shell': "Shell",
                'terminal_terminal': "Terminal",
                'terminal_home_directory': "Домашняя директория",
                'terminal_permissions': "Права",
                'terminal_available_commands': "Доступные команды",
                'terminal_environment_variables': "Переменные окружения",
                'terminal_current_directory': "Текущая директория",
                'terminal_full_path': "Полный путь",
                'terminal_directory_info': "Информация",
                'terminal_exists': "Существует",
                'terminal_writable': "Доступ на запись",
                'terminal_readable': "Доступ на чтение",
                'terminal_quick_commands': "Быстрые команды",
                'terminal_directory_content': "Содержимое директории",
                'terminal_items_count': "Объектов",
                'terminal_folders': "папок",
                'terminal_files': "файлов",
                'terminal_folders_list': "Папки",
                'terminal_files_list': "Файлы",
                'terminal_empty_directory': "Директория пуста",
                'terminal_use_for_details': "Используйте для детальной информации",
                'terminal_cleaner': "Terminal Cleaner",
                'terminal_cleared_status': "История терминала очищена",
                'terminal_freed_space': "Освобождено",
                'terminal_optimization': "Оптимизация",
                'terminal_cache_cleared': "Кэш сброшен",
                'terminal_recommendations': "Рекомендации",
                'terminal_clear_session': "очистка сессии",
                'terminal_clear_history': "очистка истории команд",
                'terminal_full_cleanup': "полная очистка",
                'terminal_symbolic_cleanup': "Очистка выполнена символически",
                'terminal_use_system_commands': "Для реальной очистки используйте системные команды",
                'terminal_completed_with_code': "Команда выполнена с кодом",
                'terminal_success': "Успешно",
                'terminal_failed': "Ошибка",
                'terminal_in_progress': "Выполняется",
                'terminal_updates_count': "обновление",
                'terminal_completed': "Завершено",
                
                # Server info
                'os': "ОС",
                'architecture': "Архитектура",
                'python_version': "Версия Python",
                'directory': "Директория",
                'cpu': "Процессор",
                'memory': "Память",
                'disk': "Диск",
                'cores': "Ядра",
                'usage': "Использование",
                'total_memory': "Всего памяти",
                'used_memory': "Использовано памяти",
                'available_memory': "Доступно памяти",
                'total_disk': "Всего диска",
                'used_disk': "Использовано диска",
                'free_disk': "Свободно диска",
                'install': "Установить",
                'server_hardware_info': "информация о серверном оборудовании",
                'basic_system_info': "базовая системная информация",
                
                # Lang модуль
                'language_set': "Язык установлен",
                'unsupported_language': "Неподдерживаемый язык",
                'supported_languages': "Поддерживаемые языки",
                'current_language': "Текущий язык",
                'set_language': "Установить язык",
                'language_changed_success': "Язык успешно изменен",
                'language_change_error': "Ошибка смены языка",
                
                # HLoader модуль
                'module_installed': "Модуль установлен",
                'module_removed': "Модуль удален",
                'module_reloaded': "Модуль перезагружен",
                'dangerous_code': "Опасный код",
                'download_error': "Ошибка загрузки",
                'installation_error': "Ошибка установки",
                'loading_error': "Ошибка загрузки",
                'uninstall_error': "Ошибка удаления",
                'reload_error': "Ошибка перезагрузки",
                'module_not_found': "Модуль не найден",
                'multiple_modules_found': "Найдено несколько модулей",
                'specify_exact_name': "Укажите точное имя",
                'file_not_found': "Файл не найден",
                'installed_modules': "Установленные модули",
                'no_installed_modules': "Нет установленных модулей",
                'module_information': "Информация о модуле",
                'file': "Файл",
                'source': "Источник",
                'command_list': "Список команд",
                'management': "Управление",
                'scanning_modules': "Сканирование модулей",
                'loaded_modules': "Загружено модулей",
                'install_from_url': "Установить по ссылке",
                'install_from_text': "Установить из текста",
                'install_from_file': "Установить из файла",
                'file_must_be_python': "Файл должен быть Python файлом (.py)",
                'downloading_file': "Скачивание файла",
                'file_read_error': "Ошибка чтения файла",
                'downloading_module': "Скачивание модуля",
                'commands_count': "команд",
                'command_word_single': "команда",
                'command_word_few': "команды",
                'command_word_many': "команд",
                'existing_source': "существующий",
                'url_source': "URL",
                'text_source': "текстовое сообщение",
                'file_source': "файл",
                'reload_source': "перезагрузка",
                'available_commands': "Доступные команды",
                'module_file': "Файл модуля",
                'uninstall_usage': "Удалить модуль",
                'reload_usage': "Перезагрузить модуль",
                'module_info_usage': "Информация о модуле",
                'list_modules_usage': "Список модулей",
                'install_usage': "Установить модуль",
                'safe_code_check': "Проверка безопасности кода",
                'dangerous_patterns_detected': "Обнаружены опасные паттерны",
                'forbidden_import': "Запрещенный импорт",
                'forbidden_call': "Запрещенный вызов",
                'syntax_error': "Синтаксическая ошибка",
                'code_safety_check': "Проверка безопасности кода",
                
                # Общие фразы
                'yes': "Да",
                'no': "Нет",
                'on': "Вкл",
                'off': "Выкл",
                'enabled': "Включено",
                'disabled': "Выключено",
                'active': "Активно",
                'inactive': "Неактивно",
                'online': "Онлайн",
                'offline': "Офлайн",
                'true': "Истина",
                'false': "Ложь",
                
                # Время
                'seconds': "секунд",
                'minutes': "минут",
                'hours': "часов",
                'days': "дней",
                'weeks': "недель",
                'months': "месяцев",
                'years': "лет",
                
                # Разное
                'install': "Установить",
                'update': "Обновить",
                'restart': "Перезапустить",
                'stop': "Остановить",
                'start': "Запустить",
                'configure': "Настроить",
                'reset': "Сбросить",
                'back': "Назад",
                'next': "Далее",
                'previous': "Предыдущий",
                'first': "Первый",
                'last': "Последний",
                'more': "Еще",
                'less': "Меньше",
                'all': "Все",
                'none': "Ничего",
                'some': "Некоторые",
                'many': "Много",
                'few': "Мало",
                'every': "Каждый",
                'each': "Каждый",
                'any': "Любой",
                'other': "Другой",
                'same': "Такой же",
                'different': "Разный",
                'important': "Важный",
                'necessary': "Необходимый",
                'optional': "Опциональный",
                'required': "Обязательный",
                'default': "По умолчанию",
                'custom': "Пользовательский",
                'auto': "Авто",
                'manual': "Ручной",
                'easy': "Легкий",
                'hard': "Сложный",
                'simple': "Простой",
                'complex': "Сложный",
                'fast': "Быстрый",
                'slow': "Медленный",
                'new': "Новый",
                'old': "Старый",
                'good': "Хороший",
                'bad': "Плохой",
                'better': "Лучше",
                'worse': "Хуже",
                'best': "Лучший",
                'worst': "Худший",
                
                # Новые переводы для help системы
                'all_commands': "ВСЕ КОМАНДЫ",
                'complete_command_reference': "полный справочник команд",
                'main_modules': "ОСНОВНЫЕ МОДУЛИ",
                'quick_help': "Быстрый доступ",
                'module_help': "детали модуля",
                'command_help': "помощь по команде",
                'search_commands': "Поиск команд",
                'current_language_display': "Текущий",
                'use_command_for_help': "используйте .help <command> для подробной справки",
                'total_commands_count': "Всего команд",
                'alternative_for': "Альтернатива для",
                'show_detailed_statistics': "Показать детальную статистику",
                'show_most_used_commands': "Показать самые используемые команды",
                'set_language_command': "Установить язык (ru/en)",
                'show_supported_languages': "Показать поддерживаемые языки",
                'show_current_language_settings': "Показать текущие настройки языка",
                'check_bot_response_time': "Проверить время ответа бота и аптайм",
                'show_detailed_server_info': "Показать детальную информацию о сервере",
                'show_basic_system_info': "Показать базовую системную информацию",
                'start_bot_and_show_info': "Запустить бота и показать информацию",
                'execute_command_in_terminal': "Выполнить команду в терминале",
                'short_version_of_terminal': "Короткая версия terminal",
                'execute_shell_command': "Выполнить shell команду",
                'execute_system_command': "Выполнить системную команду",
                
                # Новые общие фразы
                'prefix': "префикс",
                'use': "используйте",
                'to_see': "чтобы увидеть",
                'for_detailed_help': "для подробной справки",
                'complete': "полный",
                'reference': "справочник",
                'try': "попробуйте",
                'main_menu': "главное меню",
                'documentation': "документация",
                'for_commands': "для команд",
                'core': "основные",
                'user_custom': "пользовательские",
                'top': "топ",
                'uses': "использований",
                'last_update': "последнее обновление",
                'found': "найдено",
                'results': "результатов",
                'more_results': "еще",
                'for_your_query': "для вашего запроса",
                'no_usage_data_yet': "данные об использовании еще не собраны",
                'commands_will_appear_here': "команды появятся здесь по мере использования",
                'no_command_usage_data': "нет данных об использовании команд",
                'most_frequently_used_commands': "наиболее часто используемые команды",
                'specify_search_term': "укажите поисковый запрос",
                'search_commands_by_name_or_description': "поиск команд по имени или описанию",
                'choose_your_preferred_language': "выберите ваш предпочтительный язык",
                'for_better_experience': "для лучшего опыта",
                'your_personal_settings': "ваши персональные настройки",
                'languages_list': "языки",
                'in_multiple_modules': "в нескольких модулях",
                'available_in': "доступна в",
                'command_details': "детали команды",
                'performance_metrics': "производительность метрики",
                'no_modules_loaded': "модули не загружены",
                'module_documentation': "документация модуля",
                'popular_commands_list': "популярные команды",
                'system_statistics': "системная статистика",
                'search_functionality': "функция поиска",
                'execute_system_commands_safely': "выполнять системные команды безопасно",
                'no_modules_found': "модули не найдены",
                
                # Система ограничений
                'rate_limit_exceeded': "ПРЕВЫШЕН ЛИМИТ ИСПОЛЬЗОВАНИЯ",
                'limit_reached': "Достигнут лимит команд",
                'wait_time': "Ожидание",
                'current_usage': "Текущее использование",
                'period': "Период",
                'rate_limit_tip': "Советы по использованию",
                'slow_down_commands': "Замедлите выполнение команд",
                'wait_before_retry': "Подождите перед повторной попыткой",
                'contact_admin_if_issue': "Обратитесь к администратору если это ошибка",
                'anti_spam_protection': "Система защиты от спама",
                'rate_limit_info': "Информация о лимитах",
                'your_current_limits': "Ваши текущие лимиты",
                'commands_used': "команд использовано",
                'reset_in': "Сброс через",
                'unlimited': "Неограниченно",
                'rate_settings': "Настройки лимитов",
                'protection_system': "Система защиты",
            },
            'en': {
                # System
                'loading': "Loading...",
                'error': "Error",
                'success': "Success",
                'warning': "Warning",
                'info': "Information",
                'not_found': "Not found",
                'access_denied': "Access denied",
                'rate_limit': "Rate limit exceeded",
                'not_set': "Not set",
                'unknown': "Unknown",
                'not_available': "Not available",
                'full': "Full",
                'support': "support",
                'change_language': "Change language",
                'or': "or",
                'and': "and",
                'username': "Username",
                'performance': "performance",
                'metrics': "metrics",
                'powered_by': "Powered by",
                'developers': "Developers",
                
                # Titles
                'help_title': "HYDRA HELP SYSTEM", 
                'start_title': "Hydra User Bot",
                'ping_title': "PING RESULTS",
                'server_title': "SERVER INFORMATION", 
                'terminal_title': "TERMINAL",
                'lang_title': "LANGUAGE SYSTEM",
                'installer_title': "MODULE INSTALLATION SYSTEM",
                
                # Main texts
                'version': "Version",
                'user': "User",
                'developer': "Developer", 
                'response': "Response",
                'uptime': "Uptime",
                'stats': "Statistics",
                'modules': "Modules", 
                'commands': "Commands",
                'core_modules': "CORE MODULES",
                'user_modules': "USER MODULES", 
                'usage': "Usage",
                'examples': "Examples",
                'total': "Total",
                'available': "Available",
                'settings': "Settings",
                'language': "Language",
                'current': "Current",
                'system': "System",
                'platform': "Platform",
                'implementation': "Implementation",
                'hostname': "Hostname",
                'for_more_info': "For more information",
                
                # Help system
                'overview': "Overview",
                'quick_access': "Quick Access",
                'available_modules': "Available Modules", 
                'module_details': "Module Details",
                'command_help': "Command Help",
                'search_commands': "Search Commands", 
                'statistics': "Statistics",
                'popular_commands': "Popular Commands",
                'description': "Description",
                'details': "Details",
                'navigation': "Navigation",
                'related': "Related",
                
                # Terminal - NEW TRANSLATIONS
                'executing': "Executing",
                'command': "Command",
                'exit_code': "Exit code",
                'output': "Output",
                'success_exec': "Successfully executed",
                'stdout': "Standard output",
                'stderr': "Errors",
                'time': "Time",
                'path': "Path",
                'command_executed': "Command executed",
                'with_exit_code': "with exit code",
                'terminal_live': "Terminal Live",
                'terminal_result': "Terminal Result",
                'status': "Status",
                'execution_time': "Execution time",
                'waiting_output': "Waiting for output",
                'command_completed': "Command completed",
                'no_output': "No output",
                'output_truncated': "output truncated",
                'errors_truncated': "errors truncated",
                'terminal_help_title': "🖥️ Terminal",
                'terminal_help_usage': "Usage",
                'terminal_help_examples': "Examples",
                'terminal_help_permissions': "Permissions",
                'terminal_help_current_path': "Current path",
                'terminal_help_features': "Features",
                'terminal_live_updates': "Live output updates in real time",
                'terminal_animations_support': "Support for animations and progress",
                'terminal_ansi_cleanup': "Removes color output (ANSI codes) for clean output",
                'terminal_long_commands': "Long command processing",
                'terminal_hang_protection': "Hang protection",
                'terminal_dangerous_blocked': "Dangerous command blocked",
                'terminal_executing_command': "Executing command",
                'terminal_scanning_directory': "Scanning directory",
                'terminal_gathering_info': "Gathering information",
                'terminal_environment': "Terminal Environment",
                'terminal_shell': "Shell",
                'terminal_terminal': "Terminal",
                'terminal_home_directory': "Home directory",
                'terminal_permissions': "Permissions",
                'terminal_available_commands': "Available commands",
                'terminal_environment_variables': "Environment variables",
                'terminal_current_directory': "Current directory",
                'terminal_full_path': "Full path",
                'terminal_directory_info': "Information",
                'terminal_exists': "Exists",
                'terminal_writable': "Writable",
                'terminal_readable': "Readable",
                'terminal_quick_commands': "Quick commands",
                'terminal_directory_content': "Directory content",
                'terminal_items_count': "Items",
                'terminal_folders': "folders",
                'terminal_files': "files",
                'terminal_folders_list': "Folders",
                'terminal_files_list': "Files",
                'terminal_empty_directory': "Directory is empty",
                'terminal_use_for_details': "Use for detailed information",
                'terminal_cleaner': "Terminal Cleaner",
                'terminal_cleared_status': "Terminal history cleared",
                'terminal_freed_space': "Freed",
                'terminal_optimization': "Optimization",
                'terminal_cache_cleared': "Cache cleared",
                'terminal_recommendations': "Recommendations",
                'terminal_clear_session': "clear session",
                'terminal_clear_history': "clear command history",
                'terminal_full_cleanup': "full cleanup",
                'terminal_symbolic_cleanup': "Cleanup performed symbolically",
                'terminal_use_system_commands': "For real cleanup use system commands",
                'terminal_completed_with_code': "Command completed with code",
                'terminal_success': "Success",
                'terminal_failed': "Error",
                'terminal_in_progress': "In progress",
                'terminal_updates_count': "update",
                'terminal_completed': "Completed",
                
                # Server info
                'os': "OS",
                'architecture': "Architecture",
                'python_version': "Python version",
                'directory': "Directory",
                'cpu': "CPU",
                'memory': "Memory",
                'disk': "Disk",
                'cores': "Cores",
                'usage': "Usage",
                'total_memory': "Total memory",
                'used_memory': "Used memory",
                'available_memory': "Available memory",
                'total_disk': "Total disk",
                'used_disk': "Used disk",
                'free_disk': "Free disk",
                'install': "Install",
                'server_hardware_info': "server hardware information",
                'basic_system_info': "basic system information",
                
                # Lang module
                'language_set': "Language set",
                'unsupported_language': "Unsupported language",
                'supported_languages': "Supported languages",
                'current_language': "Current language",
                'set_language': "Set language",
                'language_changed_success': "Language successfully changed",
                'language_change_error': "Language change error",
                
                # HLoader module
                'module_installed': "Module installed",
                'module_removed': "Module removed",
                'module_reloaded': "Module reloaded",
                'dangerous_code': "Dangerous code",
                'download_error': "Download error",
                'installation_error': "Installation error",
                'loading_error': "Loading error",
                'uninstall_error': "Uninstall error",
                'reload_error': "Reload error",
                'module_not_found': "Module not found",
                'multiple_modules_found': "Multiple modules found",
                'specify_exact_name': "Specify exact name",
                'file_not_found': "File not found",
                'installed_modules': "Installed modules",
                'no_installed_modules': "No installed modules",
                'module_information': "Module information",
                'file': "File",
                'source': "Source",
                'command_list': "Command list",
                'management': "Management",
                'scanning_modules': "Scanning modules",
                'loaded_modules': "Loaded modules",
                'install_from_url': "Install from URL",
                'install_from_text': "Install from text",
                'install_from_file': "Install from file",
                'file_must_be_python': "File must be Python file (.py)",
                'downloading_file': "Downloading file",
                'file_read_error': "File read error",
                'downloading_module': "Downloading module",
                'commands_count': "commands",
                'command_word_single': "command",
                'command_word_few': "commands",
                'command_word_many': "commands",
                'existing_source': "existing",
                'url_source': "URL",
                'text_source': "text message",
                'file_source': "file",
                'reload_source': "reload",
                'available_commands': "Available commands",
                'module_file': "Module file",
                'uninstall_usage': "Uninstall module",
                'reload_usage': "Reload module",
                'module_info_usage': "Module information",
                'list_modules_usage': "List modules",
                'install_usage': "Install module",
                'safe_code_check': "Safe code check",
                'dangerous_patterns_detected': "Dangerous patterns detected",
                'forbidden_import': "Forbidden import",
                'forbidden_call': "Forbidden call",
                'syntax_error': "Syntax error",
                'code_safety_check': "Code safety check",
                
                # Common phrases
                'yes': "Yes",
                'no': "No",
                'on': "On",
                'off': "Off",
                'enabled': "Enabled",
                'disabled': "Disabled",
                'active': "Active",
                'inactive': "Inactive",
                'online': "Online",
                'offline': "Offline",
                'true': "True",
                'false': "False",
                
                # Time
                'seconds': "seconds",
                'minutes': "minutes",
                'hours': "hours",
                'days': "days",
                'weeks': "weeks",
                'months': "months",
                'years': "years",
                
                # Miscellaneous
                'install': "Install",
                'update': "Update",
                'restart': "Restart",
                'stop': "Stop",
                'start': "Start",
                'configure': "Configure",
                'reset': "Reset",
                'back': "Back",
                'next': "Next",
                'previous': "Previous",
                'first': "First",
                'last': "Last",
                'more': "More",
                'less': "Less",
                'all': "All",
                'none': "None",
                'some': "Some",
                'many': "Many",
                'few': "Few",
                'every': "Every",
                'each': "Each",
                'any': "Any",
                'other': "Other",
                'same': "Same",
                'different': "Different",
                'important': "Important",
                'necessary': "Necessary",
                'optional': "Optional",
                'required': "Required",
                'default': "Default",
                'custom': "Custom",
                'auto': "Auto",
                'manual': "Manual",
                'easy': "Easy",
                'hard': "Hard",
                'simple': "Simple",
                'complex': "Complex",
                'fast': "Fast",
                'slow': "Slow",
                'new': "New",
                'old': "Old",
                'good': "Good",
                'bad': "Bad",
                'better': "Better",
                'worse': "Worse",
                'best': "Best",
                'worst': "Worst",
                
                # New translations for help system
                'all_commands': "ALL COMMANDS",
                'complete_command_reference': "complete command reference",
                'main_modules': "MAIN MODULES",
                'quick_help': "Quick Access",
                'module_help': "module details",
                'command_help': "command help",
                'search_commands': "Search Commands",
                'current_language_display': "Current",
                'use_command_for_help': "use .help <command> for detailed help",
                'total_commands_count': "Total commands",
                'alternative_for': "Alternative for",
                'show_detailed_statistics': "Show detailed statistics",
                'show_most_used_commands': "Show most used commands",
                'set_language_command': "Set your language (ru/en)",
                'show_supported_languages': "Show supported languages",
                'show_current_language_settings': "Show current language settings",
                'check_bot_response_time': "Check bot response time and uptime",
                'show_detailed_server_info': "Show detailed server information",
                'show_basic_system_info': "Show basic system information",
                'start_bot_and_show_info': "Start the bot and show information",
                'execute_command_in_terminal': "Execute command in terminal",
                'short_version_of_terminal': "Short version of terminal",
                'execute_shell_command': "Execute shell command",
                'execute_system_command': "Execute system command",
                
                # New common phrases
                'prefix': "prefix",
                'use': "use",
                'to_see': "to see",
                'for_detailed_help': "for detailed help",
                'complete': "complete",
                'reference': "reference",
                'try': "try",
                'main_menu': "main menu",
                'documentation': "documentation",
                'for_commands': "for commands",
                'core': "core",
                'user_custom': "user",
                'top': "top",
                'uses': "uses",
                'last_update': "last update",
                'found': "found",
                'results': "results",
                'more_results': "more",
                'for_your_query': "for your query",
                'no_usage_data_yet': "no usage data yet",
                'commands_will_appear_here': "commands will appear here as you use them",
                'no_command_usage_data': "no command usage data",
                'most_frequently_used_commands': "most frequently used commands",
                'specify_search_term': "specify search term",
                'search_commands_by_name_or_description': "search commands by name or description",
                'choose_your_preferred_language': "choose your preferred language",
                'for_better_experience': "for better experience",
                'your_personal_settings': "your personal settings",
                'languages_list': "languages",
                'in_multiple_modules': "in multiple modules",
                'available_in': "available in",
                'command_details': "command details",
                'performance_metrics': "performance metrics",
                'no_modules_loaded': "no modules loaded",
                'module_documentation': "module documentation",
                'popular_commands_list': "popular commands",
                'system_statistics': "system statistics",
                'search_functionality': "search functionality",
                'execute_system_commands_safely': "execute system commands safely",
                'no_modules_found': "no modules found",
                
                # Rate limiting system
                'rate_limit_exceeded': "RATE LIMIT EXCEEDED",
                'limit_reached': "Command limit reached",
                'wait_time': "Wait time",
                'current_usage': "Current usage",
                'period': "Period",
                'rate_limit_tip': "Usage tips",
                'slow_down_commands': "Slow down command execution",
                'wait_before_retry': "Wait before retrying",
                'contact_admin_if_issue': "Contact admin if this is an error",
                'anti_spam_protection': "Anti-spam protection system",
                'rate_limit_info': "Rate limit information",
                'your_current_limits': "Your current limits",
                'commands_used': "commands used",
                'reset_in': "Reset in",
                'unlimited': "Unlimited",
                'rate_settings': "Rate settings",
                'protection_system': "Protection system",
            }
        }
    
    def get_text(self, user_id, key):
        """Get text in user's language"""
        lang = get_user_setting(user_id, 'language', 'en')
        return self.translations[lang].get(key, key)
    
    def set_language(self, user_id, language):
        """Set user language"""
        if language in self.supported_languages:
            set_user_setting(user_id, 'language', language)
            return True
        return False
    
    def get_current_language(self, user_id):
        """Get current user language"""
        return get_user_setting(user_id, 'language', 'en')


# Global translation instance
translator = TranslationSystem()


async def lang_handler(event):
    """Set language with fast animation"""
    loading_msg = await edit_or_reply(event, "🌐")
    await fast_animation(loading_msg, "🌐", f"🌐 {translator.get_text(event.sender_id, 'loading')}")
    
    args = event.text.split()
    
    if len(args) == 1:
        current_lang = translator.get_current_language(event.sender_id)
        text = f"""<b>🌐 {translator.get_text(event.sender_id, 'lang_title')}</b>

<blockquote>📝 <b>{translator.get_text(event.sender_id, 'current_language')}:</b> <code>{current_lang.upper()}</code>

🔧 <b>{translator.get_text(event.sender_id, 'usage')}:</b>
<code>.lang ru</code> {translator.get_text(event.sender_id, 'or')} <code>.lang en</code>

💡 <b>{translator.get_text(event.sender_id, 'examples')}:</b>
<code>.lang ru</code> - Русский
<code>.lang en</code> - English</blockquote>

<blockquote>💡 {translator.get_text(event.sender_id, 'use')} <code>.lang</code> {translator.get_text(event.sender_id, 'to_see')} {translator.get_text(event.sender_id, 'current')} {translator.get_text(event.sender_id, 'settings')}</blockquote>"""
        
        await loading_msg.edit(text, parse_mode='HTML')
        return
    
    language = args[1].lower()
    if translator.set_language(event.sender_id, language):
        text = f"""<b>✅ {translator.get_text(event.sender_id, 'language_changed_success')}</b>

<blockquote>🌍 <b>{translator.get_text(event.sender_id, 'language')}:</b> <code>{language.upper()}</code>
👤 <b>{translator.get_text(event.sender_id, 'user')}:</b> <code>{event.sender_id}</code></blockquote>

<blockquote>💡 {translator.get_text(event.sender_id, 'success')}! {translator.get_text(event.sender_id, 'language')} {translator.get_text(event.sender_id, 'success')}</blockquote>"""
        
        await loading_msg.edit(text, parse_mode='HTML')
    else:
        text = f"""<b>❌ {translator.get_text(event.sender_id, 'language_change_error')}</b>

<blockquote>🚫 <b>{translator.get_text(event.sender_id, 'unsupported_language')}:</b> <code>{language}</code>

✅ <b>{translator.get_text(event.sender_id, 'supported_languages')}:</b>
🇷🇺 <code>ru</code> - Russian
🇺🇸 <code>en</code> - English</blockquote>

<blockquote>💡 {translator.get_text(event.sender_id, 'use')} <code>.lang</code> {translator.get_text(event.sender_id, 'to_see')} {translator.get_text(event.sender_id, 'current')} {translator.get_text(event.sender_id, 'settings')}</blockquote>"""
        
        await loading_msg.edit(text, parse_mode='HTML')


async def languages_handler(event):
    """Show all supported languages with animation"""
    loading_msg = await edit_or_reply(event, "🌍")
    await fast_animation(loading_msg, "🌍", f"🌍 {translator.get_text(event.sender_id, 'loading')}")
    
    text = f"""<b>🌐 {translator.get_text(event.sender_id, 'supported_languages').upper()}</b>

<blockquote>🇷🇺 <b>Russian (ru)</b>
- {translator.get_text(event.sender_id, 'full')} Russian {translator.get_text(event.sender_id, 'support')}

🇺🇸 <b>English (en)</b> 
- {translator.get_text(event.sender_id, 'full')} English {translator.get_text(event.sender_id, 'support')}

💡 <b>{translator.get_text(event.sender_id, 'usage')}:</b>
<code>.lang ru</code> - Русский
<code>.lang en</code> - English</blockquote>

<blockquote>🌍 {translator.get_text(event.sender_id, 'choose_your_preferred_language')} {translator.get_text(event.sender_id, 'for_better_experience')}</blockquote>"""

    await loading_msg.edit(text, parse_mode='HTML')


async def mylang_handler(event):
    """Show current language settings"""
    current_lang = translator.get_current_language(event.sender_id)
    username = getattr(event.sender, 'username', translator.get_text(event.sender_id, 'not_set'))
    first_name = getattr(event.sender, 'first_name', translator.get_text(event.sender_id, 'unknown'))
    
    text = f"""<b>🌐 {translator.get_text(event.sender_id, 'language').upper()} {translator.get_text(event.sender_id, 'settings')}</b>

<blockquote>👤 <b>{translator.get_text(event.sender_id, 'user')}:</b> {first_name}
📱 <b>{translator.get_text(event.sender_id, 'username')}:</b> @{username}
🆔 <b>ID:</b> <code>{event.sender_id}</code>
🌍 <b>{translator.get_text(event.sender_id, 'current_language')}:</b> <code>{current_lang.upper()}</code>

🔧 <b>{translator.get_text(event.sender_id, 'available')} {translator.get_text(event.sender_id, 'commands')}:</b>
<code>.lang ru</code> - Русский
<code>.lang en</code> - English
<code>.languages</code> - {translator.get_text(event.sender_id, 'all')} {translator.get_text(event.sender_id, 'languages_list')}</blockquote>

<blockquote>⚙️ {translator.get_text(event.sender_id, 'your_personal_settings')}</blockquote>"""

    await edit_or_reply(event, text, parse_mode='HTML')


modules_help = {
    "lang": {
        "lang": "Set your language (ru/en)",
        "languages": "Show supported languages", 
        "mylang": "Show current language settings"
    }
}
