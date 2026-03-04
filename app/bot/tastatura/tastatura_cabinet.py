from aiogram.types import ReplyKeyboardMarkup, KeyboardButton  # Importam clasele pentru tastatura reply si butoanele de tastatura din aiogram

def cabinet_keyboard(language: str, test_completed: bool= False):  # Definim functia care creeaza tastatura cabinetului personal in functie de limba si starea testului
    if language == "ro":  # Verificam daca limba selectata este romana
        buttons = [  # Initializam lista de randuri de butoane pentru limba romana
            [  # Primul rand de butoane
                KeyboardButton(text="➕ Adaugă compania"),  # Butonul pentru adaugarea companiei in romana
                KeyboardButton(text="📊 Vezi poziția companiei")  # Butonul pentru vizualizarea pozitiei companiei in romana
            ],
            [  # Al doilea rand de butoane
                KeyboardButton(text="💬 Contacte"),  # Butonul pentru contacte in romana
            ],
        ]
        if not test_completed:  # Verificam daca testul nu a fost inca finalizat
            buttons.append([KeyboardButton(text="📝 Test")])  # Adaugam butonul "Test" daca testul nu este completat

    else:  # Daca limba selectata este rusa (sau orice alta limba)
        buttons = [  # Initializam lista de randuri de butoane pentru limba rusa
            [  # Primul rand de butoane
                KeyboardButton(text="➕ Добавить компанию"),  # Butonul pentru adaugarea companiei in rusa
                KeyboardButton(text="📊 Позиция компании")  # Butonul pentru vizualizarea pozitiei companiei in rusa
            ],
            [  # Al doilea rand de butoane
                KeyboardButton(text="💬 Контакты"),  # Butonul pentru contacte in rusa
            ],
        ]
        if not test_completed:  # Verificam daca testul nu a fost inca finalizat
            buttons.append(  # Adaugam un rand nou de butoane
            [KeyboardButton(text="📝 Тест")])  # Butonul "Test" in rusa daca testul nu este completat


    return ReplyKeyboardMarkup(  # Returnam tastatura reply cu butoanele configurate
        keyboard=buttons,  # Setam butoanele tastaturii
        resize_keyboard=True  # Activam redimensionarea tastaturii pentru a se adapta la ecran
    )
