# Importam functiile necesare din SQLAlchemy: select (interogare), update (actualizare), delete (stergere), func (functii agregate), and_ (conditie logica SI)
from sqlalchemy import select, update, delete, func, and_
# Importam sesiunea asincrona pentru conectarea la baza de date
from bd_sqlite.conexiune import async_session
# Importam modelele tabelelor din baza de date
from bd_sqlite.modele import (
    User,        # Modelul utilizatorului
    Intrebare,   # Modelul intrebarii
    Raspuns,     # Modelul raspunsului
    Rezultat,    # Modelul rezultatului
    PragRisc     # Modelul pragului de risc
)

# =====================================================
# USER
# =====================================================

# Functie asincrona care obtine un utilizator existent sau creeaza unul nou
async def get_or_create_user(telegram_id, username, first_name):
    # Deschidem o sesiune asincrona catre baza de date
    async with async_session() as session:

        # Executam o interogare pentru a cauta utilizatorul dupa telegram_id
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        # Extragem un singur rezultat sau None daca nu exista
        user = result.scalar_one_or_none()

        # Daca utilizatorul exista deja, il returnam
        if user:
            return user

        # Cream un obiect nou de tip User cu datele primite
        user = User(
            telegram_id=telegram_id,  # ID-ul de Telegram al utilizatorului
            username=username,        # Numele de utilizator Telegram
            first_name=first_name     # Prenumele utilizatorului
        )

        # Adaugam utilizatorul nou in sesiune (il pregatim pentru salvare)
        session.add(user)
        # Salvam modificarile in baza de date (commit tranzactia)
        await session.commit()

        # Returnam utilizatorul nou creat
        return user


# Functie asincrona care obtine un utilizator dupa ID-ul de Telegram
async def get_user_by_telegram_id(telegram_id: int):
    # Deschidem o sesiune asincrona catre baza de date
    async with async_session() as session:

        # Executam o interogare pentru a cauta utilizatorul dupa telegram_id
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )

        # Returnam utilizatorul gasit sau None daca nu exista
        return result.scalar_one_or_none()


# Functie asincrona care seteaza limba utilizatorului si reseteaza tot testul
async def set_user_language(telegram_id: int, language: str):
    """
    Setează limba și RESETEAZĂ tot testul.
    Șterge răspunsurile și rezultatele vechi.
    """
    # Deschidem o sesiune asincrona catre baza de date
    async with async_session() as session:

        # Cautam utilizatorul dupa telegram_id
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        # Extragem utilizatorul sau None daca nu exista
        user = result.scalar_one_or_none()

        # Daca utilizatorul nu exista, iesim din functie fara sa facem nimic
        if not user:
            return

        # Actualizam datele utilizatorului: limba, indexul curent la 1, testul ca necompletat, scorul la 0
        await session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(
                language=language,       # Setam limba aleasa
                current_index=1,         # Resetam indexul intrebarii curente la prima intrebare
                test_completed=False,    # Marcam testul ca necompletat
                score=0                  # Resetam scorul la zero
            )
        )

        # Stergem toate raspunsurile vechi ale utilizatorului
        await session.execute(
            delete(Raspuns).where(Raspuns.user_id == user.id)
        )

        # Stergem toate rezultatele vechi ale utilizatorului
        await session.execute(
            delete(Rezultat).where(Rezultat.user_id == user.id)
        )

        # Salvam toate modificarile in baza de date
        await session.commit()


# =====================================================
# SALVARE RASPUNS
# =====================================================

