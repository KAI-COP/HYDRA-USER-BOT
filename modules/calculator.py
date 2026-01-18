import math
from utils.misc import edit_or_reply, rate_limit
from config import prefix

modules_help = {
    "calculator": {
        "calc": "Вычислить математическое выражение. Пример: .calc 2+2*5"
    }
}

@rate_limit(60, 60)
async def calc(event):
    """Вычисление математических выражений"""
    args = event.text.split(maxsplit=1)
    
    if len(args) < 2:
        return await edit_or_reply(event, f"❌ <b>Введите выражение!</b>\nПример: <code>{prefix}calc 2+2</code>", parse_mode='HTML')

    expression = args[1]
    
    try:

        safe_dict = {k: v for k, v in vars(math).items() if not k.startswith("_")}

        result = eval(expression, {"__builtins__": None}, safe_dict)

        response = (
            f"<b>🔢 Калькулятор</b>\n\n"
            f"<b>📝 Запрос:</b> <code>{expression}</code>\n"
            f"<b>✅ Результат:</b> <code>{result}</code>"
        )
        
        await edit_or_reply(event, response, parse_mode='HTML')

    except Exception as e:
        await edit_or_reply(event, f"<b>❌ Ошибка:</b>\n<code>{str(e)}</code>", parse_mode='HTML')