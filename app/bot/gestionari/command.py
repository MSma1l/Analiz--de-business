from aiogram import Router, F
from aiogram.types import Message
from bd_sqlite.fuction_bd import get_user_by_telegram_id
from bot.tastatura.meniuButton import main_menu
from bd_sqlite.models import User

router = Router()


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
        reply_markup= main_menu(language=user.language, test_completed=User.test_completed)
    ) 