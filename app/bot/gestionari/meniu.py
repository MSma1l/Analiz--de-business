from aiogram import Router, F  # Importam clasa Router si filtrul F din biblioteca aiogram
from aiogram.types import Message  # Importam tipul Message pentru a lucra cu mesajele primite
from sqlalchemy import update  # Importam functia update din SQLAlchemy pentru actualizarea bazei de date
from bd_sqlite.functii_bd import get_user_by_telegram_id  # Importam functia care obtine utilizatorul dupa ID-ul Telegram
from bd_sqlite.conexiune import async_session  # Importam sesiunea asincrona pentru conectarea la baza de date
from bd_sqlite.modele import User  # Importam modelul User care reprezinta tabela utilizatorilor
from logica.stare import CabinetState  # Importam starile FSM pentru fluxul cabinetului personal
from aiogram.fsm.context import FSMContext  # Importam contextul FSM pentru gestionarea starilor conversatiei
from bot.tastatura.tastatura_cabinet import cabinet_keyboard  # Importam functia care genereaza tastatura cabinetului
from sqlalchemy import select, desc  # Importam functiile select si desc pentru interogari SQL
from bot.tastatura.tastatura_locatie import locatie_keyboard  # Importam functia care genereaza tastatura cu locatia


router = Router()  # Cream un router nou pentru a inregistra handler-ele de mesaje

@router.message(F.text.in_(["👤 Cabinet personal", "👤 Личный кабинет"]))  # Handler care reactioneaza la apasarea butonului "Cabinet personal" in romana sau rusa
async def cabinet_personal(message: Message):  # Definim functia asincrona care gestioneaza deschiderea cabinetului personal
    user = await get_user_by_telegram_id(message.from_user.id)  # Obtinem utilizatorul din baza de date dupa ID-ul sau Telegram

    texts = {  # Definim dictionarul cu textele de raspuns in ambele limbi
        "ro": "📊 Cabinetul personal:",  # Textul in limba romana
        "ru": "📊 Личный кабинет:"  # Textul in limba rusa
    }

    await message.answer(  # Trimitem raspunsul catre utilizator
        texts[user.language],  # Selectam textul in functie de limba utilizatorului
        reply_markup=cabinet_keyboard(user.language,  # Atasam tastatura cabinetului generata conform limbii
                                      test_completed=user.test_completed  # Transmitem starea testului (finalizat sau nu)
        )
    )

@router.message(F.text.in_(["➕ Adaugă compania", "➕ Добавить компанию"]))  # Handler care reactioneaza la apasarea butonului "Adauga compania" in romana sau rusa
async def add_company_start(message: Message, state: FSMContext):  # Definim functia asincrona care initiaza procesul de adaugare a companiei
    user = await get_user_by_telegram_id(message.from_user.id)  # Obtinem utilizatorul din baza de date dupa ID-ul sau Telegram

    texts_company = {  # Definim dictionarul cu textele care cer numele companiei
        "ro": "🏢 Introdu numele companiei:",  # Textul in limba romana
        "ru": "🏢 Введите название компании:"  # Textul in limba rusa
    }

    await state.set_state(CabinetState.waiting_company_name)  # Setam starea FSM la asteptarea numelui companiei
    await message.answer(texts_company[user.language])  # Trimitem mesajul care cere numele companiei in limba utilizatorului

@router.message(CabinetState.waiting_company_name)  # Handler care reactioneaza cand FSM-ul este in starea de asteptare a numelui companiei
async def save_company_name(message: Message, state: FSMContext):  # Definim functia asincrona care salveaza numele companiei
    user = await get_user_by_telegram_id(message.from_user.id)  # Obtinem utilizatorul din baza de date dupa ID-ul sau Telegram

    company_name = message.text.strip()  # Extragem si curatam textul mesajului (numele companiei) de spatii

    if len(company_name) < 2:  # Verificam daca numele companiei are mai putin de 2 caractere
        await message.answer(  # Trimitem mesaj de eroare daca numele este prea scurt
            "❌ Numele companiei este prea scurt"  # Mesajul de eroare in romana
            if user.language == "ro"  # Conditia pentru limba romana
            else "❌ Название компании слишком короткое"  # Mesajul de eroare in rusa
        )
        return  # Oprim executia functiei daca validarea a esuat

    await state.update_data(company_name=company_name)  # Salvam numele companiei in datele starii FSM

    # FIX BUG 4: Salvam imediat company_name in BD — daca bot-ul se restarteaza, datele nu se pierd complet
    async with async_session() as session:
        await session.execute(
            update(User).where(User.id == user.id).values(company_name=company_name)
        )
        await session.commit()

    texts_number = {  # Definim dictionarul cu textele care cer numarul companiei
        "ro": "📞 Introdu numărul companiei:",  # Textul in limba romana
        "ru": "📞 Введите номер компании:"  # Textul in limba rusa
    }

    await state.set_state(CabinetState.waiting_company_number)  # Setam starea FSM la asteptarea numarului companiei
    await message.answer(texts_number[user.language])  # Trimitem mesajul care cere numarul companiei in limba utilizatorului

