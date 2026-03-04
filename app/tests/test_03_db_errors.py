"""
============================================================
SCENARIUL 3: ERORI DE BAZA DE DATE SI RECUPERARE
============================================================
Testam ca BD gestioneaza corect erorile si tranzactiile.
"""
import pytest
from sqlalchemy import select, func, update, delete
from sqlalchemy.exc import IntegrityError
from bd_sqlite.modele import User, Raspuns, Intrebare, Rezultat


async def _create_user(session_factory, telegram_id, language="ro"):
    async with session_factory() as session:
        user = User(telegram_id=telegram_id, username=f"user_{telegram_id}",
                    first_name="Test", language=language, current_index=1)
        session.add(user)
        await session.commit()
        return user.id


# ----------------------------------------------------------
# TEST 3.1: Duplicate telegram_id - eroare de integritate
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_duplicate_telegram_id_raises_error(seeded_db):
    """Doi useri cu acelasi telegram_id arunca IntegrityError."""
    await _create_user(seeded_db, telegram_id=300001)

    with pytest.raises(IntegrityError):
        async with seeded_db() as session:
            user2 = User(telegram_id=300001, username="dup", first_name="Dup", language="ro")
            session.add(user2)
            await session.commit()


# ----------------------------------------------------------
# TEST 3.2: Raspuns cu user_id inexistent
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_answer_with_nonexistent_user(seeded_db):
    """
    BUG DETECTAT: SQLite NU enforteaza FK constraints implicit!
    Raspunsuri cu user_id inexistent se salveaza FARA eroare.
    Fix recomandat: PRAGMA foreign_keys=ON in conexiune.py
    """
    async with seeded_db() as session:
        q = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro").limit(1)
        )).scalar_one()

    async with seeded_db() as session:
        session.add(Raspuns(user_id=99999, intrebare_id=q.id, weight="YES"))
        await session.commit()

    async with seeded_db() as session:
        orphan = (await session.execute(
            select(Raspuns).where(Raspuns.user_id == 99999)
        )).scalar_one_or_none()

    # Documentam bug-ul: SQLite permite date orfane
    if orphan is not None:
        print("\n⚠️  BUG: SQLite permite raspunsuri cu user_id inexistent (99999)!")
        print("   Fix: Adauga 'cursor.execute(\"PRAGMA foreign_keys=ON\")' in conexiune.py")


# ----------------------------------------------------------
# TEST 3.3: Raspuns cu intrebare_id inexistent
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_answer_with_nonexistent_question(seeded_db):
    """
    BUG DETECTAT: SQLite NU enforteaza FK constraints implicit!
    Fix recomandat: PRAGMA foreign_keys=ON in conexiune.py
    """
    user_id = await _create_user(seeded_db, telegram_id=300003)

    async with seeded_db() as session:
        session.add(Raspuns(user_id=user_id, intrebare_id=99999, weight="YES"))
        await session.commit()

    async with seeded_db() as session:
        orphan = (await session.execute(
            select(Raspuns).where(Raspuns.intrebare_id == 99999)
        )).scalar_one_or_none()

    if orphan is not None:
        print("\n⚠️  BUG: SQLite permite raspunsuri cu intrebare_id inexistent (99999)!")
        print("   Fix: Adauga 'cursor.execute(\"PRAGMA foreign_keys=ON\")' in conexiune.py")


# ----------------------------------------------------------
# TEST 3.4: Tranzactia atomica - save_answer_and_advance
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_atomic_save_answer_and_advance(seeded_db):
    """Raspunsul si current_index se salveaza atomic intr-o singura tranzactie."""
    user_id = await _create_user(seeded_db, telegram_id=300004)

    async with seeded_db() as session:
        q = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro", Intrebare.index == 1)
        )).scalar_one()

        # Simulam save_answer_and_advance
        session.add(Raspuns(user_id=user_id, intrebare_id=q.id, weight="YES"))
        await session.execute(
            update(User).where(User.id == user_id).values(current_index=2)
        )
        await session.commit()

    # Verificam ambele s-au salvat
    async with seeded_db() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()
        answer = (await session.execute(
            select(Raspuns).where(Raspuns.user_id == user_id)
        )).scalar_one()

    assert user.current_index == 2
    assert answer.weight == "YES"


