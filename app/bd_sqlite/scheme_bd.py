import asyncio
from bd_sqlite.conexiune import engine
from bd_sqlite.models import Base


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Baza de date a fost creată cu succes")


if __name__ == "__main__":
    asyncio.run(async_main())
