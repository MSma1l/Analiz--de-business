"""
Test de incarcare: 20 utilizatori simultani parcurg testul complet.
Simuleaza: creare user → selectie limba → raspuns la 33 intrebari → finalizare → generare PDF.
Ruleaza din folderul app/: python -m scripts.test_incarcare
"""

import asyncio  # Importam modulul asyncio pentru programare asincrona
import time  # Importam modulul time pentru masurarea timpului de executie
import random  # Importam modulul random pentru generarea valorilor aleatoare
import os  # Importam modulul os pentru lucrul cu caile de fisiere
import sys  # Importam modulul sys pentru manipularea caii de cautare a modulelor

# Adaugam directorul app/ in sys.path pentru a putea importa modulele proiectului
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bd_sqlite.schema_bd import async_main  # Importam functia de creare a tabelelor in baza de date
from bd_sqlite.functii_bd import (  # Importam functiile de lucru cu baza de date
    get_or_create_user,  # Functia pentru crearea sau obtinerea unui utilizator
    set_user_language,  # Functia pentru setarea limbii si resetarea testului
    save_answer_and_advance,  # Functia pentru salvarea raspunsului si avansarea indexului
    get_current_question,  # Functia pentru obtinerea intrebarii curente
)
from bot.gestionari.raport import finalize_test  # Importam functia de finalizare a testului
from raport_pdf import build_user_report  # Importam functia de generare a raportului PDF

# ==================== CONFIGURARE TEST ====================
NUM_USERS = 20  # Numarul de utilizatori simulati
TOTAL_INTREBARI = 33  # Numarul total de intrebari din test
RASPUNSURI_POSIBILE = ["YES", "NO", "IDK"]  # Lista raspunsurilor posibile


async def simulate_user(user_num: int) -> dict:  # Functie care simuleaza un utilizator complet
    """Simuleaza un utilizator care parcurge testul complet."""
    telegram_id = 9000000 + user_num  # Generam un telegram_id unic pentru fiecare utilizator simulat
    username = f"test_user_{user_num}"  # Generam un username unic
    first_name = f"Test{user_num}"  # Generam un prenume unic
    result = {  # Initializam dictionarul cu rezultatele simularii
        "user_num": user_num,  # Numarul utilizatorului
        "success": False,  # Statusul de succes (implicit fals)
        "error": None,  # Mesajul de eroare (implicit gol)
        "time": 0,  # Timpul de executie (implicit 0)
        "time_test": 0,  # Timpul doar pentru parcurgerea testului (fara PDF)
        "time_pdf": 0,  # Timpul doar pentru generarea PDF-ului
        "answers": 0,  # Numarul de raspunsuri date
        "pdf": False,  # Daca PDF-ul a fost generat cu succes
    }

    start = time.time()  # Marcam timpul de start al simularii

    try:
        # 1. Creare utilizator
        user = await get_or_create_user(telegram_id, username, first_name)  # Cream sau obtinem utilizatorul
        user_id = user.id  # Salvam ID-ul utilizatorului

        # 2. Selectie limba (reseteaza testul)
        await set_user_language(telegram_id, "ro")  # Setam limba romana si resetam testul

        # 3. Raspundem la toate cele 33 de intrebari
        for idx in range(1, TOTAL_INTREBARI + 1):  # Iteram prin fiecare intrebare (1 pana la 33)
            question = await get_current_question(idx, "ro")  # Obtinem intrebarea curenta
            if not question:  # Daca intrebarea nu exista
                result["error"] = f"Intrebarea {idx} nu exista"  # Setam mesajul de eroare
                result["time"] = time.time() - start  # Calculam timpul de executie
                return result  # Returnam rezultatul cu eroare

            raspuns = random.choice(RASPUNSURI_POSIBILE)  # Alegem un raspuns aleatoriu
            await save_answer_and_advance(user_id, question.id, raspuns, idx + 1)  # Salvam raspunsul si avansam indexul intr-o singura tranzactie

            result["answers"] += 1  # Incrementam contorul de raspunsuri

        # 4. Finalizare test (calcul scoruri + salvare rezultate)
        raport, language = await finalize_test(user_id)  # Finalizam testul si obtinem raportul
        result["time_test"] = time.time() - start  # Salvam timpul parcurgerii testului (fara PDF)

        # 5. Generare PDF
        pdf_start = time.time()  # Marcam timpul de start al generarii PDF-ului
        pdf_path = await build_user_report(user_id, "ro", username=username, first_name=first_name)  # Generam raportul PDF cu datele utilizatorului
        result["time_pdf"] = time.time() - pdf_start  # Salvam timpul generarii PDF-ului
        if os.path.exists(pdf_path):  # Verificam daca fisierul PDF a fost creat
            result["pdf"] = True  # Marcam PDF-ul ca generat cu succes

        result["success"] = True  # Marcam simularea ca reusita

    except Exception as e:  # Prindem orice exceptie aparuta in timpul simularii
        result["error"] = str(e)  # Salvam mesajul de eroare

    result["time"] = time.time() - start  # Calculam timpul total de executie
    return result  # Returnam rezultatul simularii


