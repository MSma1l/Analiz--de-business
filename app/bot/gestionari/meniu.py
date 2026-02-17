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
        reply_markup=cabinet_keyboard(user.language,
                                      test_completed=user.test_completed
        )
    )

@router.message(F.text.in_(["➕ Adaugă compania", "➕ Добавить компанию"]))
async def add_company_start(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)

    texts_company = {
        "ro": "🏢 Introdu numele companiei:",
        "ru": "🏢 Введите название компании:"
    }

    await state.set_state(CabinetState.waiting_company_name)
    await message.answer(texts_company[user.language])

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

    await state.update_data(company_name=company_name)

    texts_number = {
        "ro": "📞 Introdu numărul companiei:",
        "ru": "📞 Введите номер компании:"
    }

    await state.set_state(CabinetState.waiting_company_number)
    await message.answer(texts_number[user.language])

@router.message(CabinetState.waiting_company_number)
async def save_company_number(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)

    number_company = message.text.strip()

    if len(number_company) < 9:
        await message.answer(
            "❌ Număr invalid"
            if user.language == "ro"
            else "❌ Неверный номер"
        )
        return

    await state.update_data(number_company=number_company)

    texts_email = {
        "ro": "📧 Introdu emailul:",
        "ru": "📧 Введите email:"
    }

    await state.set_state(CabinetState.waiting_company_email)
    await message.answer(texts_email[user.language])

@router.message(CabinetState.waiting_company_email)
async def save_company_email(message: Message, state: FSMContext):
    user = await get_user_by_telegram_id(message.from_user.id)

    email_company = message.text.strip()

    if "@" not in email_company:
        await message.answer(
            "❌ Email invalid"
            if user.language == "ro"
            else "❌ Неверный email"
        )
        return

    data = await state.get_data()

    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.id == user.id)
            .values(
                company_name=data["company_name"],
                number_company=data["number_company"],
                email_company=email_company
            )
        )
        await session.commit()

    await state.clear()

    texts = {
        "ro": f"✅ Compania a fost salvată:\n🏢 {data['company_name']}\n📞 {data['number_company']}\n📧 {email_company}",
        "ru": f"✅ Компания сохранена:\n🏢 {data['company_name']}\n📞 {data['number_company']}\n📧 {email_company}"
    }

    await message.answer(
        texts[user.language],
        reply_markup=cabinet_keyboard(user.language,
                                      test_completed=user.test_completed
        )
    )


@router.message(F.text.in_(["📊 Vezi poziția companiei", "📊 Позиция компании"]))
async def company_position(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

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
    "ro": "📩 Contacte:\n\n📞 Telefon: +373 XXX XXXXX\n\n✉️ Poșta electronică: support@gmail.com",
    "ru": "📩 Контакты:\n\n📞 Телефон: +373 XXX XXXXX\n\n✉️ Электронная почта: support@gmail.com"
    }
    
    await message.answer(
        contacte[user.language],
        reply_markup= locatie_keyboard(user.language)
        )
