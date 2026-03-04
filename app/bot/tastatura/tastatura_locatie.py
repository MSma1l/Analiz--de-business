from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton  # Importam clasele pentru tastatura inline si butoanele inline din aiogram

def locatie_keyboard(language: str):  # Definim functia care creeaza tastatura inline cu butonul de locatie in functie de limba
    if language == "ro":  # Verificam daca limba selectata este romana
        return InlineKeyboardMarkup(  # Returnam un obiect InlineKeyboardMarkup (tastatura inline) pentru romana
            inline_keyboard=[  # Definim lista de randuri de butoane ale tastaturii
                [  # Primul rand de butoane (contine un singur buton)
                    InlineKeyboardButton(  # Cream un buton inline
                        text="📍 Deschide locația",  # Textul butonului in limba romana
                        url="https://maps.google.com/?q=Strada+Alexei+Șciusev+29+Chișinău"  # URL-ul Google Maps catre adresa companiei
                    )
                ]
            ]
        )
    else:  # Daca limba selectata este rusa (sau orice alta limba)
        return InlineKeyboardMarkup(  # Returnam un obiect InlineKeyboardMarkup (tastatura inline) pentru rusa
            inline_keyboard=[  # Definim lista de randuri de butoane ale tastaturii
                [  # Primul rand de butoane (contine un singur buton)
                    InlineKeyboardButton(  # Cream un buton inline
                        text="📍 Наше местоположение",  # Textul butonului in limba rusa
                        url="https://maps.google.com/?q=Strada+Alexei+Șciusev+29+Chișinău"  # URL-ul Google Maps catre adresa companiei
                    )
                ]
            ]
        )
