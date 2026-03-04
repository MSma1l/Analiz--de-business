"""
============================================================
SCENARIUL 1: UTILIZATORUL NU TERMINA TESTUL
============================================================
Verificam ca raspunsurile partiale sunt salvate in BD si ca
utilizatorul poate relua testul de unde a ramas.
"""
import pytest
import pytest_asyncio
from sqlalchemy import select, func
from bd_sqlite.modele import User, Raspuns, Intrebare, Rezultat


# ----------------------------------------------------------
# Helper: creeaza un user si raspunde la N intrebari
# ----------------------------------------------------------
async def _create_user_and_answer(session_factory, telegram_id, language, num_answers):
    """Creeaza un user, raspunde la `num_answers` intrebari si returneaza user-ul."""
    async with session_factory() as session:
        user = User(telegram_id=telegram_id, username="test_user", first_name="Test", language=language, current_index=1)
        session.add(user)
        await session.commit()
        user_id = user.id

    # Raspundem la primele N intrebari
    async with session_factory() as session:
        questions = (await session.execute(
            select(Intrebare)
            .where(Intrebare.language == language)
            .order_by(Intrebare.index)
            .limit(num_answers)
        )).scalars().all()

        for i, q in enumerate(questions):
            session.add(Raspuns(user_id=user_id, intrebare_id=q.id, weight="YES"))

        # Actualizam current_index
        from sqlalchemy import update
        await session.execute(
            update(User).where(User.id == user_id).values(current_index=num_answers + 1)
        )
        await session.commit()

    return user_id


# ----------------------------------------------------------
# TEST 1.1: Raspunsurile partiale se salveaza corect
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_partial_answers_saved_in_db(seeded_db):
    """Utilizatorul raspunde la 10 din 33 intrebari — toate 10 trebuie salvate."""
    user_id = await _create_user_and_answer(seeded_db, telegram_id=100001, language="ro", num_answers=10)

    async with seeded_db() as session:
        count = (await session.execute(
            select(func.count(Raspuns.id)).where(Raspuns.user_id == user_id)
        )).scalar()

    assert count == 10, f"Asteptam 10 raspunsuri salvate, am gasit {count}"


# ----------------------------------------------------------
# TEST 1.2: current_index reflecta progresul
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_current_index_reflects_progress(seeded_db):
    """Dupa 15 raspunsuri, current_index trebuie sa fie 16."""
    user_id = await _create_user_and_answer(seeded_db, telegram_id=100002, language="ro", num_answers=15)

    async with seeded_db() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()

    assert user.current_index == 16, f"current_index asteptat 16, gasit {user.current_index}"


# ----------------------------------------------------------
# TEST 1.3: test_completed ramane False daca testul nu e terminat
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_incomplete_test_not_marked_completed(seeded_db):
    """Testul nu trebuie marcat ca terminat daca nu s-au raspuns la toate intrebarile."""
    user_id = await _create_user_and_answer(seeded_db, telegram_id=100003, language="ro", num_answers=20)

    async with seeded_db() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()

    assert user.test_completed is False, "Testul nu ar trebui sa fie marcat ca terminat"
    assert user.score is None or user.score == 0, "Scorul ar trebui sa fie None sau 0 pentru test incomplet"


# ----------------------------------------------------------
# TEST 1.4: Rezultatele NU exista pentru test incomplet
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_no_results_for_incomplete_test(seeded_db):
    """Tabela rezultate trebuie sa fie goala daca testul nu e terminat."""
    user_id = await _create_user_and_answer(seeded_db, telegram_id=100004, language="ro", num_answers=25)

    async with seeded_db() as session:
        results = (await session.execute(
            select(func.count(Rezultat.id)).where(Rezultat.user_id == user_id)
        )).scalar()

    assert results == 0, f"Nu ar trebui sa existe rezultate, dar am gasit {results}"


# ----------------------------------------------------------
# TEST 1.5: Reluarea testului dupa pauza
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_resume_test_after_pause(seeded_db):
    """Utilizatorul poate relua testul de unde a ramas si sa adauge raspunsuri noi."""
    user_id = await _create_user_and_answer(seeded_db, telegram_id=100005, language="ro", num_answers=10)

    # Verificam ca avem 10 raspunsuri
    async with seeded_db() as session:
        count_before = (await session.execute(
            select(func.count(Raspuns.id)).where(Raspuns.user_id == user_id)
        )).scalar()
    assert count_before == 10

    # Simulam ca utilizatorul reia si mai raspunde la 5 intrebari (11-15)
    async with seeded_db() as session:
        questions = (await session.execute(
            select(Intrebare)
            .where(Intrebare.language == "ro")
            .order_by(Intrebare.index)
            .offset(10)
            .limit(5)
        )).scalars().all()

        for q in questions:
            session.add(Raspuns(user_id=user_id, intrebare_id=q.id, weight="NO"))

        from sqlalchemy import update
        await session.execute(
            update(User).where(User.id == user_id).values(current_index=16)
        )
        await session.commit()

    # Acum trebuie sa avem 15 raspunsuri
    async with seeded_db() as session:
        count_after = (await session.execute(
            select(func.count(Raspuns.id)).where(Raspuns.user_id == user_id)
        )).scalar()

    assert count_after == 15, f"Dupa reluare ar trebui 15 raspunsuri, avem {count_after}"


