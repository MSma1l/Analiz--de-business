from sqlalchemy import select, update, delete, func, and_
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
    weight = YES / NO / IDK
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

async def get_max_score_by_category(language: str):
    """
    Returnează scorul maxim posibil pentru fiecare categorie
    (suma tuturor weight-urilor din întrebări)
    """
    async with async_session() as session:
        stmt = (
            select(
                Intrebare.categorie,
                func.sum(Intrebare.weight).label("max_scor")
            )
            .where(Intrebare.language == language)
            .group_by(Intrebare.categorie)
        )
        result = await session.execute(stmt)
        return {categorie: max_scor for categorie, max_scor in result.all()}


async def calculate_score_by_category(user_id: int, language: str):
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
                Raspuns.weight == "YES",
                Intrebare.language == language
            )
            .group_by(Intrebare.categorie)
        )

        result = await session.execute(stmt)

        return result.all()


# =====================================================
# NIVEL RISC DIN INTERVAL
# =====================================================

async def get_nivel_risc(categorie: str, scor: int, language: str):
    """
    Găsește nivelul de risc pentru o categorie și scor dat
    """

    async with async_session() as session:

        stmt = select(PragRisc.nivel).where(
            PragRisc.categorie == categorie,
            PragRisc.scor_min <= scor,
            PragRisc.scor_max >= scor,
            PragRisc.language == language
        )

        result = await session.execute(stmt)
        nivel = result.scalar_one_or_none()

        return nivel or "Necunoscut"


# =====================================================
# SALVARE REZULTATE ÎN BD
# =====================================================

async def save_results_to_db(user_id: int, raport, max_scores: dict):
    """
    Salvează rezultatele pe categorii în tabela Rezultat
    raport = [(categorie, scor, nivel), ...]
    max_scores = {categorie: max_scor}
    """
    async with async_session() as session:
        
        for categorie, scor, nivel in raport:
            max_scor = max_scores.get(categorie, scor)  # Default la scor actual dacă nu găsește
            
            # Verifică dacă există deja rezultat pentru această categorie
            result = await session.execute(
                select(Rezultat).where(
                    Rezultat.user_id == user_id,
                    Rezultat.categorie == categorie
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Actualizează rezultatul existent
                existing.scor = scor
                existing.max_scor = max_scor
                existing.nivel = nivel
            else:
                # Adaugă rezultat nou
                session.add(
                    Rezultat(
                        user_id=user_id,
                        categorie=categorie,
                        scor=scor,
                        max_scor=max_scor,
                        nivel=nivel
                    )
                )
        
        await session.commit()


# =====================================================
# RESETARE REZULTATE USER
# =====================================================

async def reset_user_results(user_id: int):
    """
    Șterge toate rezultatele vechi și resetează scorul și testul
    """
    async with async_session() as session:
        
        # Șterge rezultatele
        await session.execute(
            delete(Rezultat).where(Rezultat.user_id == user_id)
        )
        
        # Resetează user
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(score=0, test_completed=False, current_index=1)
        )
        
        await session.commit()


# =====================================================
# PRELUARE REZULTATE USER
# =====================================================

async def get_user_results(user_id: int):
    """
    Returnează rezultatele salvate pentru un utilizator
    Returns: dict {categorie: {"scor": scor, "max_scor": max_scor, "nivel": nivel}}
    """
    async with async_session() as session:
        
        result = await session.execute(
            select(Rezultat.categorie, Rezultat.scor, Rezultat.max_scor, Rezultat.nivel)
            .where(Rezultat.user_id == user_id)
            .order_by(Rezultat.categorie)
        )
        
        rows = result.all()
        
        # Returnează dict pentru acces ușor
        return {
            categorie: {"scor": scor, "max_scor": max_scor or scor, "nivel": nivel}
            for categorie, scor, max_scor, nivel in rows
        }


# =====================================================
# FINALIZARE TEST
# =====================================================

async def finalize_test(user_id: int):
    """
    1. Calculează scor pe categorii
    2. Determină risc din interval
    3. Salvează rezultate în BD (inclusiv max_scor)
    4. Marchează test ca finalizat
    """
    
    async with async_session() as session:
        
        # 1. Aflăm limba utilizatorului
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one()
        language = user.language or "ro"
        
        # 2. Obținem scorurile maxime posibile pe categorii
        max_scores = await get_max_score_by_category(language)
        
        # 3. Calculăm scorul obținut pe categorii
        scoruri_categorii = await calculate_score_by_category(user_id, language)
        
        # 4. Construim raportul complet cu niveluri de risc
        raport = []
        for categorie, scor in scoruri_categorii:
            nivel = await get_nivel_risc(categorie, scor, language)
            raport.append((categorie, scor, nivel))
        
        # 5. Salvăm rezultatele în BD (cu max_scor)
        await save_results_to_db(user_id, raport, max_scores)
        
        # 6. Calculăm scorul total
        scor_total = sum(scor for _, scor, _ in raport)
        
        # 7. Marcăm testul ca finalizat și salvăm scorul total
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(score=scor_total, test_completed=True)
        )
        
        await session.commit()
    
    return raport


# =====================================================
# RAPORT TEXT TELEGRAM
# =====================================================

def format_report(raport, language="ro"):
    """
    Formatează raportul pentru afișare în Telegram
    raport = [(categorie, scor, nivel), ...]
    """
    
    # Determinăm nivelul general de risc
    niveluri = [nivel.lower() for _, _, nivel in raport]
    
    if language == "ro":
        if any("ridicat" in nivel or "înalt" in nivel for nivel in niveluri):
            nivel_general = "Risc Înalt - acționați urgent"
        elif any("mediu" in nivel for nivel in niveluri):
            nivel_general = "Risc Mediu - verificați periodic"
        else:
            nivel_general = "Risc Minim - recomandat control anual"
        
        text = "📊 Raport evaluare risc:\n\n"
        
        text += f"📌 Nivel general: {nivel_general}\n"
    
    else:  # ru
        if any("высокий" in nivel for nivel in niveluri):
            nivel_general = "Высокий риск - действовать срочно"
        elif any("средний" in nivel for nivel in niveluri):
            nivel_general = "Средний риск - проверять периодически"
        else:
            nivel_general = "Минимальный риск - рекомендован ежегодный контроль"
        
        text = "📊 Отчет оценки риска:\n\n"
        
        text += f"📌 Общий уровень: {nivel_general}\n"
    
    return text