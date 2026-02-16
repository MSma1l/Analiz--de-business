import os
import json
import asyncio
from bd_sqlite.conexiune import async_session
from bd_sqlite.models import PragRisc

async def main():
    # Cale absolută către fișierul JSON
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /app
    json_path = os.path.join(BASE_DIR, "data", "risc.json")

    if not os.path.exists(json_path):
        print(f"❌ EROARE: Fișierul {json_path} nu există!")
        return

    # citire JSON
    with open(json_path, encoding="utf-8-sig") as f:  # UTF-8 BOM safe
        full_data = json.load(f)

    # verificăm dacă există cheia "praguri"
    if "praguri" not in full_data:
        print("❌ EROARE: JSON trebuie să conțină cheia 'praguri'")
        return

    data = full_data["praguri"]  # extragem lista de obiecte

    print(f"✅ {len(data)} praguri de risc au fost citite")

    # salvare în baza de date
    async with async_session() as session:
        for r in data:
                session.add(PragRisc(
                    categorie=r.get("categorie"),
                    scor_min=r.get("scor_min"),
                    scor_max=r.get("scor_max"),
                    nivel=r.get("nivel"),
                    language=r.get("language")
                ))

        await session.commit()

    print("✅ Pragurile de risc au fost încărcate în DB")

if __name__ == "__main__":
    asyncio.run(main())