# ----------------------------------------------------------
# TEST 1.6: Raspunsurile vechi nu se pierd la reluare
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_old_answers_preserved_on_resume(seeded_db):
    """La reluare, raspunsurile vechi raman intacte cu valorile lor."""
    user_id = await _create_user_and_answer(seeded_db, telegram_id=100006, language="ro", num_answers=5)

    # Verificam ca toate 5 raspunsuri au weight="YES"
    async with seeded_db() as session:
        answers = (await session.execute(
            select(Raspuns).where(Raspuns.user_id == user_id)
        )).scalars().all()

    assert len(answers) == 5
    for a in answers:
        assert a.weight == "YES", f"Raspunsul {a.id} ar trebui sa fie YES, gasit {a.weight}"


# ----------------------------------------------------------
# TEST 1.7: Schimbarea limbii sterge raspunsurile partial
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_language_change_resets_partial_answers(seeded_db):
    """Daca utilizatorul schimba limba, toate raspunsurile partiale se sterg."""
    user_id = await _create_user_and_answer(seeded_db, telegram_id=100007, language="ro", num_answers=20)

    # Simulam set_user_language - sterge raspunsuri, reseteaza index
    from sqlalchemy import update, delete
    async with seeded_db() as session:
        await session.execute(delete(Raspuns).where(Raspuns.user_id == user_id))
        await session.execute(delete(Rezultat).where(Rezultat.user_id == user_id))
        await session.execute(
            update(User).where(User.id == user_id).values(
                language="ru", current_index=1, test_completed=False, score=0
            )
        )
        await session.commit()

    # Verificam reset complet
    async with seeded_db() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()
        answers_count = (await session.execute(
            select(func.count(Raspuns.id)).where(Raspuns.user_id == user_id)
        )).scalar()

    assert user.language == "ru"
    assert user.current_index == 1
    assert user.test_completed is False
    assert answers_count == 0, f"Dupa schimbarea limbii, raspunsurile ar trebui sterse. Gasit: {answers_count}"


# ----------------------------------------------------------
# TEST 1.8: Testul complet cu 33 raspunsuri
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_complete_test_33_answers(seeded_db):
    """Utilizatorul raspunde la toate 33 intrebari - testul se marcheaza ca finalizat."""
    user_id = await _create_user_and_answer(seeded_db, telegram_id=100008, language="ro", num_answers=33)

    # Simulam finalize_test: marcam ca terminat
    from sqlalchemy import update
    async with seeded_db() as session:
        await session.execute(
            update(User).where(User.id == user_id).values(test_completed=True, score=50)
        )
        await session.commit()

    async with seeded_db() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()
        count = (await session.execute(
            select(func.count(Raspuns.id)).where(Raspuns.user_id == user_id)
        )).scalar()

    assert user.test_completed is True
    assert count == 33
    assert user.current_index == 34


# ----------------------------------------------------------
# TEST 1.9: Raspunsurile IDK si NO sunt salvate corect
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_idk_and_no_answers_saved(seeded_db):
    """Raspunsurile IDK si NO se salveaza cu valorile corecte."""
    async with seeded_db() as session:
        user = User(telegram_id=100009, username="test_idk", first_name="IDK", language="ro", current_index=1)
        session.add(user)
        await session.commit()
        user_id = user.id

    async with seeded_db() as session:
        questions = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro").order_by(Intrebare.index).limit(3)
        )).scalars().all()

        session.add(Raspuns(user_id=user_id, intrebare_id=questions[0].id, weight="YES"))
        session.add(Raspuns(user_id=user_id, intrebare_id=questions[1].id, weight="NO"))
        session.add(Raspuns(user_id=user_id, intrebare_id=questions[2].id, weight="IDK"))
        await session.commit()

    async with seeded_db() as session:
        answers = (await session.execute(
            select(Raspuns).where(Raspuns.user_id == user_id).order_by(Raspuns.id)
        )).scalars().all()

    assert answers[0].weight == "YES"
    assert answers[1].weight == "NO"
    assert answers[2].weight == "IDK"