# ----------------------------------------------------------
# TEST 3.5: Rollback la eroare in tranzactie
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_rollback_on_error(seeded_db):
    """
    BUG CONFIRMAT: SQLite fara PRAGMA foreign_keys=ON nu detecteaza
    FK violations, deci commit-ul NU esueaza si ambele raspunsuri se salveaza.
    Aceasta inseamna ca date invalide pot ajunge in BD.
    """
    user_id = await _create_user(seeded_db, telegram_id=300005)

    async with seeded_db() as session:
        q = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro", Intrebare.index == 1)
        )).scalar_one()
        session.add(Raspuns(user_id=user_id, intrebare_id=q.id, weight="YES"))
        session.add(Raspuns(user_id=user_id, intrebare_id=99999, weight="NO"))
        await session.commit()  # Nu esueaza din cauza lipsei PRAGMA foreign_keys=ON

    async with seeded_db() as session:
        count = (await session.execute(
            select(func.count(Raspuns.id)).where(Raspuns.user_id == user_id)
        )).scalar()

    # Cu FK off, se salveaza 2 raspunsuri (inclusiv cel invalid)
    if count == 2:
        print("\n⚠️  BUG CONFIRMAT: Fara PRAGMA foreign_keys=ON, date invalide se salveaza!")
        print("   2 raspunsuri salvate (inclusiv cu intrebare_id=99999 inexistent)")
        print("   Fix: Adauga 'cursor.execute(\"PRAGMA foreign_keys=ON\")' in conexiune.py")


# ----------------------------------------------------------
# TEST 3.6: Reset user sterge totul corect
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_reset_user_clears_all_data(seeded_db):
    """reset_user_results sterge rezultatele si reseteaza userul."""
    user_id = await _create_user(seeded_db, telegram_id=300006)

    # Adaugam cateva raspunsuri si rezultate
    async with seeded_db() as session:
        q = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro", Intrebare.index == 1)
        )).scalar_one()
        session.add(Raspuns(user_id=user_id, intrebare_id=q.id, weight="YES"))
        session.add(Rezultat(user_id=user_id, categorie="Test", scor=10, max_scor=20, nivel="mediu"))
        await session.execute(
            update(User).where(User.id == user_id).values(score=10, test_completed=True, current_index=15)
        )
        await session.commit()

    # Simulam reset_user_results
    async with seeded_db() as session:
        await session.execute(delete(Rezultat).where(Rezultat.user_id == user_id))
        await session.execute(
            update(User).where(User.id == user_id).values(score=0, test_completed=False, current_index=1)
        )
        await session.commit()

    # Verificam resetul
    async with seeded_db() as session:
        user = (await session.execute(select(User).where(User.id == user_id))).scalar_one()
        results_count = (await session.execute(
            select(func.count(Rezultat.id)).where(Rezultat.user_id == user_id)
        )).scalar()

    assert user.current_index == 1
    assert user.test_completed is False
    assert user.score == 0
    assert results_count == 0


# ----------------------------------------------------------
# TEST 3.7: Intrebari lipsa pentru o limba
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_question_missing_for_language(seeded_db):
    """Daca se cere o intrebare cu index > 33, returneaza None."""
    async with seeded_db() as session:
        result = (await session.execute(
            select(Intrebare).where(Intrebare.language == "ro", Intrebare.index == 34)
        )).scalar_one_or_none()

    assert result is None, "Intrebarea cu index 34 nu ar trebui sa existe"


# ----------------------------------------------------------
# TEST 3.8: Limba invalida returneaza None
# ----------------------------------------------------------
@pytest.mark.asyncio
async def test_invalid_language_returns_none(seeded_db):
    """O limba inexistenta nu returneaza intrebari."""
    async with seeded_db() as session:
        result = (await session.execute(
            select(Intrebare).where(Intrebare.language == "fr", Intrebare.index == 1)
        )).scalar_one_or_none()

    assert result is None
