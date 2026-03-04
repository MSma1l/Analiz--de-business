import asyncio  # Importam modulul asyncio pentru mecanismul de lock anti-dublu-click
from aiogram import Router, F  # Importam clasa Router si filtrul F din framework-ul aiogram
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile  # Importam tipurile pentru callback, tastatura inline, buton inline si fisiere locale
from bd_sqlite.functii_bd import (  # Importam functiile de lucru cu baza de date
    save_answer_and_advance,  # Functia pentru salvarea raspunsului si avansarea indexului intr-o singura tranzactie
    get_user_by_telegram_id,  # Functia pentru obtinerea utilizatorului dupa ID-ul Telegram
    get_current_question,  # Functia pentru obtinerea intrebarii curente dupa index
)
from .raport import (finalize_test, format_report)  # Importam functiile de finalizare a testului si formatare a raportului
from raport_pdf import build_user_report  # Importam functia de generare a raportului PDF
from bot.tastatura.tastatura_test import yes_no_keyboard  # Importam functia care genereaza tastatura cu Da/Nu/Nu stiu

router = Router()  # Cream o instanta de Router pentru a inregistra handler-ele de callback
TOTAL_INTREBARI = 33  # Definim numarul total de intrebari din test

# ==================== PROTECTIE ANTI-DUBLU-CLICK ====================
_user_locks: dict[int, asyncio.Lock] = {}  # Dictionar cu lock-uri per utilizator — impiedica procesarea simultana a mai multor click-uri


def _get_user_lock(telegram_id: int) -> asyncio.Lock:  # Functia care obtine sau creeaza un lock pentru un utilizator
    if telegram_id not in _user_locks:  # Daca utilizatorul nu are inca un lock creat
        _user_locks[telegram_id] = asyncio.Lock()  # Cream un lock nou pentru acest utilizator
    return _user_locks[telegram_id]  # Returnam lock-ul utilizatorului

ANSWER_LABELS = {  # Dictionar cu etichetele raspunsurilor in ambele limbi (romana si rusa)
    "answer_yes": {"ro": "✅ Da",    "ru": "✅ Да"},  # Eticheta pentru raspunsul "Da"
    "answer_no":  {"ro": "❌ Nu",    "ru": "❌ Нет"},  # Eticheta pentru raspunsul "Nu"
    "answer_idk": {"ro": "🤷 Nu știu", "ru": "🤷 Не знаю"},  # Eticheta pentru raspunsul "Nu stiu"
}

def selected_keyboard(chosen: str, language: str) -> InlineKeyboardMarkup:  # Functia care creeaza o tastatura cu raspunsul selectat de utilizator
    label = ANSWER_LABELS.get(chosen, {}).get(language, chosen)  # Obtinem eticheta raspunsului ales in limba utilizatorului
    return InlineKeyboardMarkup(inline_keyboard=[  # Returnam o tastatura inline cu un singur buton care arata raspunsul ales
        [InlineKeyboardButton(text=label, callback_data="done")]  # Butonul arata textul raspunsului si trimite callback-ul "done"
    ])


@router.callback_query(F.data == "done")  # Handler pentru callback-ul "done" - cand utilizatorul a ales deja un raspuns
async def handle_done(callback: CallbackQuery):  # Functia asincrona care proceseaza apasarea pe butonul deja selectat
    await callback.answer()  # Confirma callback-ul fara a afisa nimic (inchide animatia de incarcare)


