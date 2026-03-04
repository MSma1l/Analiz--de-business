"""
Configurare pytest pentru testele BizCheck Bot.
Creeaza o baza de date SQLite in memorie pentru fiecare test.
"""
import sys
import os
import asyncio
import json
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import event

# Adaugam app/ in sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from bd_sqlite.modele import Base, User, Intrebare, PragRisc, Raspuns, Rezultat


@pytest.fixture(scope="session")
def event_loop():
    """Un singur event loop per sesiune de teste."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_engine():
    """Motor SQLite async in memorie, cu WAL si pragme ca in productie."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"timeout": 30},
    )

    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=-8000")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    """Sesiune async catre BD in memorie."""
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    yield session_factory


@pytest_asyncio.fixture
async def seeded_db(db_session):
    """
    BD populata cu intrebari si praguri de risc din fisierele JSON reale.
    Returneaza session factory-ul.
    """
    base_dir = os.path.join(os.path.dirname(__file__), "..")

    # Incarcam intrebarile
    with open(os.path.join(base_dir, "data", "Intrebari.json"), "r", encoding="utf-8") as f:
        data_q = json.load(f)

    async with db_session() as session:
        for q in data_q["questionnaire"]:
            session.add(Intrebare(
                index=q["index"],
                categorie=q["category"],
                text=q["text"],
                tip="boolean",
                language=q["language"],
                weight=q["weight"],
            ))
        await session.commit()

    # Incarcam pragurile de risc
    with open(os.path.join(base_dir, "data", "risc.json"), "r", encoding="utf-8") as f:
        data_r = json.load(f)

    async with db_session() as session:
        for p in data_r["praguri"]:
            session.add(PragRisc(
                categorie=p["categorie"],
                scor_min=p["scor_min"],
                scor_max=p["scor_max"],
                nivel=p["nivel"],
                language=p.get("language", "ro"),
            ))
        await session.commit()

    yield db_session
