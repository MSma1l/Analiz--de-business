from aiogram import Router, F
from aiogram.types import Message
from bd_sqlite.fuction_bd import (
    get_user_by_telegram_id,
    get_current_question
)
from bot.tastatura.testButton import yes_no_keyboard

router = Router()


@router.message(F.text.in_(["📝 Începe testul", "📝 Начать тест","📝 Test","📝 Тест"]))
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