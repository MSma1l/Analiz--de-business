from aiogram import Router, F  # Importam clasa Router si filtrul F din biblioteca aiogram
from aiogram.types import Message  # Importam tipul Message pentru gestionarea mesajelor primite
from bd_sqlite.functii_bd import (  # Importam functiile de lucru cu baza de date
    get_user_by_telegram_id,  # Functia care obtine un utilizator dupa ID-ul Telegram din baza de date
    get_current_question,  # Functia care obtine intrebarea curenta din baza de date dupa index si limba
)
from bot.tastatura.tastatura_test import yes_no_keyboard  # Importam functia care genereaza tastatura cu butoanele Da/Nu pentru test

router = Router()  # Cream o instanta de Router pentru a inregistra handler-ele din acest fisier

TOTAL_INTREBARI = 33  # Definim constanta cu numarul total de intrebari din test


@router.message(F.text.in_(["📝 Începe testul", "📝 Начать тест", "📝 Test", "📝 Тест"]))  # Decoratorul care inregistreaza handler-ul pentru butoanele de pornire a testului (in romana si rusa)
async def start_test(message: Message):  # Definim functia asincrona care se executa cand utilizatorul apasa pe butonul de start al testului
    user = await get_user_by_telegram_id(message.from_user.id)  # Obtinem obiectul utilizatorului din baza de date dupa ID-ul Telegram

    question = await get_current_question(user.current_index, user.language)  # Obtinem intrebarea curenta din baza de date pe baza indexului curent al utilizatorului si a limbii selectate

    if not question:  # Verificam daca intrebarea nu a fost gasita in baza de date
        await message.answer("❌ Nu există întrebări")  # Trimitem un mesaj de eroare daca nu exista intrebari disponibile
        return  # Iesim din functie deoarece nu avem intrebare de afisat

    await message.answer(f"📌 *{question.categorie}*", parse_mode="Markdown")  # Trimitem un mesaj cu categoria intrebarii curente formatata bold in Markdown

    # Folosim direct question.index care e 1-based în DB (1, 2, 3... 33)
    await message.answer(  # Trimitem mesajul cu intrebarea propriu-zisa catre utilizator
        f"`{question.index}/{TOTAL_INTREBARI}`\n\n{question.text}",  # Formatam textul cu numarul intrebarii din total si textul intrebarii
        reply_markup=yes_no_keyboard(user.language),  # Atasam tastatura inline cu butoanele Da/Nu in limba utilizatorului
        parse_mode="Markdown"  # Setam modul de parsare Markdown pentru formatarea textului
    )
