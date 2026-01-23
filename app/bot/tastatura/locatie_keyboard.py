from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def locatie_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📍 Deschide locația",
                    url="https://maps.google.com/?q=Strada+Alexei+Șciusev+29+Chișinău"
                )
            ]
        ]
    )
