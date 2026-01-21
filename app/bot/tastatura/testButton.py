from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def yes_no_keyboard(language: str):
    if language == "ro":
        yes, no = "Da", "Nu"
    else:
        yes, no = "Да", "Нет"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=yes, callback_data="answer_yes"),
            InlineKeyboardButton(text=no, callback_data="answer_no")
        ]
    ])
