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
    """
    Setează limba și RESETEAZĂ tot testul.
    Șterge răspunsurile și rezultatele vechi.
    """
    async with async_session() as session:

        # Găsim userul pentru a-i lua ID-ul intern
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            return

        # Resetăm: limbă, index, test_completed, scor
        await session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(
                language=language,
                current_index=1,
                test_completed=False,
                score=0
            )
        )

        # Ștergem răspunsurile vechi
        await session.execute(
            delete(Raspuns).where(Raspuns.user_id == user.id)
        )

        # Ștergem rezultatele vechi
        await session.execute(
            delete(Rezultat).where(Rezultat.user_id == user.id)
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
# CALCUL SCOR — SUMA PUNCTAJ
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
            max_scor = max_scores.get(categorie, scor)

            result = await session.execute(
                select(Rezultat).where(
                    Rezultat.user_id == user_id,
                    Rezultat.categorie == categorie
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.scor = scor
                existing.max_scor = max_scor
                existing.nivel = nivel
            else:
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

        await session.execute(
            delete(Rezultat).where(Rezultat.user_id == user_id)
        )

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
    5. Returnează (raport, language)
    """

    async with async_session() as session:

        # 1. Aflăm limba utilizatorului
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one()
        language = user.language or "ro"

    # 2. Obținem scorurile maxime posibile pe categorii
    #    ✅ Apelat DUPĂ ce sesiunea s-a închis
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

    # 6. Calculăm scorul total și marcăm testul ca finalizat
    scor_total = sum(scor for _, scor, _ in raport)

    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(score=scor_total, test_completed=True)
        )
        await session.commit()

    # ✅ Returnează (raport, language) - cele 2 valori
    return raport, language


# =====================================================
# RAPORT TEXT TELEGRAM
# =====================================================

def format_report(raport, language="ro"):
    """
    Formatează raportul pentru afișare în Telegram.
    Grupează blocurile pe niveluri de risc cu recomandări.
    raport = [(categorie, scor, nivel), ...]

    Exemplu output:
    📊 Итоговый результат:

    🟢 Риски минимальные - рекомендуем проверять раз в год
        └ 2 Блока (1 и 4)

    🟡 Средний Риск - обратитесь когда будут проблемы
        └ 3 Блока (2, 3 и 5)

    🔴 Высокий Риск проблем - срочно примите меры
        └ 2 Блока (6 и 7)
    """

    # =====================================================
    # TEXTE PE LIMBĂ
    # =====================================================

    if language == "ro":
        titlu = "📊 *Rezultat final:*"
        texte_risc = {
            "minim":   "Riscuri minime - recomandăm verificare anuală",
            "mediu":   "Risc Mediu - consultați când apar probleme",
            "ridicat": "Risc Ridicat - luați măsuri urgente"
        }
        separator = " și "
        cuvant_bloc_singular = "Bloc"
        cuvant_bloc_plural = "Blocuri"
        text_final = "\n📄 Raportul PDF detaliat a fost generat."
    else:  # ru
        titlu = "📊 *Итоговый результат:*"
        texte_risc = {
            "minim":   "Риски минимальные - рекомендуем проверять раз в год",
            "mediu":   "Средний Риск - обратитесь когда будут проблемы",
            "ridicat": "Высокий Риск проблем - срочно примите меры"
        }
        separator = " и "
        cuvant_bloc_singular = "Блок"
        cuvant_bloc_plural = "Блока"
        text_final = "\n📄 Детальный PDF отчет был сгенерирован."

    emoji_map = {
        "minim":   "🟢",
        "mediu":   "🟡",
        "ridicat": "🔴"
    }

    # =====================================================
    # EXTRAGE NUMĂRUL BLOCULUI
    # =====================================================

    def get_bloc_number(categorie: str) -> str:
        """
        Extrage numărul blocului din numele categoriei
        "Blocul 3. Finanțe..." → "3"
        "Блок 3. Финансы..."   → "3"
        """
        try:
            part = categorie.split(".")[0]        # "Blocul 3" sau "Блок 3"
            return part.strip().split(" ")[-1]    # "3"
        except:
            return categorie

    # =====================================================
    # GRUPARE BLOCURI PE NIVEL
    # =====================================================

    grupe = {"minim": [], "mediu": [], "ridicat": []}

    for item in raport:
        # ✅ Acceptă atât 3 cât și 4 valori (cu sau fără max_scor)
        if len(item) == 4:
            categorie, scor, max_scor, nivel = item
        else:
            categorie, scor, nivel = item

        nr = get_bloc_number(categorie)
        nivel_lower = nivel.lower()

        if language == "ro":
            if "ridicat" in nivel_lower or "înalt" in nivel_lower:
                grupe["ridicat"].append(nr)
            elif "mediu" in nivel_lower:
                grupe["mediu"].append(nr)
            else:
                grupe["minim"].append(nr)
        else:  # ru
            if "высокий" in nivel_lower:
                grupe["ridicat"].append(nr)
            elif "средний" in nivel_lower:
                grupe["mediu"].append(nr)
            else:
                grupe["minim"].append(nr)

    # =====================================================
    # CONSTRUIRE TEXT FINAL
    # =====================================================

    text = f"{titlu}\n\n"

    # Afișăm în ordinea: risc ridicat → mediu → minim
    for cheie in ["ridicat", "mediu", "minim"]:
        blocuri = grupe[cheie]

        if not blocuri:
            continue

        emoji = emoji_map[cheie]
        label = texte_risc[cheie]

        # Formatăm lista de blocuri
        if len(blocuri) == 1:
            blocuri_str = f"{cuvant_bloc_singular} {blocuri[0]}"
        else:
            if len(blocuri) == 2:
                joined = separator.join(blocuri)
            else:
                joined = ", ".join(blocuri[:-1]) + separator + blocuri[-1]

            blocuri_str = f"{len(blocuri)} {cuvant_bloc_plural} ({joined})"

        text += f"{emoji} {label}\n"
        text += f"    └ *{blocuri_str}*\n\n"

    text += text_final

    return text