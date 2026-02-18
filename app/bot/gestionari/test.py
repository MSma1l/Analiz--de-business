from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
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

# Etichete vizuale pentru răspunsuri
ANSWER_LABELS = {
    "answer_yes": {"ro": "✅ Da",    "ru": "✅ Да"},
    "answer_no":  {"ro": "❌ Nu",    "ru": "❌ Нет"},
    "answer_idk": {"ro": "🤷 Nu știu", "ru": "🤷 Не знаю"},
}

def selected_keyboard(chosen: str, language: str) -> InlineKeyboardMarkup:
    """
    Returnează un keyboard cu un singur buton — alegerea făcută,
    evidențiată vizual. Celelalte butoane dispar.
    """
    label = ANSWER_LABELS.get(chosen, {}).get(language, chosen)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=label, callback_data="done")]
    ])


@router.callback_query(F.data == "done")
async def handle_done(callback: CallbackQuery):
    """Ignorăm click-urile pe butonul 'ales' deja."""
    await callback.answer()


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
        "answer_no":  "NO",
        "answer_idk": "IDK"
    }
    valoare = mapping.get(callback.data)

    # ① Edităm mesajul curent: păstrăm textul întrebării,
    #    dar înlocuim keyboard-ul cu butonul ales (inactiv vizual)
    try:
        await callback.message.edit_reply_markup(
            reply_markup=selected_keyboard(callback.data, user.language)
        )
    except Exception:
        pass  # dacă mesajul nu mai poate fi editat, continuăm oricum

    # Confirmăm imediat callback-ul → dispare "loading"
    await callback.answer()

    # SALVĂM RĂSPUNSUL
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
        # ② FINAL TEST
        rezultat  = await finalize_test(user.id)
        rezultate = rezultat[0]
        language  = rezultat[1]

        raport_text = format_report(rezultate, language)
        await callback.message.answer(raport_text, parse_mode="Markdown")
        return

    # ③ Trimitem MESAJ NOU cu următoarea întrebare
    await callback.message.answer(
        next_q.text,
        reply_markup=yes_no_keyboard(user.language)
    )
