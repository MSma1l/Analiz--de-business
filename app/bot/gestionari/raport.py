import asyncio  # Importam asyncio pentru retry logic cu sleep la concurenta SQLite
from bd_sqlite.functii_bd import (  # Importam functiile necesare din modulul de lucru cu baza de date
    get_max_score_by_category,  # Functia care obtine scorul maxim posibil pentru fiecare categorie
    calculate_score_by_category,  # Functia care calculeaza scorul utilizatorului pe fiecare categorie
    get_nivel_risc,  # Functia care determina nivelul de risc pe baza scorului
    save_results_to_db,  # Functia care salveaza rezultatele finale in baza de date
    get_questions_per_category,  # Functia care returneaza numarul de intrebari pe fiecare categorie
    MAX_RETRIES, RETRY_BASE_DELAY,  # Constantele pentru retry logic
)
from bd_sqlite.conexiune import async_session  # Importam sesiunea asincrona pentru conectarea la baza de date
from bd_sqlite.modele import User  # Importam modelul User care reprezinta tabelul utilizatorilor
from sqlalchemy import select, update  # Importam functiile select si update din SQLAlchemy pentru interogari SQL
from sqlalchemy.exc import OperationalError  # Importam OperationalError pentru retry logic la BD blocat


# =====================================================
# FINALIZARE TEST
# =====================================================

async def finalize_test(user_id: int):  # Functia asincrona care finalizeaza testul pentru un utilizator dat
    """
    1. Calculează scor pe categorii
    2. Determină risc din interval
    3. Adaugă categoriile cu scor 0 (fără niciun YES) în raport
    4. Salvează rezultate în BD (inclusiv max_scor)
    5. Marchează test ca finalizat
    6. Returnează (raport, language)
    """

    async with async_session() as session:  # Deschidem o sesiune asincrona cu baza de date
        result = await session.execute(  # Executam o interogare SQL de selectare
            select(User).where(User.id == user_id)  # Selectam utilizatorul cu ID-ul specificat
        )
        user = result.scalar_one()  # Extragem exact un singur rezultat (obiectul User)
        language = user.language or "ro"  # Obtinem limba utilizatorului sau folosim romana ca limba implicita

    max_scores = await get_max_score_by_category(language)  # Obtinem scorurile maxime posibile pentru fiecare categorie in limba utilizatorului

    scoruri_categorii = await calculate_score_by_category(user_id, language)  # Calculam scorurile utilizatorului pentru fiecare categorie

    # Construim un set cu categoriile care au cel putin un raspuns YES
    categorii_cu_scor = {categorie for categorie, _ in scoruri_categorii}

    raport = []  # Initializam o lista goala care va contine raportul final
    for categorie, scor in scoruri_categorii:  # Iteram prin fiecare categorie si scorul corespunzator
        nivel = await get_nivel_risc(categorie, scor, language)  # Determinam nivelul de risc pe baza categoriei si scorului
        raport.append((categorie, scor, nivel))  # Adaugam in raport un tuplu cu categoria, scorul si nivelul de risc

    # FIX BUG 3: Adaugam categoriile care au scor 0 (toate raspunsurile NO/IDK) — altfel lipsesc din raport si PDF
    for categorie in max_scores:  # Iteram prin toate categoriile existente
        if categorie not in categorii_cu_scor:  # Daca categoria nu a aparut in scorurile calculate (0 raspunsuri YES)
            nivel = await get_nivel_risc(categorie, 0, language)  # Determinam nivelul de risc pentru scor 0
            raport.append((categorie, 0, nivel))  # Adaugam categoria cu scor 0 in raport

    await save_results_to_db(user_id, raport, max_scores)  # Salvam rezultatele raportului in baza de date impreuna cu scorurile maxime

    scor_total = sum(scor for _, scor, _ in raport)  # Calculam scorul total insumand scorurile tuturor categoriilor

    # Retry logic pentru marcarea testului ca finalizat — previne pierderea starii la concurenta mare
    for attempt in range(MAX_RETRIES):
        try:
            async with async_session() as session:  # Deschidem o noua sesiune asincrona cu baza de date
                await session.execute(  # Executam o comanda SQL de actualizare
                    update(User)  # Cream o comanda de update pentru tabelul User
                    .where(User.id == user_id)  # Filtram dupa ID-ul utilizatorului
                    .values(score=scor_total, test_completed=True)  # Setam scorul total si marcam testul ca finalizat
                )
                await session.commit()  # Confirmam modificarile in baza de date
            break  # Tranzactia a reusit, iesim din bucla
        except OperationalError:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_BASE_DELAY * (attempt + 1))  # Asteptam cu backoff inainte de reincercare
            else:
                raise  # Dupa MAX_RETRIES incercari, aruncam eroarea

    return raport, language  # Returnam raportul cu rezultatele si limba utilizatorului


# =====================================================
# RAPORT TEXT TELEGRAM
# =====================================================