@router.message(CabinetState.waiting_company_number)  # Handler care reactioneaza cand FSM-ul este in starea de asteptare a numarului companiei
async def save_company_number(message: Message, state: FSMContext):  # Definim functia asincrona care salveaza numarul companiei
    user = await get_user_by_telegram_id(message.from_user.id)  # Obtinem utilizatorul din baza de date dupa ID-ul sau Telegram

    number_company = message.text.strip()  # Extragem si curatam textul mesajului (numarul companiei) de spatii

    if len(number_company) < 9:  # Verificam daca numarul are mai putin de 9 caractere (numar invalid)
        await message.answer(  # Trimitem mesaj de eroare daca numarul este invalid
            "❌ Număr invalid"  # Mesajul de eroare in romana
            if user.language == "ro"  # Conditia pentru limba romana
            else "❌ Неверный номер"  # Mesajul de eroare in rusa
        )
        return  # Oprim executia functiei daca validarea a esuat

    await state.update_data(number_company=number_company)  # Salvam numarul companiei in datele starii FSM

    # FIX BUG 4: Salvam imediat number_company in BD — daca bot-ul se restarteaza, datele nu se pierd
    async with async_session() as session:
        await session.execute(
            update(User).where(User.id == user.id).values(number_company=number_company)
        )
        await session.commit()

    texts_email = {  # Definim dictionarul cu textele care cer emailul
        "ro": "📧 Introdu emailul:",  # Textul in limba romana
        "ru": "📧 Введите email:"  # Textul in limba rusa
    }

    await state.set_state(CabinetState.waiting_company_email)  # Setam starea FSM la asteptarea emailului companiei
    await message.answer(texts_email[user.language])  # Trimitem mesajul care cere emailul in limba utilizatorului

@router.message(CabinetState.waiting_company_email)  # Handler care reactioneaza cand FSM-ul este in starea de asteptare a emailului companiei
async def save_company_email(message: Message, state: FSMContext):  # Definim functia asincrona care salveaza emailul si finalizeaza procesul
    user = await get_user_by_telegram_id(message.from_user.id)  # Obtinem utilizatorul din baza de date dupa ID-ul sau Telegram

    email_company = message.text.strip()  # Extragem si curatam textul mesajului (emailul companiei) de spatii

    if "@" not in email_company:  # Verificam daca emailul contine caracterul "@" (validare simpla)
        await message.answer(  # Trimitem mesaj de eroare daca emailul este invalid
            "❌ Email invalid"  # Mesajul de eroare in romana
            if user.language == "ro"  # Conditia pentru limba romana
            else "❌ Неверный email"  # Mesajul de eroare in rusa
        )
        return  # Oprim executia functiei daca validarea a esuat

    data = await state.get_data()  # Obtinem toate datele acumulate in starea FSM (numele si numarul companiei)

    async with async_session() as session:  # Deschidem o sesiune asincrona cu baza de date
        await session.execute(  # Executam interogarea de actualizare in baza de date
            update(User)  # Construim interogarea UPDATE pe tabela User
            .where(User.id == user.id)  # Filtram dupa ID-ul utilizatorului curent
            .values(  # Setam valorile de actualizat
                company_name=data["company_name"],  # Actualizam numele companiei din datele FSM
                number_company=data["number_company"],  # Actualizam numarul companiei din datele FSM
                email_company=email_company  # Actualizam emailul companiei cu valoarea curenta
            )
        )
        await session.commit()  # Salvam modificarile in baza de date (commit tranzactie)

    await state.clear()  # Curatam starea FSM dupa salvarea cu succes

    texts = {  # Definim dictionarul cu mesajele de confirmare a salvarii
        "ro": f"✅ Compania a fost salvată:\n🏢 {data['company_name']}\n📞 {data['number_company']}\n📧 {email_company}",  # Mesajul de confirmare in romana cu datele companiei
        "ru": f"✅ Компания сохранена:\n🏢 {data['company_name']}\n📞 {data['number_company']}\n📧 {email_company}"  # Mesajul de confirmare in rusa cu datele companiei
    }

    await message.answer(  # Trimitem mesajul de confirmare catre utilizator
        texts[user.language],  # Selectam textul in functie de limba utilizatorului
        reply_markup=cabinet_keyboard(user.language,  # Atasam tastatura cabinetului generata conform limbii
                                      test_completed=user.test_completed  # Transmitem starea testului (finalizat sau nu)
        )
    )


