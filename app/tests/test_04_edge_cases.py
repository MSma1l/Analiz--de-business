"""
============================================================
SCENARIUL 4: EDGE CASES SI CAZURI NEPREVAZUTE
============================================================
Testam situatii la limita care pot cauza buguri.
"""
import pytest
from sqlalchemy import select, func, update
from bd_sqlite.modele import User, Raspuns, Intrebare, Rezultat, PragRisc


async def _create_user(session_factory, telegram_id, language="ro", **kwargs):
    async with session_factory() as session:
        user = User(telegram_id=telegram_id, username=f"user_{telegram_id}",
                    first_name="Test", language=language, current_index=1, **kwargs)
        session.add(user)
        await session.commit()
        return user.id


# ----------------------------------------------------------
# TEST 4.1: User fara limba setata
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_user_without_language(seeded_db):
    """BUG POTENCIAL: User cu language=None incearca sa inceapa testul."""
    async with seeded_db() as session:
        user = User(telegram_id=400001, username="no_lang", first_name="NoLang", current_index=1)
        session.add(user)
        await session.commit()
        user_id = user.id

    # In productie, get_current_question(1, None) ar returna None
    async with seeded_db() as session:
        result = (await session.execute(
            select(Intrebare).where(Intrebare.language == None, Intrebare.index == 1)
        )).scalar_one_or_none()

    assert result is None, "Cu limba None, nu ar trebui sa gaseasca intrebari"


# ----------------------------------------------------------
# TEST 4.2: User apasa /start de mai multe ori
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_multiple_start_commands(seeded_db):
    """Apasarea /start de mai multe ori nu trebuie sa creeze useri duplicati."""
    # Simulam get_or_create_user de 5 ori
    user_ids = []
    for _ in range(5):
        async with seeded_db() as session:
            result = (await session.execute(
                select(User).where(User.telegram_id == 400002)
            )).scalar_one_or_none()

            if result:
                user_ids.append(result.id)
            else:
                user = User(telegram_id=400002, username="multi_start", first_name="Multi")
                session.add(user)
                await session.commit()
                user_ids.append(user.id)

    # Toti trebuie sa aiba acelasi id
    assert len(set(user_ids)) == 1, f"Trebuie un singur user, gasit IDs diferite: {set(user_ids)}"


# ----------------------------------------------------------
# TEST 4.3: current_index in afara range-ului (< 1)
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_current_index_below_range(seeded_db):
    """BUG POTENTAIL: current_index = 0 sau negativ."""
    user_id = await _create_user(seeded_db, telegram_id=400003)

    async with seeded_db() as session:
        await session.execute(
            update(User).where(User.id == user_id).values(current_index=0)
        )
        await session.commit()

    # Intrebarea cu index 0 nu exista
    async with seeded_db() as session:
        q = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro", Intrebare.index == 0)
        )).scalar_one_or_none()

    assert q is None, "current_index=0 nu are intrebare corespunzatoare"


# ----------------------------------------------------------
# TEST 4.4: current_index depaseste 33
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_current_index_exceeds_33(seeded_db):
    """Dupa ultima intrebare, current_index devine 34 — nu trebuie erori."""
    user_id = await _create_user(seeded_db, telegram_id=400004)

    async with seeded_db() as session:
        await session.execute(
            update(User).where(User.id == user_id).values(current_index=34)
        )
        await session.commit()

    async with seeded_db() as session:
        q = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro", Intrebare.index == 34)
        )).scalar_one_or_none()

    assert q is None, "Index 34 nu trebuie sa returneze intrebare"


# ----------------------------------------------------------
# TEST 4.5: Username foarte lung
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_very_long_username(seeded_db):
    """Username-uri foarte lungi nu trebuie sa provoace erori."""
    long_name = "a" * 50  # Limita de 50 in model
    async with seeded_db() as session:
        user = User(telegram_id=400005, username=long_name, first_name=long_name, language="ro")
        session.add(user)
        await session.commit()

    async with seeded_db() as session:
        user = (await session.execute(
            select(User).where(User.telegram_id == 400005)
        )).scalar_one()

    assert len(user.username) == 50


