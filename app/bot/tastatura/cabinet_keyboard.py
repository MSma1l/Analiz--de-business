from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def cabinet_keyboard(language: str):
    if language == "ro":
        buttons = [
            [
                KeyboardButton(text="➕ Adaugă compania"),
                KeyboardButton(text="📊 Vezi poziția companiei")
            ],
            [
                KeyboardButton(text="💬 Contacte"),
                KeyboardButton(text="📄 Raport PDF")
            ],
            [KeyboardButton(text="📝 Test")]
        ]
    else:
        buttons = [
            [
                KeyboardButton(text="➕ Добавить компанию"),
                KeyboardButton(text="📊 Позиция компании")
            ],
            [
                KeyboardButton(text="💬 Контакты"),
                KeyboardButton(text="📄 PDF отчёт")
            ],
            [KeyboardButton(text="📝 Тест")]
        ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
