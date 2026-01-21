from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from bot.tastatura.limba import language_keyboard
from bd_sqlite.fuction_bd import get_or_create_user, set_user_language

router = Router()


@router.message(CommandStart())
async def start_bot(message: Message):
    await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    await message.answer(
        "Bun venit! / Добро пожадовать!\n\n Alege limba / Выберите язык: ",
        reply_markup=language_keyboard()
    )

@router.message(F.text.in_(["🇷🇴 Română", "🇷🇺 Русский"]))
async def language_selected(message:Message):
    language =  "ro" if "Română" in message.text else "ru"
    
    await set_user_language(
        telegram_id=message.from_user.id,
        language=language
    )
    await message.answer(
                "✅ Limba a fost setată.\n\nÎncepem testul 🚀",
        reply_markup=None
    )