# ----------------------------------------------------------
# TEST 4.6: Scor 0 pe toate categoriile (toate raspunsuri NO)
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_all_no_answers_zero_score(seeded_db):
    """Daca userul raspunde NO la toate, scorul per categorie e 0."""
    user_id = await _create_user(seeded_db, telegram_id=400006)

    async with seeded_db() as session:
        questions = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro").order_by(Intrebare.index)
        )).scalars().all()

        for q in questions:
            session.add(Raspuns(user_id=user_id, intrebare_id=q.id, weight="NO"))
        await session.commit()

    # Calculam scorurile: suma YES * weight = 0 pt fiecare categorie
    async with seeded_db() as session:
        from sqlalchemy import func as sa_func
        result = (await session.execute(
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

    # Niciun scor nu ar trebui sa existe (toate NO)
    assert len(result) == 0, "Cu toate raspunsurile NO, nu ar trebui scoruri YES"


# ----------------------------------------------------------
# TEST 4.7: Scor maxim (toate raspunsuri YES)
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_all_yes_answers_max_score(seeded_db):
    """Daca userul raspunde YES la toate, scorul total trebuie sa fie > 0."""
    user_id = await _create_user(seeded_db, telegram_id=400007)

    async with seeded_db() as session:
        questions = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro").order_by(Intrebare.index)
        )).scalars().all()

        for q in questions:
            session.add(Raspuns(user_id=user_id, intrebare_id=q.id, weight="YES"))
        await session.commit()

    async with seeded_db() as session:
        from sqlalchemy import func as sa_func
        total = (await session.execute(
            select(sa_func.sum(Intrebare.weight))
            .select_from(Raspuns)
            .join(Intrebare, Intrebare.id == Raspuns.intrebare_id)
            .where(
                Raspuns.user_id == user_id,
                Raspuns.weight == "YES",
                Intrebare.language == "ro"
            )
        )).scalar()

    assert total is not None and total > 0, f"Scorul total cu YES la toate trebuie > 0, gasit {total}"


# ----------------------------------------------------------
# TEST 4.8: Categorii identice in ambele limbi
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_categories_count_same_both_languages(seeded_db):
    """Numarul de categorii trebuie sa fie egal in ro si ru."""
    async with seeded_db() as session:
        cats_ro = (await session.execute(
            select(Intrebare.categorie).where(Intrebare.language == "ro").distinct()
        )).scalars().all()

        cats_ru = (await session.execute(
            select(Intrebare.categorie).where(Intrebare.language == "ru").distinct()
        )).scalars().all()

    assert len(cats_ro) == len(cats_ru), \
        f"Ro are {len(cats_ro)} categorii, Ru are {len(cats_ru)}"


# ----------------------------------------------------------
# TEST 4.9: 33 intrebari per limba
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_33_questions_per_language(seeded_db):
    """Fiecare limba trebuie sa aiba exact 33 intrebari."""
    for lang in ["ro", "ru"]:
        async with seeded_db() as session:
            count = (await session.execute(
                select(func.count(Intrebare.id)).where(Intrebare.language == lang)
            )).scalar()

        assert count == 33, f"Limba {lang} are {count} intrebari, asteptam 33"


# ----------------------------------------------------------
# TEST 4.10: Pragurile de risc acopera toate scorurile posibile
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_risk_thresholds_cover_all_scores(seeded_db):
    """Fiecare categorie trebuie sa aiba praguri care acopera de la 0 la max_score."""
    async with seeded_db() as session:
        # Obtinem categoriile si max score per categorie
        categories = (await session.execute(
            select(Intrebare.categorie, func.sum(Intrebare.weight).label("max_score"))
            .where(Intrebare.language == "ro")
            .group_by(Intrebare.categorie)
        )).all()

        for cat, max_score in categories:
            thresholds = (await session.execute(
                select(PragRisc)
                .where(PragRisc.categorie == cat, PragRisc.language == "ro")
                .order_by(PragRisc.scor_min)
            )).scalars().all()

            assert len(thresholds) > 0, f"Categoria '{cat}' nu are praguri de risc"

            # Verificam ca scor=0 este acoperit
            covered_zero = any(t.scor_min <= 0 for t in thresholds)
            assert covered_zero, f"Categoria '{cat}': scor 0 nu este acoperit de niciun prag"


