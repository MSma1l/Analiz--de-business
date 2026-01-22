from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy import update
from bot.tastatura.limba import language_keyboard
from bot.tastatura.testButton import yes_no_keyboard
from bot.tastatura.meniuButton import main_menu
from bd_sqlite.fuction_bd import (
    get_or_create_user,
    set_user_language,
    get_user_by_telegram_id,
    get_current_question
)
from bd_sqlite.conexiune import async_session
from bd_sqlite.models import User
from logica.State import CabinetState
from aiogram.fsm.context import FSMContext




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


    # setează limba + reset index în DB
    await set_user_language(message.from_user.id, language)

    user = await get_user_by_telegram_id(message.from_user.id)

    
    texts = {
        "ro": "✅ Limba setată. Alege o opțiune:",
        "ru": "✅ Язык установлен. Выберите опцию:"
    }
    # await message.answer(texts.get(language, texts["ro"]))

    
    await message.answer(
        texts[language],
        reply_markup=main_menu(language)
    )

@router.message(F.text.in_(["📝 Începe testul", "📝 Начать тест"]))
async def start_test(message:Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    
    question =await get_current_question(
    user.current_index,
    user.language
    )
    
    
    if not question:
        await message.answer("❌ Nu există întrebări")
        return
    
    await message.answer(
        question.text,
        reply_markup=yes_no_keyboard(user.language)
    )
   
@router.message(F.text.in_(["📊 Cabinetul Personal", "📊 Личный кабинет"]))
async def cabinet_personal(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)

    if not user:
        return

    if not user.company_name:
        texts = {
            "ro": "🏢 Introdu numele companiei tale:",
            "ru": "🏢 Введите название вашей компании:"
        }

        await message.answer(texts[user.language])
        await state.set_state(CabinetState.waiting_company_name)
        return

    await show_cabinet(message, user)


@router.message(CabinetState.waiting_company_name)
async def save_company_name(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)

    if not user:
        return

    company_name = message.text.strip()

    if len(company_name) < 2:
        await message.answer(
            "❌ Numele companiei trebuie să aibă cel puțin 2 caractere"
            if user.language == "ro"
            else "❌ Название компании слишком короткое"
        )
        return

    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.id == user.id)
            .values(company_name=company_name)
        )
        await session.commit()

    await state.clear()  # 🔴 OBLIGATORIU

    texts = {
        "ro": f"✅ Compania **{company_name}** a fost salvată.\n\n📊 Cabinetul tău:",
        "ru": f"✅ Компания **{company_name}** сохранена.\n\n📊 Ваш кабинет:"
    }

    await message.answer(texts[user.language], parse_mode="Markdown")

    user.company_name = company_name  # 🔧 update local
    await show_cabinet(message, user)


async def show_cabinet(message: Message, user):
    texts = {
        "ro": (
            f"🏢 Companie: {user.company_name}\n"
            f"📊 Scor: {user.score if user.score is not None else '—'}%\n"
            f"📝 Test: {'Finalizat' if user.test_completed else 'Neînceput'}\n\n"
            "📄 Raportul va fi disponibil în curând."
        ),
        "ru": (
            f"🏢 Компания: {user.company_name}\n"
            f"📊 Оценка: {user.score if user.score is not None else '—'}%\n"
            f"📝 Тест: {'Завершён' if user.test_completed else 'Не начат'}\n\n"
            "📄 Отчёт скоро будет доступен."
        )
    }

    await message.answer(texts[user.language])
