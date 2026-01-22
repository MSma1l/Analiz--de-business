from aiogram import Router, F
from aiogram.types import CallbackQuery
from bd_sqlite.fuction_bd import (
    get_user_by_telegram_id,
    get_current_question
)
from bot.tastatura.testButton import yes_no_keyboard

router = Router()


@router.callback_query(F.data == "start_test")
async def start_test(callback: CallbackQuery):
    user = await get_user_by_telegram_id(callback.from_user.id)

    if not user:
        await callback.message.answer("Eroare utilizator")
        return

    question = await get_current_question(
        user.current_index,
        user.language
    )

    if not question:
        msg = "Nu există întrebări" if user.language == "ro" else "Нет вопросов"
        await callback.message.answer(msg)
        return

    await callback.message.answer(
        question.text,
        reply_markup=yes_no_keyboard(user.language)
    )
