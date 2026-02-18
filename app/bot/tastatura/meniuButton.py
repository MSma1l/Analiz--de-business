from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu(language: str):
    if language == "ro":
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    # KeyboardButton(text="👤 Cabinet personal"),
                    KeyboardButton(text="📝 Începe testul")
                ]
            ],
            resize_keyboard=True
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    # KeyboardButton(text="👤 Личный кабинет"),
                    KeyboardButton(text="📝 Начать тест")
                ]
            ],
            resize_keyboard=True
        )
