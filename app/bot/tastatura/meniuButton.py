from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu(language: str, test_completed: bool = False):
    if language == "ro":
        keyboard = []
        # if test_completed:
        #     keyboard.append(KeyboardButton(text="📄 Raport PDF"))
        keyboard.append(KeyboardButton(text="📝 Începe testul"))
        return ReplyKeyboardMarkup(
            keyboard=[keyboard],
            resize_keyboard=True
        )
    else:
        keyboard = []
        # if test_completed:
        #     keyboard.append(KeyboardButton(text="📄 PDF отчёт"))
        keyboard.append(KeyboardButton(text="📝 Начать тест"))
        return ReplyKeyboardMarkup(
            keyboard=[keyboard],
            resize_keyboard=True
        )