async def main():  # Functia principala a testului de incarcare
    print("=" * 60)  # Afisam linie separatoare
    print(f"  TEST DE INCARCARE: {NUM_USERS} utilizatori simultani")  # Afisam titlul testului
    print("=" * 60)  # Afisam linie separatoare

    # Cream tabelele in baza de date daca nu exista
    await async_main()  # Initializam baza de date

    # Verificam ca intrebarile sunt incarcate
    q = await get_current_question(1, "ro")  # Verificam daca exista prima intrebare in romana
    if not q:  # Daca intrebarile nu sunt incarcate
        print("EROARE: Intrebarile nu sunt incarcate in BD!")  # Afisam mesaj de eroare
        print("Ruleaza mai intai: python -m scripts.incarcare_intrebari")  # Instructiuni pentru incarcare
        return  # Iesim din functie

    print(f"\nLansam {NUM_USERS} utilizatori simultan...\n")  # Afisam mesajul de start

    start_total = time.time()  # Marcam timpul de start total

    # Lansam toti utilizatorii simultan
    tasks = [simulate_user(i) for i in range(1, NUM_USERS + 1)]  # Cream taskurile pentru toti utilizatorii
    results = await asyncio.gather(*tasks, return_exceptions=True)  # Executam toate taskurile simultan

    total_time = time.time() - start_total  # Calculam timpul total de executie

    # ==================== RAPORT REZULTATE ====================
    print("\n" + "=" * 60)  # Afisam linie separatoare
    print("  REZULTATE")  # Afisam titlul sectiunii de rezultate
    print("=" * 60)  # Afisam linie separatoare

    succese = 0  # Contor pentru simulari reusite
    erori = 0  # Contor pentru simulari esuate
    pdf_ok = 0  # Contor pentru PDF-uri generate cu succes
    timpi = []  # Lista cu timpii de executie individuali

    for r in results:  # Iteram prin fiecare rezultat
        if isinstance(r, Exception):  # Daca rezultatul este o exceptie
            erori += 1  # Incrementam contorul de erori
            print(f"  [EXCEPTIE] {r}")  # Afisam exceptia
            continue  # Trecem la urmatorul rezultat

        status = "OK" if r["success"] else "EROARE"  # Determinam statusul simularii
        pdf_status = "PDF OK" if r["pdf"] else "PDF -"  # Determinam statusul PDF-ului
        print(f"  User {r['user_num']:2d} | {status:6s} | {r['answers']:2d} rasp | test:{r['time_test']:.1f}s | pdf:{r['time_pdf']:.1f}s | total:{r['time']:.1f}s"  # Afisam detaliile cu timpi separati
              + (f" | {r['error']}" if r["error"] else ""))  # Adaugam mesajul de eroare daca exista

        if r["success"]:  # Daca simularea a fost reusita
            succese += 1  # Incrementam contorul de succese
        else:  # Daca simularea a esuat
            erori += 1  # Incrementam contorul de erori
        if r["pdf"]:  # Daca PDF-ul a fost generat
            pdf_ok += 1  # Incrementam contorul de PDF-uri
        timpi.append(r["time"])  # Adaugam timpul de executie la lista

    print("\n" + "-" * 60)  # Afisam linie separatoare
    print(f"  Total:    {NUM_USERS} utilizatori")  # Afisam numarul total de utilizatori
    print(f"  Succese:  {succese}/{NUM_USERS}")  # Afisam numarul de succese
    print(f"  Erori:    {erori}/{NUM_USERS}")  # Afisam numarul de erori
    print(f"  PDF OK:   {pdf_ok}/{NUM_USERS}")  # Afisam numarul de PDF-uri generate
    if timpi:  # Daca avem timpi de executie
        print(f"  Timp min: {min(timpi):.2f}s")  # Afisam timpul minim
        print(f"  Timp max: {max(timpi):.2f}s")  # Afisam timpul maxim
        print(f"  Timp med: {sum(timpi)/len(timpi):.2f}s")  # Afisam timpul mediu
    print(f"  Timp total: {total_time:.2f}s")  # Afisam timpul total al testului
    print("=" * 60)  # Afisam linie separatoare finala

    # Verdict final
    if succese == NUM_USERS:  # Daca toate simularile au fost reusite
        print("\n  VERDICT: BOTUL REZISTA LA 20 UTILIZATORI SIMULTANI!")  # Afisam mesajul de succes
    else:  # Daca exista erori
        print(f"\n  VERDICT: {erori} ERORI — necesita investigare!")  # Afisam mesajul de eroare


if __name__ == "__main__":  # Verificam daca scriptul este executat direct
    asyncio.run(main())  # Rulam functia principala asincrona
