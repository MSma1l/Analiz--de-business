import json
import asyncio

from app.bd_sqlite.conexiune import async_session
from app.bd_sqlite.models import Intrebare


async def load_questions():
    with open("data/Intrebari.json", encoding="utf-8") as f:
        questions = json.load(f)
    print("Gsit intrebarile cu succes")

    async with async_session() as session:
        for q in questions:
            session.add(
                Intrebare(
                    categorie=q["categorie"],
                    text=q["text"],
                    tip=q["tip"],
                    language=q["language"]
                )
            )
        await session.commit()

    print("✅ Întrebările au fost încărcate în baza de date")


if __name__ == "__main__":
    asyncio.run(load_questions())
