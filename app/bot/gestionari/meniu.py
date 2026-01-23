from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import update
from bd_sqlite.fuction_bd import get_user_by_telegram_id
from bd_sqlite.conexiune import async_session
from bd_sqlite.models import User
from logica.State import CabinetState
from aiogram.fsm.context import FSMContext
from bot.tastatura.cabinet_keyboard import cabinet_keyboard
from sqlalchemy import select, desc
from bot.tastatura.locatie_keyboard import locatie_keyboard


router = Router()

@router.message(F.text.in_(["👤 Cabinet personal", "👤 Личный кабинет"]))
async def cabinet_personal(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    texts = {
        "ro": "📊 Cabinetul personal:",
        "ru": "📊 Личный кабинет:"
    }

    await message.answer(
        texts[user.language],
        reply_markup=cabinet_keyboard(user.language)
    )

@router.message(F.text.in_(["➕ Adaugă compania", "➕ Добавить компанию"]))
async def add_company_start(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)

    texts = {
        "ro": "🏢 Introdu numele companiei:",
        "ru": "🏢 Введите название компании:"
    }

    await state.set_state(CabinetState.waiting_company_name)
    await message.answer(texts[user.language])

@router.message(CabinetState.waiting_company_name)
async def save_company_name(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)

    company_name = message.text.strip()

    if len(company_name) < 2:
        await message.answer(
            "❌ Numele companiei este prea scurt"
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

    await state.clear()

    texts = {
        "ro": f"✅ Compania **{company_name}** a fost salvată.",
        "ru": f"✅ Компания **{company_name}** сохранена."
    }

    await message.answer(
        texts[user.language],
        reply_markup=cabinet_keyboard(user.language),
        parse_mode="Markdown"
    )

@router.message(F.text.in_(["📊 Vezi poziția companiei", "📊 Позиция компании"]))
async def company_position(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    # dacă nu a terminat testul
    if not user.test_completed or user.score is None:
        await message.answer(
            "❌ Mai întâi trebuie să finalizezi testul."
            if user.language == "ro"
            else "❌ Сначала нужно пройти тест."
        )
        return

    async with async_session() as session:
        # luăm toate companiile cu scor
        result = await session.execute(
            select(User)
            .where(User.company_name.isnot(None))
            .where(User.score.isnot(None))
            .where(User.test_completed == True)
            .order_by(desc(User.score))
        )
        users = result.scalars().all()

    if not users:
        await message.answer("Nu există date pentru clasament.")
        return

    top5 = users[:5]

    position = next(
        (i + 1 for i, u in enumerate(users) if u.id == user.id),
        None
    )

    if user.language == "ro":
        text = "🏆 TOP 5 companii:\n\n"
        for i, u in enumerate(top5, start=1):
            text += f"{i}. {u.company_name} — {u.score}%\n"

        text += f"\n📍 Compania ta este pe locul {position} din {len(users)}."
    else:
        text = "🏆 ТОП 5 компаний:\n\n"
        for i, u in enumerate(top5, start=1):
            text += f"{i}. {u.company_name} — {u.score}%\n"

        text += f"\n📍 Ваша компания на месте {position} из {len(users)}."

    await message.answer(text)


@router.message(F.text.in_(["💬 Contacte","💬 Контакты"]))
async def contacte(message:Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    
    
    contacte = {
    "ro": "📩 Contacte:\n\n📞 Telefon: +373 XXX XXXXX\n\n✉️ Email: support@gmail.com",
    "ru": "📩 Контакты:\n\n📞 Телефон: +373 XXX XXXXX\n\n✉️ Email: support@gmail.com"
    }
    
    await message.answer(
        contacte[user.language],
        reply_markup= locatie_keyboard()
        )
