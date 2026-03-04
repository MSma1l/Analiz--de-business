from aiogram import Router, F  # Importam clasa Router si filtrul F din biblioteca aiogram
from aiogram.filters import CommandStart  # Importam filtrul CommandStart pentru comanda /start
from aiogram.types import Message, CallbackQuery  # Importam tipurile Message si CallbackQuery pentru gestionarea mesajelor si apasarilor pe butoane
from bot.tastatura.limba import language_keyboard  # Importam functia care genereaza tastatura de selectare a limbii
from bot.tastatura.tastatura_meniu import main_menu  # Importam functia care genereaza meniul principal
from bd_sqlite.functii_bd import (  # Importam functiile de lucru cu baza de date
    get_or_create_user,  # Functia care obtine sau creeaza un utilizator in baza de date
    set_user_language,  # Functia care seteaza limba utilizatorului in baza de date
    get_user_by_telegram_id,  # Functia care obtine un utilizator dupa ID-ul sau Telegram
)

router = Router()  # Cream o instanta de Router pentru a inregistra handler-ele din acest fisier


@router.message(CommandStart())  # Decoratorul care inregistreaza handler-ul pentru comanda /start
async def start_bot(message: Message):  # Definim functia asincrona care se executa la comanda /start
    await get_or_create_user(  # Apelam functia care obtine sau creeaza utilizatorul in baza de date
        telegram_id=message.from_user.id,  # Transmitem ID-ul Telegram al utilizatorului
        username=message.from_user.username,  # Transmitem numele de utilizator Telegram
        first_name=message.from_user.first_name  # Transmitem prenumele utilizatorului
    )

    await message.answer(  # Trimitem un mesaj de bun venit utilizatorului
        "Bun venit! Mă numesc BizzCheck \nДобро пожаловать! Меня зовут BizzCheck \n\nAlegeți limba / Выберите язык:",  # Textul de bun venit in romana si rusa cu cererea de a alege limba
        reply_markup=language_keyboard()  # Atasam tastatura inline cu butoanele de selectare a limbii
    )


@router.callback_query(F.data.in_(["lang_ro", "lang_ru"]))  # Decoratorul care inregistreaza handler-ul pentru apasarea butoanelor de limba (romana sau rusa)
async def language_selected(callback: CallbackQuery):  # Definim functia asincrona care se executa cand utilizatorul selecteaza limba
    language = "ro" if callback.data == "lang_ro" else "ru"  # Determinam limba selectata: "ro" daca a apasat pe romana, altfel "ru" pentru rusa

    await set_user_language(callback.from_user.id, language)  # Salvam limba selectata in baza de date pentru utilizatorul curent

    user = await get_user_by_telegram_id(callback.from_user.id)  # Obtinem obiectul utilizatorului din baza de date dupa ID-ul Telegram

    texts = {  # Cream un dictionar cu textele de bun venit in ambele limbi
        "ro": """🏢 BizzCheck Bot

    Bine ai venit în centrul tău de analiză!
    📈 Analiza performanței afacerii
    📊 Evaluarea stării businessului
    📋 Rapoarte și comparații inteligente""",  # Textul de bun venit in limba romana cu descrierea functiilor botului
        "ru": """🏢 BizzCheck Bot

    Добро пожаловать в центр бизнес-анализа!
    📈 Анализ эффективности бизнеса
    📊 Оценка состояния компании
    📋 Умные отчёты и сравнения"""  # Textul de bun venit in limba rusa cu descrierea functiilor botului
    }

    await callback.message.answer(  # Trimitem mesajul de bun venit in limba selectata
        texts[language],  # Selectam textul corespunzator limbii alese din dictionar
        reply_markup=main_menu(language=user.language, test_completed=user.test_completed)  # Atasam meniul principal configurat in functie de limba si starea testului
    )

    await callback.answer()  # Inchidem notificarea callback-ului pentru a opri animatia de incarcare pe buton
