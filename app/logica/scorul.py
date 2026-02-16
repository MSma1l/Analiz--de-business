from sqlalchemy import select, func, update
from bd_sqlite.conexiune import async_session
from bd_sqlite.models import Raspuns, Intrebare, User


async def calculate_score_by_category(user_id: int):
    """
    Calculează scorul pe categorii DOAR pentru răspunsurile YES
    Salvează scorul total în User.score
    Returnează lista de scoruri pe categorii
    """
    async with async_session() as session:

        # Calculează scor pe categorii
        stmt = (
            select(
                Intrebare.categorie,
                func.sum(Intrebare.weight).label("scor")
            )
            .select_from(Raspuns)
            .join(Intrebare, Intrebare.id == Raspuns.intrebare_id)
            .where(
                Raspuns.user_id == user_id,
                Raspuns.weight == "YES"  # ✅ era "True"
            )
            .group_by(Intrebare.categorie)
        )

        result = await session.execute(stmt)
        scoruri_categorii = result.all()

        # Calculează scorul total
        scor_total = sum(scor for _, scor in scoruri_categorii)

        # Salvează scorul în User
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(score=scor_total)
        )
        
        await session.commit()

        return scoruri_categorii