from aiogram import Router, F  # Importam clasa Router si filtrul F din biblioteca aiogram
from aiogram.types import Message  # Importam tipul Message pentru gestionarea mesajelor primite
from bd_sqlite.functii_bd import get_user_by_telegram_id  # Importam functia care obtine un utilizator dupa ID-ul Telegram din baza de date
from bot.tastatura.tastatura_meniu import main_menu  # Importam functia care genereaza tastatura meniului principal

router = Router()  # Cream o instanta de Router pentru a inregistra handler-ele din acest fisier


@router.message(F.text.in_(["/info"]))  # Decoratorul care inregistreaza handler-ul pentru comanda /info
async def info_command(message: Message):  # Definim functia asincrona care se executa la comanda /info
    user = await get_user_by_telegram_id(message.from_user.id)  # Obtinem obiectul utilizatorului din baza de date dupa ID-ul Telegram
    language = user.language if user and user.language else "ro"  # Determinam limba utilizatorului; daca nu exista, folosim romana ca limba implicita

    textss = {  # Cream un dictionar cu textele informative in ambele limbi
        "ro": "Acest bot a fost creat pentru a oferi o perspectivă rapidă și inteligentă asupra afacerii tale. Pe baza răspunsurilor introduse, sistemul analizează datele și stabilește nivelul de dezvoltare al businessului. \nÎn plus, utilizatorul poate vizualiza rezultatele sub formă de rapoarte clare și comparații relevante, obținând astfel o înțelegere mai bună a situației economice.",  # Textul informativ in limba romana despre scopul botului
        "ru": """Этот бот был создан для того, чтобы предоставить быстрый и интеллектуальный обзор вашего бизнеса. На основе введённых ответов система анализирует данные и определяет уровень развития компании.
Кроме того, пользователь может просматривать результаты в виде наглядных отчётов и релевантных сравнений, получая тем самым более полное понимание экономической ситуации."""  # Textul informativ in limba rusa despre scopul botului
    }

    await message.answer(  # Trimitem mesajul informativ utilizatorului
        textss[language],  # Selectam textul corespunzator limbii utilizatorului din dictionar
        reply_markup=main_menu(language=user.language, test_completed=user.test_completed)  # Atasam meniul principal configurat in functie de limba si starea testului
    )


@router.message(F.text.in_(["/help"]))  # Decoratorul care inregistreaza handler-ul pentru comanda /help
async def help_command(message: Message):  # Definim functia asincrona care se executa la comanda /help
    user = await get_user_by_telegram_id(message.from_user.id)  # Obtinem obiectul utilizatorului din baza de date dupa ID-ul Telegram
    language = user.language if user and user.language else "ro"  # Determinam limba utilizatorului; daca nu exista, folosim romana ca limba implicita

    textss = {  # Cream un dictionar cu textele de ajutor in ambele limbi
        "ro": "Pentru asistență, vă rugăm să contactați suportul nostru la",  # Textul de ajutor in limba romana cu indrumarea catre suport
        "ru": "Для получения помощи, пожалуйста, свяжитесь с нашей службой поддержки по адресу"  # Textul de ajutor in limba rusa cu indrumarea catre suport
    }

    await message.answer(  # Trimitem mesajul de ajutor utilizatorului
        textss[language],  # Selectam textul corespunzator limbii utilizatorului din dictionar
        reply_markup=main_menu(language=user.language, test_completed=user.test_completed)  # Atasam meniul principal configurat in functie de limba si starea testului
    )


@router.message(F.text.in_(["/about"]))  # Decoratorul care inregistreaza handler-ul pentru comanda /about
async def about_command(message: Message):  # Definim functia asincrona care se executa la comanda /about
    user = await get_user_by_telegram_id(message.from_user.id)  # Obtinem obiectul utilizatorului din baza de date dupa ID-ul Telegram
    language = user.language if user and user.language else "ro"  # Determinam limba utilizatorului; daca nu exista, folosim romana ca limba implicita

    textss = {  # Cream un dictionar cu textele despre companie in ambele limbi
        "ro": "CROWE TURCAN MIKHAILENKO — din anul 2023 face parte din grupul internațional Crowe Global. Fondată în 1915, Crowe se numără astăzi printre primele 10 cele mai mari rețele globale de servicii profesionale.Oferim soluții avansate în domeniul fiscalității și consultanței juridice, ajutând antreprenorii să atingă noi culmi ale succesului.",  # Textul despre companie in limba romana
        "ru": "CROWE TURCAN MIKHAILENKO — с 2023 года является частью международной группы Crowe Global. Основанная в 1915 году, Crowe сегодня входит в топ-10 крупнейших глобальных сетей профессиональных услуг.Мы предоставляем передовые решения в области налогообложения и юридического консалтинга, помогая предпринимателям достигать новых вершин успеха."  # Textul despre companie in limba rusa
    }

    await message.answer(  # Trimitem mesajul despre companie utilizatorului
        textss[language],  # Selectam textul corespunzator limbii utilizatorului din dictionar
        reply_markup=main_menu(language=user.language, test_completed=user.test_completed)  # Atasam meniul principal configurat in functie de limba si starea testului
    )
