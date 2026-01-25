from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def locatie_keyboard(language: str):
    if language == "ro":
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
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📍 Наше местоположение",
                        url="https://maps.google.com/?q=Strada+Alexei+Șciusev+29+Chișinău"
                    )
                ]
            ]
        )
