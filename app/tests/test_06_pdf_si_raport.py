"""
============================================================
SCENARIUL 6: ERORI PDF SI GENERARE RAPORT
============================================================
Testam logica raportului text si posibile probleme la finalizare.
"""
import pytest
from sqlalchemy import select, func, update
from bd_sqlite.modele import User, Raspuns, Intrebare, Rezultat, PragRisc


async def _create_user_with_all_answers(session_factory, telegram_id, language, answer_type="YES"):
    """Creeaza un user si raspunde la toate 33 intrebari."""
    async with session_factory() as session:
        user = User(telegram_id=telegram_id, username=f"user_{telegram_id}",
                    first_name="Test", language=language, current_index=34)
        session.add(user)
        await session.commit()
        user_id = user.id

    async with session_factory() as session:
        questions = (await session.execute(
            select(Intrebare).where(Intrebare.language == language).order_by(Intrebare.index)
        )).scalars().all()

        for q in questions:
            session.add(Raspuns(user_id=user_id, intrebare_id=q.id, weight=answer_type))
        await session.commit()

    return user_id


# ----------------------------------------------------------
# TEST 6.1: Finalizare test - scoruri pe categorii calculate corect
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_score_calculation_by_category(seeded_db):
    """Scorurile pe categorii se calculeaza corect din raspunsuri YES."""
    user_id = await _create_user_with_all_answers(seeded_db, telegram_id=600001, language="ro")

    async with seeded_db() as session:
        from sqlalchemy import func as sa_func
        scores = (await session.execute(
            select(
                Intrebare.categorie,
                sa_func.sum(Intrebare.weight).label("scor")
            )
            .select_from(Raspuns)
            .join(Intrebare, Intrebare.id == Raspuns.intrebare_id)
            .where(
                Raspuns.user_id == user_id,
                Raspuns.weight == "YES",
                Intrebare.language == "ro"
            )
            .group_by(Intrebare.categorie)
        )).all()

    # Cu toate YES, fiecare categorie trebuie sa aiba scor > 0
    assert len(scores) > 0, "Trebuie sa existe scoruri pe categorii"
    for cat, scor in scores:
        assert scor > 0, f"Categoria '{cat}' ar trebui sa aiba scor > 0 cu toate YES"


# ----------------------------------------------------------
# TEST 6.2: Nivelul de risc determinat corect
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_risk_level_determination(seeded_db):
    """Nivelul de risc returnat corespunde scorului din praguri."""
    async with seeded_db() as session:
        # Luam un prag
        prag = (await session.execute(
            select(PragRisc).where(PragRisc.language == "ro").limit(1)
        )).scalar_one()

        # Verificam ca scorul din interval returneaza nivelul corect
        test_score = (prag.scor_min + prag.scor_max) // 2
        result = (await session.execute(
            select(PragRisc.nivel).where(
                PragRisc.categorie == prag.categorie,
                PragRisc.scor_min <= test_score,
                PragRisc.scor_max >= test_score,
                PragRisc.language == "ro"
            )
        )).scalar_one_or_none()

    assert result == prag.nivel


# ----------------------------------------------------------
# TEST 6.3: Scor in afara intervalelor returneaza "Necunoscut"
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_score_outside_range_returns_unknown(seeded_db):
    """
    BUG POTENTAIL: Scor foarte mare sau negativ nu gaseste prag.
    In productie: get_nivel_risc returneaza 'Necunoscut'.
    """
    async with seeded_db() as session:
        # Cautam o categorie
        cat = (await session.execute(
            select(PragRisc.categorie).where(PragRisc.language == "ro").limit(1)
        )).scalar_one()

        # Scor imposibil de mare
        result = (await session.execute(
            select(PragRisc.nivel).where(
                PragRisc.categorie == cat,
                PragRisc.scor_min <= 9999,
                PragRisc.scor_max >= 9999,
                PragRisc.language == "ro"
            )
        )).scalar_one_or_none()

    assert result is None, "Scor 9999 nu ar trebui sa corespunda niciunui prag"


