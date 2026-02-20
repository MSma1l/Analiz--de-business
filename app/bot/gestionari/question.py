from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy import select, func
from bd_sqlite.fuction_bd import (
    get_user_by_telegram_id,
    get_current_question,
    get_questions_per_category
)
from bd_sqlite.conexiune import async_session
from bd_sqlite.models import Intrebare
from bot.tastatura.testButton import yes_no_keyboard

router = Router()


@router.message(F.text.in_(["📝 Începe testul", "📝 Начать тест", "📝 Test", "📝 Тест"]))
async def start_test(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    question = await get_current_question(user.current_index, user.language)

    if not question:
        await message.answer("❌ Nu există întrebări")
        return

    # Trimitem numele blocului prima dată
    await message.answer(f"📌 *{question.categorie}*", parse_mode="Markdown")

    # Calculăm index_in_bloc
    async with async_session() as session:
        stmt = (
            select(func.min(Intrebare.index))
            .where(
                Intrebare.categorie == question.categorie,
                Intrebare.language == user.language
            )
        )
        result = await session.execute(stmt)
        primul_index = result.scalar_one()

    totale = await get_questions_per_category(user.language)
    index_in_bloc = question.index - primul_index + 1
    total_bloc = totale.get(question.categorie, "?")

    await message.answer(
        f"`{index_in_bloc}/{total_bloc}`\n\n{question.text}",
        reply_markup=yes_no_keyboard(user.language),
        parse_mode="Markdown"
    )
