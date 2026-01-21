from aiogram import Router, F
from aiogram.types import CallbackQuery
from bd_sqlite.fuction_bd import (
    get_user_by_telegram_id,
    get_question_by_index,
    save_answer
)
from bot.tastatura.testButton import yes_no_keyboard

router = Router()

user_question_index = {}  # telegram_id -> index

@router.callback_query(F.data == "start_test")
async def start_test(callback: CallbackQuery):
    user = await get_user_by_telegram_id(callback.from_user.id)
    user_question_index[user.telegram_id] = 0

    question = await get_question_by_index(0, user.language)
    await callback.message.answer(
        question.text,
        reply_markup=yes_no_keyboard(user.language)
    )
