from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.tastatura.limba import language_keyboard
from bot.tastatura.meniuButton import main_menu
from bd_sqlite.fuction_bd import (
    get_or_create_user,
    set_user_language,
    get_user_by_telegram_id,
)

router = Router()


@router.message(CommandStart())
async def start_bot(message: Message):
    await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )

    await message.answer(
        "Bun venit! / Добро пожаловать!\n\nAlege limba / Выберите язык:",
        reply_markup=language_keyboard()
    )

    
@router.message(F.text.in_(["🇷🇴 Română", "🇷🇺 Русский"]))
async def language_selected(message: Message):
    language = "ro" if "Română" in message.text else "ru"

    await set_user_language(message.from_user.id, language)

    user = await get_user_by_telegram_id(message.from_user.id)

    
    texts = {
        "ro": "✅ Limba setată. Alege o opțiune:",
        "ru": "✅ Язык установлен. Выберите опцию:"
    }

    
    await message.answer(
        texts[language],
        reply_markup=main_menu(language)
    )
    
