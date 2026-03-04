from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton  # Importam clasele pentru tastatura inline si butoanele inline din aiogram


def language_keyboard():  # Definim functia care creeaza tastatura inline pentru selectarea limbii
    return InlineKeyboardMarkup(  # Returnam un obiect InlineKeyboardMarkup (tastatura inline)
        inline_keyboard=[  # Definim lista de randuri de butoane ale tastaturii
            [  # Primul rand de butoane (contine ambele optiuni de limba)
            InlineKeyboardButton(text="Română", callback_data="lang_ro"),  # Butonul pentru selectarea limbii romane cu callback "lang_ro"
            InlineKeyboardButton(text="Русский", callback_data="lang_ru")  # Butonul pentru selectarea limbii ruse cu callback "lang_ru"
            ]
        ],
    )