# Functie asincrona care salveaza un raspuns al utilizatorului la o intrebare
async def save_answer(user_id: int, intrebare_id: int, weight: str):
    """
    weight = YES / NO / IDK
    """

    # Deschidem o sesiune asincrona catre baza de date
    async with async_session() as session:

        # Cautam daca exista deja un raspuns al utilizatorului pentru aceasta intrebare
        result = await session.execute(
            select(Raspuns).where(
                Raspuns.user_id == user_id,            # Filtram dupa ID-ul utilizatorului
                Raspuns.intrebare_id == intrebare_id    # Filtram dupa ID-ul intrebarii
            )
        )

        # Extragem raspunsul existent sau None
        existing = result.scalar_one_or_none()

        # Daca raspunsul exista deja, ii actualizam valoarea (weight)
        if existing:
            existing.weight = weight
        # Daca nu exista, cream un raspuns nou si il adaugam in sesiune
        else:
            session.add(
                Raspuns(
                    user_id=user_id,              # ID-ul utilizatorului care raspunde
                    intrebare_id=intrebare_id,    # ID-ul intrebarii la care raspunde
                    weight=weight                 # Valoarea raspunsului (YES/NO/IDK)
                )
            )

        # Salvam modificarile in baza de date
        await session.commit()


# Functie asincrona care salveaza raspunsul SI incrementeaza indexul intrebarii intr-o singura tranzactie
async def save_answer_and_advance(user_id: int, intrebare_id: int, weight: str, new_index: int):
    """
    Salveaza raspunsul si actualizeaza current_index intr-o singura tranzactie.
    Reduce numarul de scrieri in BD de la 2 la 1 — imbunatateste performanta.
    """
    # Deschidem o sesiune asincrona catre baza de date
    async with async_session() as session:

        # Cautam daca exista deja un raspuns al utilizatorului pentru aceasta intrebare
        result = await session.execute(
            select(Raspuns).where(
                Raspuns.user_id == user_id,            # Filtram dupa ID-ul utilizatorului
                Raspuns.intrebare_id == intrebare_id    # Filtram dupa ID-ul intrebarii
            )
        )

        # Extragem raspunsul existent sau None
        existing = result.scalar_one_or_none()

        # Daca raspunsul exista deja, ii actualizam valoarea (weight)
        if existing:
            existing.weight = weight
        # Daca nu exista, cream un raspuns nou si il adaugam in sesiune
        else:
            session.add(
                Raspuns(
                    user_id=user_id,              # ID-ul utilizatorului care raspunde
                    intrebare_id=intrebare_id,    # ID-ul intrebarii la care raspunde
                    weight=weight                 # Valoarea raspunsului (YES/NO/IDK)
                )
            )

        # Actualizam indexul intrebarii curente in aceeasi tranzactie
        await session.execute(
            update(User)
            .where(User.id == user_id)              # Filtram dupa ID-ul utilizatorului
            .values(current_index=new_index)         # Setam noul index al intrebarii
        )

        # Salvam ambele modificari intr-un singur commit (o singura scriere in BD)
        await session.commit()


# =====================================================
# INTREBARE CURENTA
# =====================================================

# Functie asincrona care obtine intrebarea curenta dupa index si limba
async def get_current_question(index: int, language: str):
    # Deschidem o sesiune asincrona catre baza de date
    async with async_session() as session:

        # Cautam intrebarea care are indexul si limba specificate
        result = await session.execute(
            select(Intrebare).where(
                Intrebare.index == index,        # Filtram dupa indexul intrebarii
                Intrebare.language == language    # Filtram dupa limba
            )
        )

        # Returnam intrebarea gasita sau None daca nu exista
        return result.scalar_one_or_none()


# =====================================================
# CALCUL SCOR — SUMA PUNCTAJ
# =====================================================

# Functie asincrona care calculeaza scorul maxim posibil pe fiecare categorie
async def get_max_score_by_category(language: str):
    """
    Returnează scorul maxim posibil pentru fiecare categorie
    """
    # Deschidem o sesiune asincrona catre baza de date
    async with async_session() as session:
        # Construim interogarea: selectam categoria si suma punctajelor (weight) pe fiecare categorie
        stmt = (
            select(
                Intrebare.categorie,                            # Selectam numele categoriei
                func.sum(Intrebare.weight).label("max_scor")    # Calculam suma punctajelor si o numim "max_scor"
            )
            .where(Intrebare.language == language)    # Filtram doar intrebarile in limba specificata
            .group_by(Intrebare.categorie)            # Grupam rezultatele pe categorii
        )
        # Executam interogarea
        result = await session.execute(stmt)
        # Returnam un dictionar {categorie: scor_maxim} din toate rezultatele
        return {categorie: max_scor for categorie, max_scor in result.all()}


