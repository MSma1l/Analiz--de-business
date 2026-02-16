import json
import asyncio
import os

from bd_sqlite.conexiune import async_session
from bd_sqlite.models import Intrebare


async def main():
    # 🔹 Determinăm calea către fișierul JSON
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folderul scripts/
    project_root = os.path.dirname(BASE_DIR)               # folderul app/
    json_path = os.path.join(project_root, "data", "Intrebari.json")

    # 🔹 Citim fișierul JSON
    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
            questions = data["questionnaire"]  # conform structurii tale JSON
    except FileNotFoundError:
        print(f"❌ Fișierul nu a fost găsit: {json_path}")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Eroare la parsarea JSON: {e}")
        return

    print(f"✅ {len(questions)} întrebări au fost citite din JSON")

    # 🔹 Inserăm întrebările în baza de date
    async with async_session() as session:
        for q in questions:
            intrebare = Intrebare(
                index=q.get("index"),
                categorie=q.get("category") or q.get("categorie"),
                text=q.get("text"),
                tip="boolean",
                language=q.get("language"),
                weight=q.get("weight")
            )
            session.add(intrebare)
        await session.commit()

    print("✅ Întrebările au fost încărcate în DB")


if __name__ == "__main__":
    asyncio.run(main())