def format_report(raport, language="ro"):  # Functia care formateaza raportul pentru afisarea in Telegram
    """
    Formatează raportul pentru afișare în Telegram.
    Grupează blocurile pe niveluri de risc cu recomandări.
    """

    if language == "ro":  # Daca limba utilizatorului este romana
        titlu = "📊 *Rezultat final:*"  # Setam titlul raportului in romana
        texte_risc = {  # Definim textele descriptive pentru fiecare nivel de risc in romana
            "minim":   "Riscuri minime - recomandăm verificare anuală",  # Textul pentru risc minim
            "mediu":   "Risc Mediu - consultați când apar probleme",  # Textul pentru risc mediu
            "ridicat": "Risc Ridicat - trebuie verificat urgent"  # Textul pentru risc ridicat
        }
        text_final = "\n📄 Raportul PDF detaliat te așteaptă în meniu."  # Mesajul final care indica disponibilitatea raportului PDF
    else:  # ru  # Daca limba utilizatorului este rusa
        titlu = "📊 *Итоговый результат:*"  # Setam titlul raportului in rusa
        texte_risc = {  # Definim textele descriptive pentru fiecare nivel de risc in rusa
            "minim":   "Риски минимальные - рекомендуем проверять раз в год",  # Textul pentru risc minim in rusa
            "mediu":   "Средний Риск - обратитесь когда будут проблемы",  # Textul pentru risc mediu in rusa
            "ridicat": "Высокий Риск проблем - требуется срочная проверка"  # Textul pentru risc ridicat in rusa
        }
        text_final = "\n📄 Детальный PDF отчет ждёт вас в меню."  # Mesajul final in rusa care indica disponibilitatea raportului PDF

    emoji_map = {  # Dictionar care asociaza fiecarui nivel de risc un emoji colorat
        "minim":   "🟢",  # Cerculet verde pentru risc minim
        "mediu":   "🟡",  # Cerculet galben pentru risc mediu
        "ridicat": "🔴"  # Cerculet rosu pentru risc ridicat
    }

    # =====================================================
    # GRUPARE BLOCURI PE NIVEL
    # =====================================================
    grupe = {"minim": [], "mediu": [], "ridicat": []}  # Initializam un dictionar cu liste goale pentru fiecare nivel de risc

    for item in raport:  # Iteram prin fiecare element al raportului
        if len(item) == 4:  # Daca elementul are 4 componente (categorie, scor, scor_maxim, nivel)
            categorie, scor, max_scor, nivel = item  # Despachetam cele 4 valori
        else:  # Daca elementul are 3 componente (categorie, scor, nivel)
            categorie, scor, nivel = item  # Despachetam cele 3 valori

        nivel_lower = nivel.lower()  # Convertim nivelul de risc la litere mici pentru comparare uniforma
        if language == "ro":  # Daca limba este romana, verificam nivelul in romana
            if "ridicat" in nivel_lower or "înalt" in nivel_lower:  # Daca nivelul contine "ridicat" sau "inalt"
                grupe["ridicat"].append(categorie)  # Adaugam categoria in grupa de risc ridicat
            elif "mediu" in nivel_lower:  # Daca nivelul contine "mediu"
                grupe["mediu"].append(categorie)  # Adaugam categoria in grupa de risc mediu
            else:  # In orice alt caz
                grupe["minim"].append(categorie)  # Adaugam categoria in grupa de risc minim
        else:  # ru  # Daca limba este rusa, verificam nivelul in rusa
            if "высокий" in nivel_lower:  # Daca nivelul contine "vysokii" (ridicat in rusa)
                grupe["ridicat"].append(categorie)  # Adaugam categoria in grupa de risc ridicat
            elif "средний" in nivel_lower:  # Daca nivelul contine "srednii" (mediu in rusa)
                grupe["mediu"].append(categorie)  # Adaugam categoria in grupa de risc mediu
            else:  # In orice alt caz
                grupe["minim"].append(categorie)  # Adaugam categoria in grupa de risc minim

    # =====================================================
    # CONSTRUIRE TEXT FINAL
    # =====================================================
    text = f"{titlu}\n\n"  # Initializam textul raportului cu titlul si doua randuri noi

    for cheie in ["ridicat", "mediu", "minim"]:  # Iteram prin nivelurile de risc in ordinea gravitatii (de la ridicat la minim)
        blocuri = grupe[cheie]  # Obtinem lista de categorii pentru nivelul curent de risc
        if not blocuri:  # Daca nu exista categorii pentru acest nivel de risc
            continue  # Sarim la urmatorul nivel de risc

        emoji = emoji_map[cheie]  # Obtinem emoji-ul corespunzator nivelului de risc
        label = texte_risc[cheie]  # Obtinem textul descriptiv pentru nivelul de risc

        text += f"{emoji} {label}\n"  # Adaugam linia cu emoji-ul si descrierea nivelului de risc
        for bloc in blocuri:  # Iteram prin categoriile din acest nivel de risc
            text += f"    └ {bloc}\n"  # Adaugam fiecare categorie cu indentare si simbol de ramificatie
        text += "\n"  # Adaugam un rand gol dupa fiecare grup de nivel de risc

    text += text_final  # Adaugam mesajul final despre disponibilitatea raportului PDF
    return text  # Returnam textul complet al raportului formatat
