from sqlalchemy import select, update
from bd_sqlite.conexiune import async_session
from bd_sqlite.models import User, Intrebare, Raspuns, Rezultat

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

        try:
            await session.commit()
        except Exception:
            await session.rollback()
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one()

        return user


async def set_user_language(telegram_id: int, language: str):
    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.telegram_id == telegram_id)
            .values(language=language)
        )
        await session.commit()

async def get_user_by_telegram_id(telegram_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

async def get_question_by_index(index: int, language: str):
    async with async_session() as session:
        result = await session.execute(
            select(Intrebare)
            .where(Intrebare.language == language)
            .offset(index)
            .limit(1)
        )
        return result.scalar_one_or_none()

async def save_answer(user_id: int, intrebare_id: int, valoare: str):
    async with async_session() as session:
        result = await session.execute(
            select(Raspuns).where(
                Raspuns.user_id == user_id,
                Raspuns.intrebare_id == intrebare_id
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.valoare = valoare
        else:
            session.add(
                Raspuns(
                    user_id=user_id,
                    intrebare_id=intrebare_id,
                    valoare=valoare
                )
            )

        await session.commit()


async def save_result(user_id: int, scor: int, nivel: str):
    async with async_session() as session:
        rezultat = Rezultat(
            user_id=user_id,
            scor=scor,
            nivel=nivel
        )
        session.add(rezultat)
        await session.commit()