@router.callback_query(F.data.startswith("answer_"))  # Handler pentru orice callback care incepe cu "answer_" (Da, Nu, Nu stiu)
async def handle_answer(callback: CallbackQuery):  # Functia asincrona principala care proceseaza raspunsul utilizatorului
    lock = _get_user_lock(callback.from_user.id)  # Obtinem lock-ul pentru acest utilizator

    # --- PROTECTIE ANTI-DUBLU-CLICK ---
    if lock.locked():  # Daca lock-ul e deja ocupat, inseamna ca un alt click se proceseaza acum
        await callback.answer()  # Confirma callback-ul fara actiune (inchide animatia de incarcare)
        return  # Ignoram click-ul duplicat si oprim executia

    async with lock:  # Blocam lock-ul — toate click-urile urmatoare vor fi ignorate pana terminam
        user = await get_user_by_telegram_id(callback.from_user.id)  # Obtinem utilizatorul din baza de date folosind ID-ul Telegram
        if not user:  # Daca utilizatorul nu a fost gasit in baza de date
            await callback.answer("Eroare utilizator", show_alert=True)  # Afisam o alerta cu mesaj de eroare
            return  # Oprim executia functiei

        question = await get_current_question(user.current_index, user.language)  # Obtinem intrebarea curenta pe baza indexului utilizatorului si a limbii
        if not question:  # Daca intrebarea nu a fost gasita in baza de date (testul s-a terminat deja)
            await callback.answer()  # Confirma callback-ul fara actiune
            return  # Oprim executia — nu mai exista intrebari de procesat

        mapping = {  # Dictionar care mapeaza callback-urile la valorile stocate in baza de date
            "answer_yes": "YES",  # Raspunsul "Da" se salveaza ca "YES"
            "answer_no":  "NO",  # Raspunsul "Nu" se salveaza ca "NO"
            "answer_idk": "IDK"  # Raspunsul "Nu stiu" se salveaza ca "IDK"
        }
        valoare = mapping.get(callback.data)  # Extragem valoarea corespunzatoare raspunsului ales din dictionar

        try:  # Incercam sa actualizam tastatura mesajului
            await callback.message.edit_reply_markup(  # Editam tastatura mesajului curent pentru a arata doar raspunsul ales
                reply_markup=selected_keyboard(callback.data, user.language)  # Inlocuim tastatura cu cea care contine doar raspunsul selectat
            )
        except Exception:  # Daca apare o eroare la editarea tastaturii (de ex. mesajul e prea vechi)
            pass  # Ignoram eroarea si continuam executia

        await callback.answer()  # Confirma callback-ul (inchide animatia de incarcare din Telegram)

        # Salvam raspunsul si avansam indexul intr-o singura tranzactie (1 scriere in loc de 2)
        user.current_index += 1  # Crestem indexul intrebarii curente cu 1 pentru a trece la urmatoarea intrebare
        await save_answer_and_advance(user.id, question.id, valoare, user.current_index)  # Salvam raspunsul si actualizam indexul simultan

        # URMĂTOAREA ÎNTREBARE
        next_q = await get_current_question(user.current_index, user.language)  # Obtinem urmatoarea intrebare din baza de date
        if not next_q:  # Daca nu exista urmatoare intrebare, inseamna ca testul s-a terminat
            rezultat    = await finalize_test(user.id)  # Finalizam testul si obtinem rezultatele
            rezultate   = rezultat[0]  # Extragem lista de rezultate (categorie, scor, nivel risc)
            language    = rezultat[1]  # Extragem limba utilizatorului
            raport_text = format_report(rezultate, language)  # Formatam raportul text pentru afisare in Telegram
            await callback.message.answer(raport_text, parse_mode="Markdown")  # Trimitem raportul formatat utilizatorului

            # Generam si trimitem automat raportul PDF
            pdf_path = await build_user_report(  # Generam raportul PDF complet pentru utilizator
                user.id, language,  # ID-ul din BD si limba utilizatorului
                username=user.username or "",  # Transmitem username-ul pentru numele fisierului
                first_name=user.first_name or ""  # Transmitem prenumele pentru numele fisierului
            )
            texts_pdf = {  # Definim mesajele de confirmare pentru PDF in ambele limbi
                "ro": "📊 Raportul tău PDF este gata!",  # Mesajul in romana care insoteste documentul PDF
                "ru": "📊 Ваш PDF отчёт готов!"  # Mesajul in rusa care insoteste documentul PDF
            }
            await callback.message.answer_document(  # Trimitem documentul PDF ca mesaj catre utilizator
                document=FSInputFile(pdf_path),  # Cream un obiect FSInputFile din calea fisierului PDF generat
                caption=texts_pdf[language]  # Adaugam mesajul de confirmare in limba utilizatorului
            )
            return  # Oprim executia functiei dupa trimiterea raportului text si PDF

        # Bloc nou — afișăm numele categoriei
        prev_q = await get_current_question(user.current_index - 1, user.language)  # Obtinem intrebarea anterioara pentru a verifica schimbarea categoriei
        bloc_nou = (prev_q is None or prev_q.categorie != next_q.categorie)  # Verificam daca categoria s-a schimbat fata de intrebarea anterioara
        if bloc_nou:  # Daca am trecut la o categorie noua de intrebari
            await callback.message.answer(f"📌 *{next_q.categorie}*", parse_mode="Markdown")  # Afisam numele noii categorii cu formatare bold

        # Folosim direct next_q.index care e 1-based în DB (1, 2, 3... 33)
        await callback.message.answer(  # Trimitem urmatoarea intrebare utilizatorului
            f"`{next_q.index}/{TOTAL_INTREBARI}`\n\n{next_q.text}",  # Textul contine numarul intrebarii si textul ei
            reply_markup=yes_no_keyboard(user.language),  # Atasam tastatura cu optiunile Da/Nu/Nu stiu
            parse_mode="Markdown"  # Folosim formatarea Markdown pentru afisare
        )