# ----------------------------------------------------------
# TEST 4.11: User cu test_completed=True nu trebuie sa piarda datele
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_completed_test_data_persists(seeded_db):
    """Dupa finalizare, rezultatele raman in BD."""
    user_id = await _create_user(seeded_db, telegram_id=400011)

    async with seeded_db() as session:
        await session.execute(
            update(User).where(User.id == user_id).values(test_completed=True, score=75)
        )
        session.add(Rezultat(user_id=user_id, categorie="Test", scor=75, max_scor=100, nivel="mediu"))
        await session.commit()

    # Verificam persistenta
    async with seeded_db() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()
        results = (await session.execute(
            select(Rezultat).where(Rezultat.user_id == user_id)
        )).scalars().all()

    assert user.test_completed is True
    assert user.score == 75
    assert len(results) == 1


# ----------------------------------------------------------
# TEST 4.12: Doua teste consecutive (retestare)
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_retest_after_language_change(seeded_db):
    """Userul termina testul, schimba limba, incepe din nou."""
    user_id = await _create_user(seeded_db, telegram_id=400012)

    # Simulam finalizare test
    async with seeded_db() as session:
        q = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro", Intrebare.index == 1)
        )).scalar_one()
        session.add(Raspuns(user_id=user_id, intrebare_id=q.id, weight="YES"))
        session.add(Rezultat(user_id=user_id, categorie="Test", scor=10, max_scor=20, nivel="mediu"))
        await session.execute(
            update(User).where(User.id == user_id).values(
                test_completed=True, score=10, current_index=34
            )
        )
        await session.commit()

    # Simulam schimbare limba (reset complet)
    from sqlalchemy import delete
    async with seeded_db() as session:
        await session.execute(delete(Raspuns).where(Raspuns.user_id == user_id))
        await session.execute(delete(Rezultat).where(Rezultat.user_id == user_id))
        await session.execute(
            update(User).where(User.id == user_id).values(
                language="ru", current_index=1, test_completed=False, score=0
            )
        )
        await session.commit()

    # Verificam resetul complet
    async with seeded_db() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()
        answers = (await session.execute(
            select(func.count(Raspuns.id)).where(Raspuns.user_id == user_id)
        )).scalar()
        results = (await session.execute(
            select(func.count(Rezultat.id)).where(Rezultat.user_id == user_id)
        )).scalar()

    assert user.language == "ru"
    assert user.current_index == 1
    assert user.test_completed is False
    assert answers == 0
    assert results == 0


# ----------------------------------------------------------
# TEST 4.13: BUG - company_position cu test_completed=False
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_company_position_requires_completed_test(seeded_db):
    """Utilizatorul nu poate vedea pozitia companiei fara test finalizat."""
    user_id = await _create_user(seeded_db, telegram_id=400013)

    async with seeded_db() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()

    # Logica din meniu.py: if not user.test_completed or user.score is None
    assert user.test_completed is False or user.score is None, \
        "Fara test completat, nu ar trebui sa se poata vedea pozitia"


# ----------------------------------------------------------
# TEST 4.14: BUG POTENTIAL - number_company e Integer dar primeste text
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_phone_number_as_integer_overflow(seeded_db):
    """
    BUG DETECTAT: number_company este Integer in model, dar numere de telefon
    mari (ex: +37369123456) pot depasi limita Integer (2^31-1 = 2147483647).
    Numarul +37369123456 = 37369123456 depaseste Integer.
    """
    user_id = await _create_user(seeded_db, telegram_id=400014)

    # Incercam sa salvam un numar de telefon mare
    big_number = 37369123456  # Numar tipic moldovenesc cu prefix

    try:
        async with seeded_db() as session:
            await session.execute(
                update(User).where(User.id == user_id).values(number_company=big_number)
            )
            await session.commit()

        async with seeded_db() as session:
            user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()
            # SQLite suporta numere mari, dar Integer Python ar putea cauza probleme
            assert user.number_company == big_number
    except Exception as e:
        pytest.fail(f"BUG: Numarul de telefon mare cauzeaza eroare: {e}")