# Functie asincrona care calculeaza scorul utilizatorului pe fiecare categorie (doar raspunsurile YES)
async def calculate_score_by_category(user_id: int, language: str):
    """
    Ia doar raspunsurile YES
    Aduna punctajul intrebarilor
    Returneaza scor pe fiecare categorie
    """

    # Deschidem o sesiune asincrona catre baza de date
    async with async_session() as session:

        # Construim interogarea: suma punctajelor intrebarilor la care utilizatorul a raspuns YES
        stmt = (
            select(
                Intrebare.categorie,                          # Selectam numele categoriei
                func.sum(Intrebare.weight).label("scor")      # Calculam suma punctajelor si o numim "scor"
            )
            .select_from(Raspuns)                              # Pornim interogarea din tabela Raspuns
            .join(Intrebare, Intrebare.id == Raspuns.intrebare_id)  # Facem join cu tabela Intrebare dupa ID
            .where(
                Raspuns.user_id == user_id,        # Filtram dupa ID-ul utilizatorului
                Raspuns.weight == "YES",           # Luam doar raspunsurile cu valoarea YES
                Intrebare.language == language      # Filtram dupa limba specificata
            )
            .group_by(Intrebare.categorie)          # Grupam rezultatele pe categorii
        )

        # Executam interogarea
        result = await session.execute(stmt)

        # Returnam toate rezultatele ca o lista de tupluri (categorie, scor)
        return result.all()


# =====================================================
# NIVEL RISC DIN INTERVAL
# =====================================================

# Functie asincrona care determina nivelul de risc pentru o categorie si un scor dat
async def get_nivel_risc(categorie: str, scor: int, language: str):
    """
    Găsește nivelul de risc pentru o categorie și scor dat
    """

    # Deschidem o sesiune asincrona catre baza de date
    async with async_session() as session:

        # Construim interogarea: cautam nivelul de risc care corespunde categoriei, scorului si limbii
        stmt = select(PragRisc.nivel).where(
            PragRisc.categorie == categorie,    # Filtram dupa categorie
            PragRisc.scor_min <= scor,          # Scorul trebuie sa fie mai mare sau egal cu scor_min
            PragRisc.scor_max >= scor,          # Scorul trebuie sa fie mai mic sau egal cu scor_max
            PragRisc.language == language        # Filtram dupa limba
        )

        # Executam interogarea
        result = await session.execute(stmt)
        # Extragem nivelul de risc sau None daca nu s-a gasit
        nivel = result.scalar_one_or_none()

        # Returnam nivelul gasit sau "Necunoscut" daca nu exista in baza de date
        return nivel or "Necunoscut"


# =====================================================
# SALVARE REZULTATE ÎN BD
# =====================================================

