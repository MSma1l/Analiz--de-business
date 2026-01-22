from sqlalchemy import select, func
from bd_sqlite.conexiune import async_session
from bd_sqlite.models import Raspuns


async def calculate_score(user_id: int) -> int:
    async with async_session() as session:
        # total răspunsuri
        total_stmt = select(func.count()).where(Raspuns.user_id == user_id)
        total = await session.scalar(total_stmt)

        if total == 0:
            return 0

        # răspunsuri DA
        positive_stmt = select(func.count()).where(
            Raspuns.user_id == user_id,
            Raspuns.valoare == True
        )
        positive = await session.scalar(positive_stmt)

    return int((positive / total) * 100)
