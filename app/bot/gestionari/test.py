from aiogram import Router, F
from aiogram.types import CallbackQuery
from bd_sqlite.fuction_bd import (
    save_answer,
    get_user_by_telegram_id,
    get_current_question,
    finalize_test,
    format_report
)
from bd_sqlite.conexiune import async_session
from bd_sqlite.models import User
from bot.tastatura.testButton import yes_no_keyboard

router = Router()


@router.callback_query(F.data.startswith("answer_"))
async def handle_answer(callback: CallbackQuery):
    user = await get_user_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Eroare utilizator", show_alert=True)
        return

    question = await get_current_question(user.current_index, user.language)
    if not question:
        await callback.answer("Nu s-a găsit întrebare", show_alert=True)
        return

    # MAPARE RĂSPUNS
    mapping = {
        "answer_yes": "YES",
        "answer_no": "NO",
        "answer_idk": "IDK"
    }
    valoare = mapping.get(callback.data)

    # salvăm răspunsul
    await save_answer(user.id, question.id, valoare)

    # INCREMENTARE INDEX
    user.current_index += 1
    async with async_session() as session:
        await session.execute(
            User.__table__.update()
            .where(User.id == user.id)
            .values(current_index=user.current_index)
        )
        await session.commit()

        # URMĂTOAREA ÎNTREBARE
        next_q = await get_current_question(user.current_index, user.language)
        if not next_q:
            # 🔥 FINAL TEST
            rezultate = await finalize_test(user.id)
            raport = format_report(rezultate)
            await callback.message.answer(raport)
            return

        # actualizăm mesajul existent cu următoarea întrebare
        await callback.message.edit_text(
            next_q.text,
            reply_markup=yes_no_keyboard(user.language)
        )

        # confirmăm callback-ul pentru a elimina “loading” la apăsare
        await callback.answer(cache_time=0)

