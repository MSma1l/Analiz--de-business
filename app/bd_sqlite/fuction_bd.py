from sqlalchemy import select, update, func
from bd_sqlite.conexiune import async_session
from bd_sqlite.models import (
    User,
    Intrebare,
    Raspuns,
    Rezultat,
    PragRisc
)

# =====================================================
# USER
# =====================================================

async def get_or_create_user(telegram_id, username, first_name):
    async with async_session() as session:

        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if user:
            return user

        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name
        )

        session.add(user)
        await session.commit()

        return user


async def get_user_by_telegram_id(telegram_id: int):
    async with async_session() as session:

        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )

        return result.scalar_one_or_none()


async def set_user_language(telegram_id: int, language: str):
    async with async_session() as session:

        await session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(language=language, current_index=1)
        )

        await session.commit()


# =====================================================
# SALVARE RASPUNS
# =====================================================

async def save_answer(user_id: int, intrebare_id: int, weight: str):
    """
    valoare = YES / NO / IDK
    """

    async with async_session() as session:

        result = await session.execute(
            select(Raspuns).where(
                Raspuns.user_id == user_id,
                Raspuns.intrebare_id == intrebare_id
            )
        )

        existing = result.scalar_one_or_none()

        if existing:
            existing.weight = weight
        else:
            session.add(
                Raspuns(
                    user_id=user_id,
                    intrebare_id=intrebare_id,
                    weight=weight
                )
            )

        await session.commit()


# =====================================================
# INTREBARE CURENTA
# =====================================================

async def get_current_question(index: int, language: str):
    async with async_session() as session:

        result = await session.execute(
            select(Intrebare).where(
                Intrebare.index == index,
                Intrebare.language == language
            )
        )

        return result.scalar_one_or_none()


# =====================================================
# 🔥 CALCUL SCOR — SUMA PUNCTAJ
# =====================================================

async def calculate_score_by_category(user_id: int):
    """
    Ia doar raspunsurile YES
    Aduna punctajul intrebarilor
    Returneaza scor pe fiecare categorie
    """

    async with async_session() as session:

        stmt = (
            select(
                Intrebare.categorie,
                func.sum(Intrebare.weight).label("scor")
            )
            .select_from(Raspuns)
            .join(Intrebare, Intrebare.id == Raspuns.intrebare_id)
            .where(
                Raspuns.user_id == user_id,
                Raspuns.weight == "YES"   # 🔥 DOAR DA puncte
            )
            .group_by(Intrebare.categorie)
        )

        result = await session.execute(stmt)

        return result.all()


# =====================================================
# NIVEL RISC DIN INTERVAL
# =====================================================

async def get_nivel_risc(categorie: str, scor: int):

    async with async_session() as session:

        stmt = select(PragRisc).where(
            PragRisc.categorie == categorie,
            PragRisc.scor_min <= scor,
            PragRisc.scor_max >= scor
        )

        result = await session.execute(stmt)
        prag = result.scalar_one_or_none()

        if prag:
            return prag.nivel

        return "Necunoscut"


# =====================================================
# FINALIZARE TEST
# =====================================================

async def finalize_test(user_id: int):
    """
    1. Calculeaza scor pe categorii
    2. Determina risc din interval
    3. Salveaza rezultate
    """

    scores = await calculate_score_by_category(user_id)

    rezultate_finale = []

    async with async_session() as session:

        for categorie, scor in scores:

            nivel = await get_nivel_risc(categorie, scor)

            rezultat = Rezultat(
                user_id=user_id,
                categorie=categorie,
                scor=scor,
                nivel=nivel
            )

            session.add(rezultat)

            rezultate_finale.append(
                (categorie, scor, nivel)
            )

        # marcam test finalizat
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(test_completed=True)
        )

        await session.commit()

    return rezultate_finale


# =====================================================
# RAPORT TEXT TELEGRAM
# =====================================================

def format_report(rezultate):

    text = "📊 Raport evaluare risc:\n\n"

    for categorie, scor, nivel in rezultate:

        text += (
            f"🔹 {categorie}\n"
            f"Scor: {scor}\n"
            f"Nivel risc: {nivel}\n\n"
        )

    return text
