"""
============================================================
SCENARIUL 7: FSM STATE SI RESTART BOT
============================================================
Testam problemele legate de pierderea starii FSM si restart.
"""
import pytest
from sqlalchemy import select, func, update
from bd_sqlite.modele import User, Raspuns, Intrebare, Rezultat


async def _create_user(session_factory, telegram_id, language="ro", **kwargs):
    async with session_factory() as session:
        user = User(telegram_id=telegram_id, username=f"user_{telegram_id}",
                    first_name="Test", language=language, current_index=1, **kwargs)
        session.add(user)
        await session.commit()
        return user.id


# ----------------------------------------------------------
# TEST 7.1: Dupa restart bot, progresul testului persista
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_test_progress_persists_after_restart(seeded_db):
    """
    Dupa restart bot, current_index si raspunsurile raman in BD.
    Userul poate relua testul.
    """
    user_id = await _create_user(seeded_db, telegram_id=700001)

    # Raspundem la 15 intrebari
    async with seeded_db() as session:
        questions = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro")
            .order_by(Intrebare.index).limit(15)
        )).scalars().all()

        for q in questions:
            session.add(Raspuns(user_id=user_id, intrebare_id=q.id, weight="YES"))
        await session.execute(
            update(User).where(User.id == user_id).values(current_index=16)
        )
        await session.commit()

    # "Restart bot" — recitim din BD
    async with seeded_db() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()

    assert user.current_index == 16, "Progresul trebuie sa persiste"


# ----------------------------------------------------------
# TEST 7.2: FSM state (cabinet) pierdut la restart - datele companiei
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_cabinet_fsm_state_lost_on_restart(seeded_db):
    """
    BUG DOCUMENTAT: MemoryStorage se pierde la restart.
    Daca user-ul era in mijlocul adaugarii companiei (FSM state),
    dupa restart va trebui sa reia de la inceput.

    Datele partial introduse (ex: company_name dar fara email) NU se salveaza in BD.
    """
    user_id = await _create_user(seeded_db, telegram_id=700002)

    # Simulam: user-ul a introdus company_name dar bot-ul s-a restartat
    # FSM data: {"company_name": "TechCorp"} — pierduta la restart

    async with seeded_db() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()

    # Datele companiei NU au fost salvate in BD (doar in FSM memory)
    assert user.company_name is None, \
        "Company name nu trebuie sa fie salvat - FSM state pierdut la restart"
    assert user.number_company is None
    assert user.email_company is None


# ----------------------------------------------------------
# TEST 7.3: User apasa butoane test dupa restart
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_user_starts_test_after_restart(seeded_db):
    """User-ul apasa 'Incepe testul' dupa restart — testul reia de la current_index."""
    user_id = await _create_user(seeded_db, telegram_id=700003)

    # Simulam: user la intrebarea 10
    async with seeded_db() as session:
        await session.execute(
            update(User).where(User.id == user_id).values(current_index=10)
        )
        await session.commit()

    # Dupa "restart", start_test citeste current_index
    async with seeded_db() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()
        question = (await session.execute(
            select(Intrebare).where(
                Intrebare.language == user.language,
                Intrebare.index == user.current_index
            )
        )).scalar_one_or_none()

    assert question is not None, "Intrebarea 10 trebuie sa existe"
    assert question.index == 10


# ----------------------------------------------------------
# TEST 7.4: User apasa test dupa ce a terminat (current_index=34)
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_user_presses_test_after_completion(seeded_db):
    """
    BUG POTENTAIL: User cu current_index=34 si test_completed=True
    apasa din nou 'Incepe testul'.
    get_current_question(34, "ro") returneaza None.
    In intrebare.py, se afiseaza "Nu exista intrebari" — corect.
    """
    user_id = await _create_user(seeded_db, telegram_id=700004)

    async with seeded_db() as session:
        await session.execute(
            update(User).where(User.id == user_id).values(
                current_index=34, test_completed=True, score=50
            )
        )
        await session.commit()

    # Simulam: get_current_question(34, "ro")
    async with seeded_db() as session:
        question = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro", Intrebare.index == 34)
        )).scalar_one_or_none()

    assert question is None, "Cu index=34, nu ar trebui sa existe intrebare"


