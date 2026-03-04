import json  # Importam modulul json pentru citirea si parsarea fisierelor JSON
import asyncio  # Importam modulul asyncio pentru executarea functiilor asincrone
import os  # Importam modulul os pentru lucrul cu caile de fisiere si directoare

from bd_sqlite.conexiune import async_session  # Importam sesiunea asincrona pentru conectarea la baza de date
from bd_sqlite.modele import Intrebare  # Importam modelul Intrebare care reprezinta structura tabelului din baza de date


async def main():  # Definim functia principala asincrona
    # Determinam calea catre fisierul JSON
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Obtinem calea absoluta a directorului curent (folderul scripts/)
    project_root = os.path.dirname(BASE_DIR)               # Obtinem calea directorului parinte (folderul app/)
    json_path = os.path.join(project_root, "data", "Intrebari.json")  # Construim calea completa catre fisierul JSON cu intrebari

    # Citim fisierul JSON
    try:  # Incercam sa deschidem si sa parsam fisierul JSON
        with open(json_path, encoding="utf-8") as f:  # Deschidem fisierul cu codificarea UTF-8
            data = json.load(f)  # Parsam continutul JSON intr-un dictionar Python
            questions = data["questionnaire"]  # Extragem lista de intrebari din cheia "questionnaire"
    except FileNotFoundError:  # Daca fisierul nu a fost gasit pe disc
        print(f"❌ Fișierul nu a fost găsit: {json_path}")  # Afisam mesaj de eroare cu calea fisierului lipsa
        return  # Iesim din functie
    except json.JSONDecodeError as e:  # Daca fisierul JSON are o structura invalida
        print(f"❌ Eroare la parsarea JSON: {e}")  # Afisam mesajul de eroare al parsarii
        return  # Iesim din functie

    print(f"✅ {len(questions)} întrebări au fost citite din JSON")  # Afisam numarul de intrebari citite cu succes

    # Inseram intrebarile in baza de date
    async with async_session() as session:  # Deschidem o sesiune asincrona cu baza de date
        for q in questions:  # Iteram prin fiecare intrebare din lista
            intrebare = Intrebare(  # Cream un obiect Intrebare cu datele din JSON
                index=q.get("index"),  # Setam indexul intrebarii
                categorie=q.get("category") or q.get("categorie"),  # Setam categoria (acceptam ambele chei: "category" sau "categorie")
                text=q.get("text"),  # Setam textul intrebarii
                tip="boolean",  # Setam tipul intrebarii ca "boolean" (da/nu)
                language=q.get("language"),  # Setam limba intrebarii
                weight=q.get("weight")  # Setam ponderea (greutatea) intrebarii
            )
            session.add(intrebare)  # Adaugam obiectul Intrebare la sesiunea bazei de date
        await session.commit()  # Salvam (comitem) toate intrebarile in baza de date

    print("✅ Întrebările au fost încărcate în DB")  # Afisam mesaj de confirmare a incarcarii cu succes


if __name__ == "__main__":  # Verificam daca scriptul este executat direct (nu importat ca modul)
    asyncio.run(main())  # Rulam functia principala asincrona
