"""
============================================================
SCENARIUL 2: DUBLU-CLICK / RACE CONDITION
============================================================
Testam mecanismul anti-dublu-click si concurenta pe acelasi user.
"""
import asyncio
import pytest
from sqlalchemy import select, func, update
from bd_sqlite.modele import User, Raspuns, Intrebare


async def _create_user(session_factory, telegram_id, language="ro"):
    async with session_factory() as session:
        user = User(telegram_id=telegram_id, username=f"user_{telegram_id}",
                    first_name="Test", language=language, current_index=1)
        session.add(user)
        await session.commit()
        return user.id


async def _simulate_answer(session_factory, user_id, question_id, weight, lock):
    """Simuleaza un raspuns cu protectie anti-dublu-click ca in raspuns.py"""
    if lock.locked():
        return "IGNORED"  # Dublu-click ignorat

    async with lock:
        async with session_factory() as session:
            # Verificam daca raspunsul exista deja
            existing = (await session.execute(
                select(Raspuns).where(
                    Raspuns.user_id == user_id,
                    Raspuns.intrebare_id == question_id
                )
            )).scalar_one_or_none()

            if existing:
                existing.weight = weight
            else:
                session.add(Raspuns(user_id=user_id, intrebare_id=question_id, weight=weight))

            await session.execute(
                update(User).where(User.id == user_id).values(current_index=User.current_index + 1)
            )
            await session.commit()
        return "PROCESSED"


# ----------------------------------------------------------
# TEST 2.1: Dublu-click rapid - al doilea click ignorat
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_double_click_ignored(seeded_db):
    """Doua click-uri simultane pe acelasi buton: doar unul procesat."""
    user_id = await _create_user(seeded_db, telegram_id=200001)

    async with seeded_db() as session:
        q = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro", Intrebare.index == 1)
        )).scalar_one()
        q_id = q.id

    lock = asyncio.Lock()

    # Lansam 2 click-uri simultan
    results = await asyncio.gather(
        _simulate_answer(seeded_db, user_id, q_id, "YES", lock),
        _simulate_answer(seeded_db, user_id, q_id, "YES", lock),
    )

    processed = results.count("PROCESSED")
    ignored = results.count("IGNORED")

    assert processed == 1, f"Doar 1 click trebuie procesat, gasit {processed}"
    assert ignored == 1, f"Al doilea click trebuie ignorat, gasit {ignored}"

    # Verificam un singur raspuns in BD
    async with seeded_db() as session:
        count = (await session.execute(
            select(func.count(Raspuns.id)).where(Raspuns.user_id == user_id)
        )).scalar()
    assert count == 1


# ----------------------------------------------------------
# TEST 2.2: 5 click-uri rapide - doar 1 procesat
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_five_rapid_clicks(seeded_db):
    """5 click-uri simultan pe aceeasi intrebare -> doar 1 raspuns."""
    user_id = await _create_user(seeded_db, telegram_id=200002)

    async with seeded_db() as session:
        q = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro", Intrebare.index == 1)
        )).scalar_one()
        q_id = q.id

    lock = asyncio.Lock()

    results = await asyncio.gather(
        *[_simulate_answer(seeded_db, user_id, q_id, "YES", lock) for _ in range(5)]
    )

    processed = results.count("PROCESSED")
    assert processed == 1, f"Doar 1 click din 5 trebuie procesat, gasit {processed}"


# ----------------------------------------------------------
# TEST 2.3: Lock-uri separate per utilizator
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_separate_locks_per_user(seeded_db):
    """2 utilizatori diferiti pot raspunde simultan fara blocare."""
    user1_id = await _create_user(seeded_db, telegram_id=200003)
    user2_id = await _create_user(seeded_db, telegram_id=200004)

    async with seeded_db() as session:
        q = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro", Intrebare.index == 1)
        )).scalar_one()
        q_id = q.id

    lock1 = asyncio.Lock()
    lock2 = asyncio.Lock()

    results = await asyncio.gather(
        _simulate_answer(seeded_db, user1_id, q_id, "YES", lock1),
        _simulate_answer(seeded_db, user2_id, q_id, "NO", lock2),
    )

    # Ambii trebuie procesati
    assert results.count("PROCESSED") == 2, "Ambii utilizatori trebuie procesati"

    # Verificam raspunsurile
    async with seeded_db() as session:
        a1 = (await session.execute(
            select(Raspuns).where(Raspuns.user_id == user1_id)
        )).scalar_one()
        a2 = (await session.execute(
            select(Raspuns).where(Raspuns.user_id == user2_id)
        )).scalar_one()

    assert a1.weight == "YES"
    assert a2.weight == "NO"


# ----------------------------------------------------------
# TEST 2.4: Raspuns duplicat suprascrie valoarea
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_duplicate_answer_overwrites(seeded_db):
    """Daca un raspuns exista deja, un nou raspuns il suprascrie."""
    user_id = await _create_user(seeded_db, telegram_id=200005)

    async with seeded_db() as session:
        q = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro", Intrebare.index == 1)
        )).scalar_one()
        q_id = q.id

    # Raspundem prima data cu YES
    async with seeded_db() as session:
        session.add(Raspuns(user_id=user_id, intrebare_id=q_id, weight="YES"))
        await session.commit()

    # Simulam suprascrierea (ca in save_answer)
    async with seeded_db() as session:
        existing = (await session.execute(
            select(Raspuns).where(
                Raspuns.user_id == user_id,
                Raspuns.intrebare_id == q_id
            )
        )).scalar_one()
        existing.weight = "NO"
        await session.commit()

    # Verificam ca avem un singur raspuns cu NO
    async with seeded_db() as session:
        answers = (await session.execute(
            select(Raspuns).where(Raspuns.user_id == user_id)
        )).scalars().all()

    assert len(answers) == 1
    assert answers[0].weight == "NO"


# ----------------------------------------------------------
# TEST 2.5: current_index nu se incrementeaza dublu
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_current_index_no_double_increment(seeded_db):
    """Dublu-click nu incrementeaza current_index de doua ori."""
    user_id = await _create_user(seeded_db, telegram_id=200006)

    async with seeded_db() as session:
        q = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro", Intrebare.index == 1)
        )).scalar_one()
        q_id = q.id

    lock = asyncio.Lock()

    await asyncio.gather(
        _simulate_answer(seeded_db, user_id, q_id, "YES", lock),
        _simulate_answer(seeded_db, user_id, q_id, "YES", lock),
    )

    async with seeded_db() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()

    # Trebuie sa fie 2 (1 + 1 incrementare), nu 3
    assert user.current_index == 2, f"current_index ar trebui sa fie 2, gasit {user.current_index}"
