from aiogram.types import ReplyKeyboardMarkup, KeyboardButton  # Importam clasele pentru tastatura reply si butoanele de tastatura din aiogram

def main_menu(language: str, test_completed: bool = False):  # Definim functia care creeaza meniul principal in functie de limba si starea testului
    if language == "ro":  # Verificam daca limba selectata este romana
        keyboard = []  # Initializam o lista goala pentru butoanele tastaturii
        # if test_completed:
        #     keyboard.append(KeyboardButton(text="📄 Raport PDF"))
        keyboard.append(KeyboardButton(text="📝 Începe testul"))  # Adaugam butonul "Incepe testul" in limba romana
        return ReplyKeyboardMarkup(  # Returnam tastatura reply cu butoanele configurate
            keyboard=[keyboard],  # Setam butoanele tastaturii (un singur rand)
            resize_keyboard=True  # Activam redimensionarea tastaturii pentru a se adapta la ecran
        )
    else:  # Daca limba selectata este rusa (sau orice alta limba)
        keyboard = []  # Initializam o lista goala pentru butoanele tastaturii
        # if test_completed:
        #     keyboard.append(KeyboardButton(text="📄 PDF отчёт"))
        keyboard.append(KeyboardButton(text="📝 Начать тест"))  # Adaugam butonul "Incepe testul" in limba rusa
        return ReplyKeyboardMarkup(  # Returnam tastatura reply cu butoanele configurate
            keyboard=[keyboard],  # Setam butoanele tastaturii (un singur rand)
            resize_keyboard=True  # Activam redimensionarea tastaturii pentru a se adapta la ecran
        )
