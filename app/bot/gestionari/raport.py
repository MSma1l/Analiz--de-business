from bd_sqlite.fuction_bd import (
    get_max_score_by_category,
    calculate_score_by_category,
    get_nivel_risc,
    save_results_to_db,
)
from bd_sqlite.conexiune import async_session
from bd_sqlite.models import User
from sqlalchemy import select, update


# =====================================================
# FINALIZARE TEST
# =====================================================

async def finalize_test(user_id: int):
    """
    1. Calculează scor pe categorii
    2. Determină risc din interval
    3. Salvează rezultate în BD (inclusiv max_scor)
    4. Marchează test ca finalizat
    5. Returnează (raport, language)
    """

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one()
        language = user.language or "ro"

    max_scores = await get_max_score_by_category(language)

    scoruri_categorii = await calculate_score_by_category(user_id, language)

    raport = []
    for categorie, scor in scoruri_categorii:
        nivel = await get_nivel_risc(categorie, scor, language)
        raport.append((categorie, scor, nivel))

    await save_results_to_db(user_id, raport, max_scores)

    scor_total = sum(scor for _, scor, _ in raport)

    async with async_session() as session:
        await session.execute(
            update(User)
            .where(User.id == user_id)
            .values(score=scor_total, test_completed=True)
        )
        await session.commit()

    return raport, language


# =====================================================
# RAPORT TEXT TELEGRAM
# =====================================================

def format_report(raport, language="ro"):
    """
    Formatează raportul pentru afișare în Telegram.
    Grupează blocurile pe niveluri de risc cu recomandări.
    """

    if language == "ro":
        titlu = "📊 *Rezultat final:*"
        texte_risc = {
            "minim":   "Riscuri minime - recomandăm verificare anuală",
            "mediu":   "Risc Mediu - consultați când apar probleme",
            "ridicat": "Risc Ridicat - trebuie verificat urgent"
        }
        text_final = "\n📄 Raportul PDF detaliat te așteaptă în meniu."
    else:  # ru
        titlu = "📊 *Итоговый результат:*"
        texte_risc = {
            "minim":   "Риски минимальные - рекомендуем проверять раз в год",
            "mediu":   "Средний Риск - обратитесь когда будут проблемы",
            "ridicat": "Высокий Риск проблем - требуется срочная проверка"
        }
        text_final = "\n📄 Детальный PDF отчет ждёт вас в меню."

    emoji_map = {
        "minim":   "🟢",
        "mediu":   "🟡",
        "ridicat": "🔴"
    }

    # =====================================================
    # GRUPARE BLOCURI PE NIVEL
    # =====================================================
    grupe = {"minim": [], "mediu": [], "ridicat": []}

    for item in raport:
        if len(item) == 4:
            categorie, scor, max_scor, nivel = item
        else:
            categorie, scor, nivel = item

        nivel_lower = nivel.lower()
        if language == "ro":
            if "ridicat" in nivel_lower or "înalt" in nivel_lower:
                grupe["ridicat"].append(categorie)
            elif "mediu" in nivel_lower:
                grupe["mediu"].append(categorie)
            else:
                grupe["minim"].append(categorie)
        else:  # ru
            if "высокий" in nivel_lower:
                grupe["ridicat"].append(categorie)
            elif "средний" in nivel_lower:
                grupe["mediu"].append(categorie)
            else:
                grupe["minim"].append(categorie)

    # =====================================================
    # CONSTRUIRE TEXT FINAL
    # =====================================================
    text = f"{titlu}\n\n"

    for cheie in ["ridicat", "mediu", "minim"]:
        blocuri = grupe[cheie]
        if not blocuri:
            continue

        emoji = emoji_map[cheie]
        label = texte_risc[cheie]

        text += f"{emoji} {label}\n"
        for bloc in blocuri:
            text += f"    └ {bloc}\n"
        text += "\n"

    text += text_final
    return text