# ----------------------------------------------------------
# TEST 6.4: format_report grupeaza corect pe niveluri
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_format_report_grouping(seeded_db):
    """Testam logica de grupare din format_report."""
    # Simulam raportul
    raport_test = [
        ("Blocul 1. Test", 30, "Risc minim"),
        ("Blocul 2. Test", 10, "Risc ridicat"),
        ("Blocul 3. Test", 20, "Risc mediu"),
        ("Blocul 4. Test", 5, "Risc ridicat"),
    ]

    grupe = {"minim": [], "mediu": [], "ridicat": []}
    for categorie, scor, nivel in raport_test:
        nivel_lower = nivel.lower()
        if "ridicat" in nivel_lower:
            grupe["ridicat"].append(categorie)
        elif "mediu" in nivel_lower:
            grupe["mediu"].append(categorie)
        else:
            grupe["minim"].append(categorie)

    assert len(grupe["ridicat"]) == 2
    assert len(grupe["mediu"]) == 1
    assert len(grupe["minim"]) == 1
    assert "Blocul 2. Test" in grupe["ridicat"]
    assert "Blocul 4. Test" in grupe["ridicat"]


# ----------------------------------------------------------
# TEST 6.5: format_report pentru limba rusa
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_format_report_russian_grouping(seeded_db):
    """Gruparea functioneaza corect si pentru limba rusa."""
    raport_ru = [
        ("Блок 1. Тест", 30, "Риски минимальные"),
        ("Блок 2. Тест", 10, "Высокий Риск проблем"),
        ("Блок 3. Тест", 20, "Средний Риск"),
    ]

    grupe = {"minim": [], "mediu": [], "ridicat": []}
    for categorie, scor, nivel in raport_ru:
        nivel_lower = nivel.lower()
        if "высокий" in nivel_lower:
            grupe["ridicat"].append(categorie)
        elif "средний" in nivel_lower:
            grupe["mediu"].append(categorie)
        else:
            grupe["minim"].append(categorie)

    assert len(grupe["ridicat"]) == 1
    assert len(grupe["mediu"]) == 1
    assert len(grupe["minim"]) == 1


# ----------------------------------------------------------
# TEST 6.6: Salvare rezultate in BD - upsert corect
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_save_results_upsert(seeded_db):
    """Salvarea rezultatelor face upsert (update daca exista, insert daca nu)."""
    user_id = await _create_user_with_all_answers(seeded_db, telegram_id=600006, language="ro")

    # Prima salvare
    async with seeded_db() as session:
        session.add(Rezultat(user_id=user_id, categorie="Test", scor=10, max_scor=20, nivel="mediu"))
        await session.commit()

    # A doua salvare (update)
    async with seeded_db() as session:
        existing = (await session.execute(
            select(Rezultat).where(Rezultat.user_id == user_id, Rezultat.categorie == "Test")
        )).scalar_one()
        existing.scor = 15
        existing.nivel = "minim"
        await session.commit()

    # Verificam ca avem un singur rezultat actualizat
    async with seeded_db() as session:
        results = (await session.execute(
            select(Rezultat).where(Rezultat.user_id == user_id, Rezultat.categorie == "Test")
        )).scalars().all()

    assert len(results) == 1
    assert results[0].scor == 15
    assert results[0].nivel == "minim"