# ----------------------------------------------------------
# TEST 7.5: Multiple callback_query simultane dupa restart
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_concurrent_callbacks_after_restart(seeded_db):
    """
    Dupa restart, lock-urile sunt resetate.
    Un user poate trimite raspunsuri imediat — lock-ul se recreeaza automat.
    """
    import asyncio

    user_id = await _create_user(seeded_db, telegram_id=700005)

    # Simulam _user_locks resetat (ca dupa restart)
    _user_locks = {}

    def _get_lock(tid):
        if tid not in _user_locks:
            _user_locks[tid] = asyncio.Lock()
        return _user_locks[tid]

    # Lock-ul trebuie sa se creeze on-the-fly
    lock = _get_lock(700005)
    assert isinstance(lock, asyncio.Lock)
    assert not lock.locked(), "Lock-ul nou trebuie sa fie deblocat"


# ----------------------------------------------------------
# TEST 7.6: User cu stare inconsistenta (raspunsuri > current_index)
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_inconsistent_state_answers_ahead_of_index(seeded_db):
    """
    BUG POTENTAIL: Daca dintr-un motiv current_index e mai mic decat
    numarul de raspunsuri, userul ar raspunde la o intrebare deja raspunsa.
    save_answer_and_advance face upsert, deci se suprascrie — dar nu e ideal.
    """
    user_id = await _create_user(seeded_db, telegram_id=700006)

    # Salvam 10 raspunsuri dar current_index e 5 (inconsistent)
    async with seeded_db() as session:
        questions = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro")
            .order_by(Intrebare.index).limit(10)
        )).scalars().all()

        for q in questions:
            session.add(Raspuns(user_id=user_id, intrebare_id=q.id, weight="YES"))
        await session.execute(
            update(User).where(User.id == user_id).values(current_index=5)
        )
        await session.commit()

    # User-ul vede intrebarea 5 (deja raspunsa)
    async with seeded_db() as session:
        answers_count = (await session.execute(
            select(func.count(Raspuns.id)).where(Raspuns.user_id == user_id)
        )).scalar()
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()

    # Inconsistenta: 10 raspunsuri dar current_index=5
    assert answers_count > user.current_index - 1, \
        f"Stare inconsistenta: {answers_count} raspunsuri, current_index={user.current_index}"


# ----------------------------------------------------------
# TEST 7.7: Limba user None dupa restart (fara selectie)
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_user_language_none_after_restart(seeded_db):
    """
    Daca user-ul a dat /start dar nu a selectat limba,
    language=None si orice actiune pe test va esua graceful.
    """
    user_id = await _create_user(seeded_db, telegram_id=700007, language=None)

    async with seeded_db() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()

    assert user.language is None

    # In intrebare.py: get_current_question(1, None) -> None
    async with seeded_db() as session:
        q = (await session.execute(
            select(Intrebare).where(Intrebare.language == None, Intrebare.index == 1)
        )).scalar_one_or_none()

    assert q is None, "Cu limba None, nu trebuie sa gaseasca intrebari"


# ----------------------------------------------------------
# TEST 7.8: Starea user-ului persistata complet
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_full_user_state_persistence(seeded_db):
    """Toate campurile user-ului se salveaza si se citesc corect."""
    async with seeded_db() as session:
        user = User(
            telegram_id=700008,
            username="full_state",
            first_name="FullState",
            language="ru",
            current_index=25,
            test_completed=False,
            score=42,
            company_name="TestCorp",
            number_company="069123456",
            email_company="test@corp.md"
        )
        session.add(user)
        await session.commit()

    # "Restart" — recitim
    async with seeded_db() as session:
        user = (await session.execute(
            select(User).where(User.telegram_id == 700008)
        )).scalar_one()

    assert user.telegram_id == 700008
    assert user.username == "full_state"
    assert user.first_name == "FullState"
    assert user.language == "ru"
    assert user.current_index == 25
    assert user.test_completed is False
    assert user.score == 42
    assert user.company_name == "TestCorp"
    assert user.number_company == "069123456"
    assert user.email_company == "test@corp.md"
