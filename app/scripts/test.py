import asyncio
from sqlalchemy import select
from bd_sqlite.conexiune import async_session
from bd_sqlite.models import Intrebare, PragRisc

async def check():
    async with async_session() as session:
        
        r1 = await session.execute(
            select(Intrebare.categorie, Intrebare.language)
            .distinct()
            .order_by(Intrebare.language, Intrebare.categorie)
        )
        print('=== INTREBARI ===')
        for cat, lang in r1.all():
            print(f'[{lang}] {repr(cat)}')
        
        r2 = await session.execute(
            select(PragRisc.categorie, PragRisc.language)
            .distinct()
            .order_by(PragRisc.language, PragRisc.categorie)
        )
        print()
        print('=== PRAGURI ===')
        for cat, lang in r2.all():
            print(f'[{lang}] {repr(cat)}')

asyncio.run(check())