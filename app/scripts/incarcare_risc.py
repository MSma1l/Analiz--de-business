import os  # Importam modulul os pentru lucrul cu caile de fisiere si directoare
import json  # Importam modulul json pentru citirea si parsarea fisierelor JSON
import asyncio  # Importam modulul asyncio pentru executarea functiilor asincrone
from bd_sqlite.conexiune import async_session  # Importam sesiunea asincrona pentru conectarea la baza de date
from bd_sqlite.modele import PragRisc  # Importam modelul PragRisc care reprezinta structura tabelului de praguri de risc

async def main():  # Definim functia principala asincrona
    # Cale absoluta catre fisierul JSON
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Obtinem calea directorului app/ (doua nivele sus din scripts/)
    json_path = os.path.join(BASE_DIR, "data", "risc.json")  # Construim calea completa catre fisierul JSON cu pragurile de risc

    if not os.path.exists(json_path):  # Verificam daca fisierul JSON exista pe disc
        print(f"❌ EROARE: Fișierul {json_path} nu există!")  # Afisam mesaj de eroare daca fisierul lipseste
        return  # Iesim din functie

    # Citire JSON
    with open(json_path, encoding="utf-8-sig") as f:  # Deschidem fisierul cu codificarea UTF-8 BOM safe (suporta BOM la inceputul fisierului)
        full_data = json.load(f)  # Parsam continutul JSON intr-un dictionar Python

    # Verificam daca exista cheia "praguri"
    if "praguri" not in full_data:  # Daca dictionarul JSON nu contine cheia "praguri"
        print("❌ EROARE: JSON trebuie să conțină cheia 'praguri'")  # Afisam mesaj de eroare despre structura invalida
        return  # Iesim din functie

    data = full_data["praguri"]  # Extragem lista de obiecte cu praguri de risc din cheia "praguri"

    print(f"✅ {len(data)} praguri de risc au fost citite")  # Afisam numarul de praguri de risc citite cu succes

    # Salvare in baza de date
    async with async_session() as session:  # Deschidem o sesiune asincrona cu baza de date
        for r in data:  # Iteram prin fiecare prag de risc din lista
                session.add(PragRisc(  # Cream si adaugam un obiect PragRisc la sesiunea bazei de date
                    categorie=r.get("categorie"),  # Setam categoria pragului de risc
                    scor_min=r.get("scor_min"),  # Setam scorul minim al intervalului
                    scor_max=r.get("scor_max"),  # Setam scorul maxim al intervalului
                    nivel=r.get("nivel"),  # Setam nivelul de risc (ex: minim, mediu, ridicat)
                    language=r.get("language")  # Setam limba pragului de risc
                ))

        await session.commit()  # Salvam (comitem) toate pragurile de risc in baza de date

    print("✅ Pragurile de risc au fost încărcate în DB")  # Afisam mesaj de confirmare a incarcarii cu succes

if __name__ == "__main__":  # Verificam daca scriptul este executat direct (nu importat ca modul)
    asyncio.run(main())  # Rulam functia principala asincrona
