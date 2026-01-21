from aiogram import Router, F
from aiogram.types import CallbackQuery
from bd_sqlite.crud import (
    get_user_by_telegram_id,
    get_question_by_index,
    save_answer
)
from bot.tastatura.testButton import yes_no_keyboard
from bot.gestionari. import user_question_index

router = Router()

@router.callback_query(F.data.in_(["answer_yes", "answer_no"]))
async def handle_answer(callback: CallbackQuery):
    user = await get_user_by_telegram_id(callback.from_user.id)
    index = user_question_index.get(user.telegram_id, 0)

    question = await get_question_by_index(index, user.language)

    value = "da" if callback.data == "answer_yes" else "nu"
    await save_answer(user.id, question.id, value)

    # next question
    user_question_index[user.telegram_id] += 1
    next_q = await get_question_by_index(
        user_question_index[user.telegram_id],
        user.language
    )

    if not next_q:
        await callback.message.answer("✅ Test finalizat")
        return

    await callback.message.answer(
        next_q.text,
        reply_markup=yes_no_keyboard(user.language)
    )