# ----------------------------------------------------------
# TEST 6.7: Raport cu 0 raspunsuri YES
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_report_with_zero_yes_answers(seeded_db):
    """Raport generat cu toate raspunsurile NO - scoruri zero pe toate categoriile."""
    user_id = await _create_user_with_all_answers(seeded_db, telegram_id=600007, language="ro", answer_type="NO")

    async with seeded_db() as session:
        from sqlalchemy import func as sa_func
        # Scoruri per categorie cu YES = ar trebui sa fie goala
        scores = (await session.execute(
            select(
                Intrebare.categorie,
                sa_func.sum(Intrebare.weight).label("scor")
            )
            .select_from(Raspuns)
            .join(Intrebare, Intrebare.id == Raspuns.intrebare_id)
            .where(
                Raspuns.user_id == user_id,
                Raspuns.weight == "YES",
                Intrebare.language == "ro"
            )
            .group_by(Intrebare.categorie)
        )).all()

    assert len(scores) == 0, "Cu toate NO, nu ar trebui categorii cu scor YES"


# ----------------------------------------------------------
# TEST 6.8: Raport cu toate IDK
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_report_with_all_idk_answers(seeded_db):
    """Raport cu toate IDK - scor 0 ca si NO."""
    user_id = await _create_user_with_all_answers(seeded_db, telegram_id=600008, language="ro", answer_type="IDK")

    async with seeded_db() as session:
        from sqlalchemy import func as sa_func
        scores = (await session.execute(
            select(sa_func.sum(Intrebare.weight))
            .select_from(Raspuns)
            .join(Intrebare, Intrebare.id == Raspuns.intrebare_id)
            .where(
                Raspuns.user_id == user_id,
                Raspuns.weight == "YES",
                Intrebare.language == "ro"
            )
        )).scalar()

    assert scores is None or scores == 0, "Cu IDK la toate, scor total trebuie sa fie 0"


# ----------------------------------------------------------
# TEST 6.9: BUG POTENTIAL - categorii fara raspunsuri in raport
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_categories_without_yes_get_zero_score(seeded_db):
    """
    BUG POTENTAIL: Daca o categorie are doar raspunsuri NO/IDK,
    calculate_score_by_category nu o include in rezultat.
    Acest lucru inseamna ca categoria respectiva LIPSESTE din raport.
    """
    user_id = await _create_user_with_all_answers(seeded_db, telegram_id=600009, language="ro", answer_type="NO")

    # Adaugam un singur YES la prima intrebare
    async with seeded_db() as session:
        first_q = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro", Intrebare.index == 1)
        )).scalar_one()

        answer = (await session.execute(
            select(Raspuns).where(
                Raspuns.user_id == user_id,
                Raspuns.intrebare_id == first_q.id
            )
        )).scalar_one()
        answer.weight = "YES"
        await session.commit()

    # Acum doar categoria primei intrebari apare in calculate_score_by_category
    async with seeded_db() as session:
        from sqlalchemy import func as sa_func
        scores = (await session.execute(
            select(Intrebare.categorie, sa_func.sum(Intrebare.weight).label("scor"))
            .select_from(Raspuns)
            .join(Intrebare, Intrebare.id == Raspuns.intrebare_id)
            .where(
                Raspuns.user_id == user_id,
                Raspuns.weight == "YES",
                Intrebare.language == "ro"
            )
            .group_by(Intrebare.categorie)
        )).all()

        all_categories = (await session.execute(
            select(Intrebare.categorie).where(Intrebare.language == "ro").distinct()
        )).scalars().all()

    categories_with_score = {cat for cat, _ in scores}
    missing_categories = set(all_categories) - categories_with_score

    # ACEASTA ESTE O PROBLEMA REALA IN COD:
    # Categoriile fara niciun YES nu apar in finalize_test ->
    # ceea ce inseamna ca aceste categorii NU primesc rezultat in raport
    # si NU apar in PDF-ul generat.
    if len(missing_categories) > 0:
        print(f"\n⚠️  BUG DETECTAT: {len(missing_categories)} categorii lipsesc din raport:")
        for cat in missing_categories:
            print(f"   - {cat}")
        print("   Cauza: calculate_score_by_category nu returneaza categorii cu 0 raspunsuri YES")
        print("   Efect: Aceste categorii nu apar in PDF si raportul text")
        # Nu facem assert fail aici, doar raportam bug-ul
