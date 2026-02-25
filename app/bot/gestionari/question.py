from aiogram import Router, F
from aiogram.types import Message
from bd_sqlite.fuction_bd import (
    get_user_by_telegram_id,
    get_current_question,
)
from bot.tastatura.testButton import yes_no_keyboard

router = Router()

TOTAL_INTREBARI = 33


@router.message(F.text.in_(["📝 Începe testul", "📝 Начать тест", "📝 Test", "📝 Тест"]))
async def start_test(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)

    question = await get_current_question(user.current_index, user.language)

    if not question:
        await message.answer("❌ Nu există întrebări")
        return

    await message.answer(f"📌 *{question.categorie}*", parse_mode="Markdown")

    # Folosim direct question.index care e 1-based în DB (1, 2, 3... 33)
    await message.answer(
        f"`{question.index}/{TOTAL_INTREBARI}`\n\n{question.text}",
        reply_markup=yes_no_keyboard(user.language),
        parse_mode="Markdown"
    )