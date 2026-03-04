from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton  # Importam clasele pentru tastatura inline si butoanele inline din aiogram

def yes_no_keyboard(language: str):  # Definim functia care creeaza tastatura inline cu optiunile Da/Nu/Nu stiu in functie de limba
    texts = {  # Definim dictionarul cu textele butoanelor in ambele limbi
        "ro": ("✅ Da", "❌ Nu", "🤷‍♂️ Nu știu",),  # Textele butoanelor in limba romana (Da, Nu, Nu stiu)
        "ru": ("✅ Да", "❌ Нет", "🤷‍♂️ Не знаю")  # Textele butoanelor in limba rusa (Da, Nu, Nu stiu)
    }

    yes_text, no_text, i_dont_know_text = texts.get(language, texts["ro"])  # Extragem textele butoanelor pentru limba selectata, cu romana ca limba implicita

    return InlineKeyboardMarkup(  # Returnam un obiect InlineKeyboardMarkup (tastatura inline)
        inline_keyboard=[  # Definim lista de randuri de butoane ale tastaturii
            [  # Primul rand de butoane (contine toate cele 3 optiuni)
                InlineKeyboardButton(text=yes_text, callback_data="answer_yes"),  # Butonul "Da" cu callback "answer_yes"
                InlineKeyboardButton(text=no_text, callback_data="answer_no"),  # Butonul "Nu" cu callback "answer_no"
                InlineKeyboardButton(text=i_dont_know_text, callback_data="answer_idk")  # Butonul "Nu stiu" cu callback "answer_idk"
            ]
        ]
    )
