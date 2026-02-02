from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def yes_no_keyboard(language: str):
    texts = {
        "ro": ("✅ Da", "❌ Nu", "🤷‍♂️ Nu știu",),
        "ru": ("✅ Да", "❌ Нет", "🤷‍♂️ Не знаю")
    }

    yes_text, no_text, i_dont_know_text = texts.get(language, texts["ro"])

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=yes_text, callback_data="answer_yes"),
                InlineKeyboardButton(text=no_text, callback_data="answer_no"),
                InlineKeyboardButton(text=i_dont_know_text, callback_data="answer_idk")
            ]
        ]
    )
