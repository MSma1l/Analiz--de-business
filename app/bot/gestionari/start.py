from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from bot.tastatura.limba import language_keyboard
from bot.tastatura.meniuButton import main_menu
from bd_sqlite.fuction_bd import (
    get_or_create_user,
    set_user_language,
    get_user_by_telegram_id,
)
from bd_sqlite.models import User

router = Router()


@router.message(CommandStart())
async def start_bot(message: Message):
    await get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )

    await message.answer(
        "Bun venit! Mă numesc BizzCheck \nДобро пожаловать! Меня зовут BizzCheck \n\nAlegeți limba / Выберите язык:",
        reply_markup=language_keyboard()
    )

@router.message(F.text.in_(["/info"]))
async def info_command(message: Message):
    user =  await get_user_by_telegram_id(message.from_user.id)
    language = user.language if user and user.language else "ro"
    
    textss = {
        "ro": "Acest bot a fost creat pentru a oferi o perspectivă rapidă și inteligentă asupra afacerii tale. Pe baza răspunsurilor introduse, sistemul analizează datele și stabilește nivelul de dezvoltare al businessului. \nÎn plus, utilizatorul poate vizualiza rezultatele sub formă de rapoarte clare și comparații relevante, obținând astfel o înțelegere mai bună a situației economice.",
        "ru": """Этот бот был создан для того, чтобы предоставить быстрый и интеллектуальный обзор вашего бизнеса. На основе введённых ответов система анализирует данные и определяет уровень развития компании.
Кроме того, пользователь может просматривать результаты в виде наглядных отчётов и релевантных сравнений, получая тем самым более полное понимание экономической ситуации."""
    }
    
    await message.answer(
        textss[language],
        reply_markup=main_menu(language=user.language, test_completed=User.test_completed)
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
        reply_markup=main_menu(language=user.language, test_completed=User.test_completed)
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
        reply_markup=main_menu(language=user.language, test_completed=User.test_completed)
    ) 
    
@router.callback_query(F.data.in_(["lang_ro", "lang_ru"]))
async def language_selected(callback: CallbackQuery):
    language = "ro" if callback.data == "lang_ro" else "ru"

    await set_user_language(callback.from_user.id, language)

    user = await get_user_by_telegram_id(callback.from_user.id)

    
    texts = {
        "ro": """🏢 BizzCheck Bot

    Bine ai venit în centrul tău de analiză!
    📈 Analiza performanței afacerii
    📊 Evaluarea stării businessului
    📋 Rapoarte și comparații inteligente""",
        "ru": """🏢 BizzCheck Bot

    Добро пожаловать в центр бизнес-анализа!
    📈 Анализ эффективности бизнеса
    📊 Оценка состояния компании
    📋 Умные отчёты и сравнения"""
    }

    await callback.message.answer(
        texts[language],
        reply_markup=main_menu(language=user.language, test_completed=User.test_completed)
    )
    
    await callback.answer()  
    
