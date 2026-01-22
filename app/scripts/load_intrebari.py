import json
import asyncio

from bd_sqlite.conexiune import async_session
from bd_sqlite.models import Intrebare


async def main():
    with open("data/Intrebari.json", encoding="utf-8") as f:
        questions = json.load(f)
        
    print("✅ Întrebările au fost citite")
    
    async with async_session() as session:
        for q in questions:
            session.add(
                Intrebare(
                    index=q["index"],   # CHEIA LOGICĂ
                    categorie=q["categorie"],
                    text=q["text"],
                    tip="boolean",
                    language=q["language"]
                )
            )
        await session.commit()

    print("✅ Întrebările au fost încărcate în DB")


if __name__ == "__main__":
    asyncio.run(main())
