import asyncio  # Importa modulul asyncio pentru programare asincrona
from bd_sqlite.conexiune import engine  # Importa motorul bazei de date din modulul de conexiune
from bd_sqlite.modele import Base  # Importa clasa de baza pentru modele care contine metadatele tabelelor


async def async_main():  # Defineste functia asincrona principala pentru crearea tabelelor
    async with engine.begin() as conn:  # Deschide o conexiune asincrona cu tranzactie catre baza de date
        await conn.run_sync(Base.metadata.create_all)  # Creeaza toate tabelele definite in modele daca nu exista deja

    print("✅ Baza de date a fost creată cu succes")  # Afiseaza mesajul de confirmare ca tabelele au fost create


if __name__ == "__main__":  # Verifica daca fisierul este rulat direct (nu importat ca modul)
    asyncio.run(async_main())  # Lanseaza functia asincrona de creare a bazei de date