@router.message(F.text.in_(["📊 Vezi poziția companiei", "📊 Позиция компании"]))  # Handler care reactioneaza la apasarea butonului "Vezi pozitia companiei" in romana sau rusa
async def company_position(message: Message):  # Definim functia asincrona care afiseaza pozitia companiei in clasament
    user = await get_user_by_telegram_id(message.from_user.id)  # Obtinem utilizatorul din baza de date dupa ID-ul sau Telegram

    if not user.test_completed or user.score is None:  # Verificam daca utilizatorul a finalizat testul si are scor
        await message.answer(  # Trimitem mesaj de eroare daca testul nu a fost finalizat
            "❌ Mai întâi trebuie să finalizezi testul."  # Mesajul de eroare in romana
            if user.language == "ro"  # Conditia pentru limba romana
            else "❌ Сначала нужно пройти тест."  # Mesajul de eroare in rusa
        )
        return  # Oprim executia functiei daca testul nu a fost finalizat

    async with async_session() as session:  # Deschidem o sesiune asincrona cu baza de date
        # luam toate companiile cu scor
        result = await session.execute(  # Executam interogarea SQL pentru a obtine toate companiile cu scor
            select(User)  # Selectam din tabela User
            .where(User.company_name.isnot(None))  # Filtram doar utilizatorii care au numele companiei setat
            .where(User.score.isnot(None))  # Filtram doar utilizatorii care au scor setat
            .where(User.test_completed == True)  # Filtram doar utilizatorii care au finalizat testul
            .order_by(desc(User.score))  # Sortam descrescator dupa scor
        )
        users = result.scalars().all()  # Extragem toti utilizatorii din rezultatul interogarii ca lista

    if not users:  # Verificam daca exista utilizatori in clasament
        await message.answer("Nu există date pentru clasament.")  # Trimitem mesaj daca nu exista date
        return  # Oprim executia functiei daca nu exista date

    top5 = users[:5]  # Extragem primii 5 utilizatori din clasament (TOP 5)

    position = next(  # Gasim pozitia companiei utilizatorului curent in clasament
        (i + 1 for i, u in enumerate(users) if u.id == user.id),  # Iteram prin lista si returnam pozitia (1-based)
        None  # Returnam None daca utilizatorul nu este gasit in clasament
    )

    if user.language == "ro":  # Verificam daca limba utilizatorului este romana
        text = "🏆 TOP 5 companii:\n\n"  # Initializam textul cu titlul clasamentului in romana
        for i, u in enumerate(top5, start=1):  # Iteram prin primele 5 companii cu numaratoare incepand de la 1
            text += f"{i}. {u.company_name} — {u.score}%\n"  # Adaugam fiecare companie cu pozitia si scorul

        text += f"\n📍 Compania ta este pe locul {position} din {len(users)}."  # Adaugam pozitia companiei utilizatorului
    else:  # Daca limba utilizatorului este rusa
        text = "🏆 ТОП 5 компаний:\n\n"  # Initializam textul cu titlul clasamentului in rusa
        for i, u in enumerate(top5, start=1):  # Iteram prin primele 5 companii cu numaratoare incepand de la 1
            text += f"{i}. {u.company_name} — {u.score}%\n"  # Adaugam fiecare companie cu pozitia si scorul

        text += f"\n📍 Ваша компания на месте {position} из {len(users)}."  # Adaugam pozitia companiei utilizatorului in rusa

    await message.answer(text)  # Trimitem mesajul cu clasamentul catre utilizator


@router.message(F.text.in_(["💬 Contacte","💬 Контакты"]))  # Handler care reactioneaza la apasarea butonului "Contacte" in romana sau rusa
async def contacte(message:Message):  # Definim functia asincrona care afiseaza informatiile de contact
    user = await get_user_by_telegram_id(message.from_user.id)  # Obtinem utilizatorul din baza de date dupa ID-ul sau Telegram


    contacte = {  # Definim dictionarul cu informatiile de contact in ambele limbi
    "ro": "📩 Contacte:\n\n📞 Telefon: +373 XXX XXXXX\n\n✉️ Poșta electronică: support@gmail.com",  # Informatiile de contact in romana
    "ru": "📩 Контакты:\n\n📞 Телефон: +373 XXX XXXXX\n\n✉️ Электронная почта: support@gmail.com"  # Informatiile de contact in rusa
    }

    await message.answer(  # Trimitem mesajul cu informatiile de contact catre utilizator
        contacte[user.language],  # Selectam textul in functie de limba utilizatorului
        reply_markup= locatie_keyboard(user.language)  # Atasam tastatura inline cu butonul de locatie
        )
