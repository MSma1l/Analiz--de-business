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

@router.message(F.text.in_(["/help"]))
async def help_command(message: Message):
    user =  await get_user_by_telegram_id(message.from_user.id)
    language = user.language if user and user.language else "ro"
    
    textss = {
        "ro": "Pentru asistență, vă rugăm să contactați suportul nostru la",
        "ru": "Для получения помощи, пожалуйста, свяжитесь с нашей службой поддержки по адресу"
    }
    
    await message.answer(
        textss[language],
        reply_markup=main_menu(language)
    )
   
@router.message(F.text.in_(["/about"]))
async def about_command(message: Message):
    user =  await get_user_by_telegram_id(message.from_user.id)
    language = user.language if user and user.language else "ro"
    
    textss = {
        "ro": "CROWE TURCAN MIKHAILENKO — din anul 2023 face parte din grupul internațional Crowe Global. Fondată în 1915, Crowe se numără astăzi printre primele 10 cele mai mari rețele globale de servicii profesionale.Oferim soluții avansate în domeniul fiscalității și consultanței juridice, ajutând antreprenorii să atingă noi culmi ale succesului.",
        "ru": "CROWE TURCAN MIKHAILENKO — с 2023 года является частью международной группы Crowe Global. Основанная в 1915 году, Crowe сегодня входит в топ-10 крупнейших глобальных сетей профессиональных услуг.Мы предоставляем передовые решения в области налогообложения и юридического консалтинга, помогая предпринимателям достигать новых вершин успеха."
    }
    
    await message.answer(
        textss[language],
        reply_markup=main_menu(language)
    ) 
    
@router.message(F.text.in_(["Română", "Русский"]))
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
    