# Functie asincrona care salveaza rezultatele pe categorii in tabela Rezultat
async def save_results_to_db(user_id: int, raport, max_scores: dict):
    """
    Salvează rezultatele pe categorii în tabela Rezultat
    raport = [(categorie, scor, nivel), ...]
    max_scores = {categorie: max_scor}
    """
    # Deschidem o sesiune asincrona catre baza de date
    async with async_session() as session:

        # Parcurgem fiecare element din raport (categorie, scor, nivel)
        for categorie, scor, nivel in raport:
            # Obtinem scorul maxim pentru categoria curenta, sau folosim scorul curent daca nu exista
            max_scor = max_scores.get(categorie, scor)

            # Cautam daca exista deja un rezultat salvat pentru acest utilizator si aceasta categorie
            result = await session.execute(
                select(Rezultat).where(
                    Rezultat.user_id == user_id,        # Filtram dupa ID-ul utilizatorului
                    Rezultat.categorie == categorie      # Filtram dupa categorie
                )
            )
            # Extragem rezultatul existent sau None
            existing = result.scalar_one_or_none()

            # Daca rezultatul exista deja, ii actualizam valorile
            if existing:
                existing.scor = scor            # Actualizam scorul
                existing.max_scor = max_scor    # Actualizam scorul maxim
                existing.nivel = nivel          # Actualizam nivelul de risc
            # Daca nu exista, cream un rezultat nou si il adaugam in sesiune
            else:
                session.add(
                    Rezultat(
                        user_id=user_id,        # ID-ul utilizatorului
                        categorie=categorie,    # Numele categoriei
                        scor=scor,              # Scorul obtinut
                        max_scor=max_scor,      # Scorul maxim posibil
                        nivel=nivel             # Nivelul de risc
                    )
                )

        # Salvam toate modificarile in baza de date
        await session.commit()


# =====================================================
# RESETARE REZULTATE USER
# =====================================================

# Functie asincrona care sterge toate rezultatele unui utilizator si reseteaza scorul si testul
async def reset_user_results(user_id: int):
    """
    Șterge toate rezultatele vechi și resetează scorul și testul
    """
    # Deschidem o sesiune asincrona catre baza de date
    async with async_session() as session:

        # Stergem toate rezultatele din tabela Rezultat pentru acest utilizator
        await session.execute(
            delete(Rezultat).where(Rezultat.user_id == user_id)
        )

        # Actualizam utilizatorul: resetam scorul la 0, testul ca necompletat, indexul la prima intrebare
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(score=0, test_completed=False, current_index=1)
        )

        # Salvam modificarile in baza de date
        await session.commit()


# =====================================================
# PRELUARE REZULTATE USER
# =====================================================

# Functie asincrona care returneaza rezultatele salvate pentru un utilizator
async def get_user_results(user_id: int):
    """
    Returnează rezultatele salvate pentru un utilizator
    Returns: dict {categorie: {"scor": scor, "max_scor": max_scor, "nivel": nivel}}
    """
    # Deschidem o sesiune asincrona catre baza de date
    async with async_session() as session:

        # Selectam categoria, scorul, scorul maxim si nivelul de risc pentru utilizator, ordonate pe categorie
        result = await session.execute(
            select(Rezultat.categorie, Rezultat.scor, Rezultat.max_scor, Rezultat.nivel)
            .where(Rezultat.user_id == user_id)       # Filtram dupa ID-ul utilizatorului
            .order_by(Rezultat.categorie)              # Ordonam alfabetic dupa categorie
        )

        # Extragem toate randurile din rezultat
        rows = result.all()

        # Construim si returnam un dictionar cu rezultatele pe categorii
        return {
            categorie: {"scor": scor, "max_scor": max_scor or scor, "nivel": nivel}
            # max_scor or scor: daca max_scor e None, folosim scorul curent ca valoare implicita
            for categorie, scor, max_scor, nivel in rows
            # Iteram prin fiecare rand extras din baza de date
        }

# Functie asincrona care returneaza numarul de intrebari pe fiecare categorie pentru o limba data
async def get_questions_per_category(language: str) -> dict:
    """
    Returnează {categorie: total_intrebari} pentru o limbă
    """
    # Deschidem o sesiune asincrona catre baza de date
    async with async_session() as session:
        # Construim interogarea: numaram intrebarile pe fiecare categorie
        stmt = (
            select(Intrebare.categorie, func.count(Intrebare.id).label("total"))
            # Selectam categoria si numarul total de intrebari din fiecare categorie
            .where(Intrebare.language == language)    # Filtram dupa limba specificata
            .group_by(Intrebare.categorie)            # Grupam rezultatele pe categorii
        )
        # Executam interogarea
        result = await session.execute(stmt)
        # Returnam un dictionar {categorie: numar_total_intrebari}
        return {categorie: total for categorie, total in result.all()}
