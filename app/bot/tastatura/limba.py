from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
            InlineKeyboardButton(text="Română", callback_data="lang_ro"),
            InlineKeyboardButton(text="Русский", callback_data="lang_ru")
            ]
        ],
    )
