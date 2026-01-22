from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def yes_no_keyboard(language: str):
    texts = {
        "ro": ("✅ Da", "❌ Nu"),
        "ru": ("✅ Да", "❌ Нет")
    }

    yes_text, no_text = texts.get(language, texts["ro"])

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=yes_text, callback_data="answer_yes"),
                InlineKeyboardButton(text=no_text, callback_data="answer_no")
            ]
        ]
    )
