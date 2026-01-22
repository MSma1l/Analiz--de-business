from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import update
from logica.scorul import calculate_score
from bd_sqlite.fuction_bd import (
    get_user_by_telegram_id,
    get_current_question,
    save_answer
)
from bd_sqlite.conexiune import async_session
from bd_sqlite.models import User
from bot.tastatura.testButton import yes_no_keyboard

router = Router()

@router.callback_query(F.data.in_(["answer_yes", "answer_no"]))
async def handle_answer(callback: CallbackQuery):
    user = await get_user_by_telegram_id(callback.from_user.id)

    if not user:
        await callback.answer("Eroare utilizator", show_alert=True)
        return

    question = await get_current_question(
        user.current_index,
        user.language
    )

    if not question:
        texts = {
            "ro": "✅ Test finalizat!\n📊 Raportul va fi disponibil în curând.",
            "ru": "✅ Тест завершён!\n📊 Отчёт скоро будет доступен."
        }
        await callback.message.edit_text(texts[user.language])
        return

    # salvăm răspunsul
    value = callback.data == "answer_yes"
    await save_answer(user.id, question.id, value)

    # calculăm noul index
    next_index = user.current_index + 1

    # salvăm indexul în DB
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.id == user.id)
            .values(current_index=next_index)
        )
        await session.commit()

    # următoarea întrebare
    next_question = await get_current_question(
        next_index,
        user.language
    )

    if not next_question:
        score = await calculate_score(user.id)

        async with async_session() as session:
            await session.execute(
                update(User)
                .where(User.id == user.id)
                .values(
                    test_completed=True,
                    score=score
                )
            )
            await session.commit()

        texts = {
            "ro": (
                f"✅ Test finalizat!\n\n"
                f"📊 Scorul tău: {score}%\n"
                f"Raportul detaliat va apărea în curând "
                f"în cabinetul tău personal."
            ),
            "ru": (
                f"✅ Тест завершён!\n\n"
                f"📊 Ваш результат: {score}%\n"
                f"Подробный отчёт скоро появится "
                f"в личном кабинете."
            )
        }

        await callback.message.edit_text(texts[user.language])
        return

    # 👇 EDITĂM mesajul, NU trimitem unul nou
    await callback.message.edit_text(
        next_question.text,
        reply_markup=yes_no_keyboard(user.language)
    )

    await callback.answer()
