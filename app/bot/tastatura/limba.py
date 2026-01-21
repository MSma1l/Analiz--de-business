from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇷🇴 Română")],
            [KeyboardButton(text="🇷🇺 Русский")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
