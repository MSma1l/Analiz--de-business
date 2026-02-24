import io
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.platypus import (
    Table, TableStyle, Paragraph, Spacer,
    Image, SimpleDocTemplate, HRFlowable, PageBreak
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfMerger

from bd_sqlite.fuction_bd import get_user_results

# ==================== FONTURI ====================
FONT_PATH      = "pdf/assets/DejaVuSans.ttf"
FONT_BOLD_PATH = "pdf/assets/DejaVuSans-Bold.ttf"
pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))
try:
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", FONT_BOLD_PATH))
except Exception:
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", FONT_PATH))

# ==================== PALETA ====================
C_BLUE_DARK   = "#1A3A5C"
C_BLUE_MID    = "#1E6FA8"
C_BLUE_LIGHT  = "#D6E8F7"
C_ORANGE      = "#F59E0B"
C_GREEN       = "#2E7D5E"
C_RED         = "#C0392B"
C_GRAY_LIGHT  = "#EEF2F7"
C_GRAY_TEXT   = "#4A5568"
C_WHITE       = "#FFFFFF"
C_SEPARATOR   = "#B8D0E8"

PAGE_W  = A4[0]
MAIN_W  = PAGE_W * 0.80
MARGIN  = (PAGE_W - MAIN_W) / 2


# ==================== UTIL PDF ====================

def append_existing_pdf(generated_pdf: str, extra_pdf: str, output_pdf: str):
    
    merger = PdfMerger()
    merger.append(extra_pdf)
    merger.append(generated_pdf)
    merger.write(output_pdf)
    merger.close()


def draw_background(canvas, doc):
    if os.path.exists("pdf/assets/bg.jpg"):
        canvas.drawImage("pdf/assets/bg.jpg", 0, 0, width=A4[0], height=A4[1])


def draw_chart_background(canvas, doc):
    if os.path.exists("pdf/assets/bg_charts.jpg"):
        canvas.drawImage("pdf/assets/bg_charts.jpg", 0, 0, width=A4[0], height=A4[1])
    elif os.path.exists("pdf/assets/bg.jpg"):
        canvas.drawImage("pdf/assets/bg.jpg", 0, 0, width=A4[0], height=A4[1])


# ==================== HELPERS ====================

def _color_for_nivel(nivel: str, language: str) -> str:
    n = nivel.lower()
    if language == "ro":
        if "ridicat" in n or "înalt" in n:
            return C_RED
        elif "mediu" in n:
            return C_ORANGE
        return C_GREEN
    else:
        if "высокий" in n:
            return C_RED
        elif "средний" in n:
            return C_ORANGE
        return C_GREEN


def _short_title(categorie: str, max_len: int = 150) -> str:
    titlu = categorie.split(". ", 1)[1] if ". " in categorie else categorie
    return titlu if len(titlu) <= max_len else titlu[:max_len - 1] + "…"


def _nivel_label(nivel: str, language: str) -> str:
    n = nivel.lower()
    if language == "ro":
        if "ridicat" in n or "înalt" in n:
            return "Ridicat"
        elif "mediu" in n:
            return "Mediu"
        return "Minim"
    else:
        if "высокий" in n:
            return "Высокий"
        elif "средний" in n:
            return "Средний"
        return "Минимальный"


def _worst_nivel(niveluri: list, language: str) -> str:
    for n in niveluri:
        nl = n.lower()
        if language == "ro":
            if "ridicat" in nl or "înalt" in nl:
                return n
        else:
            if "высокий" in nl:
                return n
    for n in niveluri:
        nl = n.lower()
        if language == "ro":
            if "mediu" in nl:
                return n
        else:
            if "средний" in nl:
                return n
    return niveluri[0] if niveluri else ""


# ==================== COMPONENTE LAYOUT ====================

def _header_block(titlu_doc: str, subtitlu_doc: str) -> Table:
    title_style = ParagraphStyle(
        "HdrTitle",
        fontName="DejaVu-Bold",
        fontSize=20,
        textColor=colors.HexColor(C_WHITE),
        alignment=1,
        leading=28,
        spaceAfter=5,
    )
    sub_style = ParagraphStyle(
        "HdrSub",
        fontName="DejaVu",
        fontSize=10,
        textColor=colors.HexColor(C_ORANGE),
        alignment=1,
        leading=15,
    )
    cell = [
        Spacer(1, 0.4 * cm),
        Paragraph(titlu_doc, title_style),
        Spacer(1, 0.12 * cm),
        Paragraph(subtitlu_doc, sub_style),
        Spacer(1, 0.4 * cm),
    ]
    tbl = Table([[cell]], colWidths=[MAIN_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(C_BLUE_DARK)),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 20),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return tbl


def _section_bar(text: str) -> Table:
    style = ParagraphStyle(
        "SecBar",
        fontName="DejaVu-Bold",
        fontSize=12,
        textColor=colors.HexColor(C_WHITE),
        alignment=0,
        leading=16,
    )
    tbl = Table([[Paragraph(text, style)]], colWidths=[MAIN_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(C_BLUE_MID)),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
        ("TOPPADDING",    (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return tbl


# ==================== GRAFICE ====================

def generate_chart_bytes(scor: int, max_scor: int, nivel: str,
                         categorie: str, language: str) -> io.BytesIO:
    buf     = io.BytesIO()
    procent = int((scor / max_scor) * 100) if max_scor > 0 else 0
    color   = _color_for_nivel(nivel, language)
    titlu   = _short_title(categorie)
    label   = _nivel_label(nivel, language)

    fig, ax = plt.subplots(figsize=(2.6, 2.6), facecolor="none")

    ax.pie(
        [procent, 100 - procent],
        startangle=90,
        colors=[color, C_GRAY_LIGHT],
        wedgeprops={"width": 0.26, "edgecolor": C_WHITE, "linewidth": 1.8},
        counterclock=False
    )

    ax.text(0,  0.10, f"{procent}%",
            ha="center", va="center",
            fontsize=14, fontweight="bold",
            color=C_BLUE_DARK, fontfamily="DejaVu Sans")

    ax.text(0, -0.22, label,
            ha="center", va="center",
            fontsize=10, fontweight="bold",
            color=color, fontfamily="DejaVu Sans")

    ax.set_aspect("equal")

    fig.text(0.5, 0.01, titlu,
             ha="center", va="bottom",
             fontsize=7.7, fontweight="bold",
             color=C_BLUE_DARK, fontfamily="DejaVu Sans")

    plt.tight_layout(pad=0.2)
    plt.savefig(buf, format="PNG", bbox_inches="tight",
                transparent=True, dpi=130)
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_general_risk_chart_bytes(raport: list, language: str) -> io.BytesIO:
    """Donut mare — procent mediu real (fara mesaj motivational, doar procentul)."""
    buf = io.BytesIO()

    procente = [
        int((scor / max_scor) * 100)
        for _, scor, max_scor, _ in raport if max_scor > 0
    ]
    procent_mediu = int(sum(procente) / len(procente)) if procente else 0

    niveluri  = [nivel for _, _, _, nivel in raport]
    worst     = _worst_nivel(niveluri, language)
    color     = _color_for_nivel(worst, language)

    if language == "ro":
        nivel_text = (
            "Risc Ridicat" if color == C_RED else
            "Risc Mediu"   if color == C_ORANGE else
            "Risc Minim"
        )
    else:
        nivel_text = (
            "Высокий риск"     if color == C_RED else
            "Средний риск"     if color == C_ORANGE else
            "Минимальный риск"
        )

    fig, ax = plt.subplots(figsize=(4.0, 4.0), facecolor="none")

    ax.pie(
        [procent_mediu, 100 - procent_mediu],
        startangle=90,
        colors=[color, C_GRAY_LIGHT],
        wedgeprops={"width": 0.30, "edgecolor": C_WHITE, "linewidth": 2.5},
        counterclock=False
    )
# general donuts
    ax.text(0,  0.14, f"{procent_mediu}%",
            ha="center", va="center",
            fontsize=26, fontweight="bold",
            color=C_BLUE_DARK, fontfamily="DejaVu Sans")


    ax.text(0, -0.20, nivel_text,
            ha="center", va="center",
            fontsize=10, fontweight="bold",
            color=color, fontfamily="DejaVu Sans")

    ax.set_aspect("equal")

    plt.tight_layout(pad=0.5)
    plt.savefig(buf, format="PNG", bbox_inches="tight",
                transparent=True, dpi=140)
    plt.close(fig)
    buf.seek(0)
    return buf


def _build_variants_block(procent_mediu: int, language: str) -> list:
    elements = []

    is_ro = language == "ro"

    label_style = ParagraphStyle(
        "VarLabel",
        fontName="DejaVu-Bold",
        fontSize=10,
        textColor=colors.HexColor(C_BLUE_MID),
        leading=15,
        spaceAfter=4,
    )
    text_style = ParagraphStyle(
        "VarText",
        fontName="DejaVu-Bold",
        fontSize=12,
        textColor=colors.HexColor(C_BLUE_DARK),
        leading=18,
        spaceAfter=0,
        leftIndent=10,
    )
    note_style = ParagraphStyle(
        "VarNote",
        fontName="DejaVu",
        fontSize=8,
        textColor=colors.HexColor(C_GRAY_TEXT),
        leading=12,
        alignment=1,
    )

    if is_ro:
        nota    = "* Aceasta este o evaluare preliminară — nu reprezintă rezultatul final."
        variants = [
            {
                "label": "Varianta 1",
                "text":  f"Ați atins {procent_mediu}% din vârful ideal de performanță.",
                "bg":    C_BLUE_LIGHT,
            },
            {
                "label": "Varianta 2",
                "text":  f"Sunteți la {procent_mediu}% distanță de afacerea perfectă.",
                "bg":    C_GRAY_LIGHT,
            },
            {
                "label": "Varianta 3",
                "text":  f"Performanța actuală: {procent_mediu}% din nivelul ideal.",
                "bg":    C_BLUE_LIGHT,
            },
        ]
    else:
        nota    = "* Это предварительная оценка — не является окончательным результатом."
        variants = [
            {
                "label": "Вариант 1",
                "text":  f"Вы достигли {procent_mediu}% от идеального пика эффективности.",
                "bg":    C_BLUE_LIGHT,
            },
            {
                "label": "Вариант 2",
                "text":  f"Вы на {procent_mediu}% пути к идеальному бизнесу.",
                "bg":    C_GRAY_LIGHT,
            },
            {
                "label": "Вариант 3",
                "text":  f"Текущий результат: {procent_mediu}% от идеального уровня.",
                "bg":    C_BLUE_LIGHT,
            },
        ]

    elements.append(Spacer(1, 0.3 * cm))

    for v in variants:
        cell_content = [
            Spacer(1, 0.18 * cm),
            Paragraph(v["label"], label_style),
            Paragraph(v["text"], text_style),
            Spacer(1, 0.18 * cm),
        ]
        row_tbl = Table([[cell_content]], colWidths=[MAIN_W])
        row_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(v["bg"])),
            ("LEFTPADDING",   (0, 0), (-1, -1), 16),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        elements.append(row_tbl)
        elements.append(Spacer(1, 0.18 * cm))

    elements.append(Spacer(1, 0.2 * cm))

    nota_tbl = Table(
        [[Paragraph(nota, note_style)]],
        colWidths=[MAIN_W]
    )
    nota_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(C_WHITE)),
        ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor(C_SEPARATOR)),
    ]))
    elements.append(nota_tbl)

    return elements


# ==================== GENERARE PDF ====================

async def generate_pdf(user_id: int, language: str, filename="raport.pdf"):

    if language == "ro":
        titlu_doc     = "Raport de Evaluare a Riscului"
        subtitlu_doc  = "Analiză detaliată pe categorii · BizzCheck"
        titlu_sectie  = "  Evaluare pe categorii"
        titlu_general = "  Scor General"
        bloc_prefix   = "Bloc"
    else:
        titlu_doc     = "Отчёт об оценке рисков"
        subtitlu_doc  = "Детальный анализ по категориям · BizzCheck"
        titlu_sectie  = "  Оценка по категориям"
        titlu_general = "  Общий результат"
        bloc_prefix   = "Блок"

    # ---- Style for the block label shown above each donut chart ----
    bloc_label_style = ParagraphStyle(
        "BlocLabel",
        fontName="DejaVu-Bold",
        fontSize=10,
        textColor=colors.HexColor(C_BLUE_DARK),
        alignment=1,      # centered
        leading=14,
        spaceAfter=2,
    )

    elements = []
    elements.append(Spacer(1, 0.5 * cm))

    elements.append(_header_block(titlu_doc, subtitlu_doc))
    elements.append(Spacer(1, 0.6 * cm))

    results_dict = await get_user_results(user_id)

    if not results_dict:
        no_data_style = ParagraphStyle(
            "ND", fontName="DejaVu", fontSize=10,
            textColor=colors.HexColor(C_BLUE_DARK)
        )
        no_data = "Nu există rezultate disponibile." if language == "ro" else "Нет доступных результатов."
        elements.append(Paragraph(no_data, no_data_style))
    else:
        raport = [
            (cat, d["scor"], d["max_scor"], d["nivel"])
            for cat, d in results_dict.items()
        ]

        elements.append(_section_bar(titlu_sectie))
        elements.append(Spacer(1, 0.45 * cm))

        IMG_SIZE = 5.0 * cm
        COLS     = 3
        COL_W    = MAIN_W / COLS

        # ---- Build chart cells with block label above each donut ----
        chart_data = []
        row = []
        for idx, (cat, scor, max_scor, nivel) in enumerate(raport, start=1):
            buf = generate_chart_bytes(scor, max_scor, nivel, cat, language)

            # Each cell is a list of flowables: label + image
            bloc_label_text = f"{bloc_prefix} {idx}"
            cell_content = [
                Paragraph(bloc_label_text, bloc_label_style),
                Spacer(1, 0.1 * cm),
                Image(buf, width=IMG_SIZE, height=IMG_SIZE),
            ]

            row.append(cell_content)
            if len(row) == COLS:
                chart_data.append(row)
                row = []

        if row:
            while len(row) < COLS:
                row.append(Spacer(COL_W, IMG_SIZE))
            chart_data.append(row)

        if chart_data:
            row_styles = []
            for i in range(len(chart_data)):
                bg = C_BLUE_LIGHT if i % 2 == 0 else C_WHITE
                row_styles.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor(bg)))

            tbl = Table(chart_data, colWidths=[COL_W] * COLS)
            tbl.setStyle(TableStyle([
                ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING",    (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING",   (0, 0), (-1, -1), 2),
                ("RIGHTPADDING",  (0, 0), (-1, -1), 2),
                *row_styles,
            ]))
            elements.append(tbl)

        elements.append(PageBreak())
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(_header_block(titlu_doc, subtitlu_doc))
        elements.append(Spacer(1, 0.6 * cm))
        elements.append(_section_bar(titlu_general))
        elements.append(Spacer(1, 0.35 * cm))

        procente_all = [
            int((scor / max_scor) * 100)
            for _, scor, max_scor, _ in raport if max_scor > 0
        ]
        procent_mediu = int(sum(procente_all) / len(procente_all)) if procente_all else 0

        general_buf = generate_general_risk_chart_bytes(raport, language)
        general_img = Image(general_buf, width=8.5 * cm, height=8.5 * cm)

        general_tbl = Table([[general_img]], colWidths=[MAIN_W])
        general_tbl.setStyle(TableStyle([
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(C_WHITE)),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(general_tbl)
        elements.append(Spacer(1, 0.3 * cm))

        for el in _build_variants_block(procent_mediu, language):
            elements.append(el)

        elements.append(Spacer(1, 0.5 * cm))

        grupe_risc = {"minim": [], "mediu": [], "ridicat": []}
        for cat, scor, max_scor, nivel in raport:
            n = nivel.lower()
            if language == "ro":
                if "ridicat" in n or "înalt" in n:
                    grupe_risc["ridicat"].append((cat, scor, max_scor, nivel))
                elif "mediu" in n:
                    grupe_risc["mediu"].append((cat, scor, max_scor, nivel))
                else:
                    grupe_risc["minim"].append((cat, scor, max_scor, nivel))
            else:
                if "высокий" in n:
                    grupe_risc["ridicat"].append((cat, scor, max_scor, nivel))
                elif "средний" in n:
                    grupe_risc["mediu"].append((cat, scor, max_scor, nivel))
                else:
                    grupe_risc["minim"].append((cat, scor, max_scor, nivel))

        config_risc = {
            "minim": {
                "color": C_GRAY_LIGHT,
                "ro": {
                    "emoji": "",
                    "titlu": "Performanță înaltă",
                    "mesaj_fn": lambda p: f"Ați atins {p}% din vârful ideal de performanță.",
                    "sub": "Aceste domenii funcționează excelent. Menții direcția!",
                    "nivel_display": "Risc Minim",
                },
                "ru": {
                    "emoji": "",
                    "titlu": "Высокая эффективность",
                    "mesaj_fn": lambda p: f"Вы достигли {p}% от идеального пика эффективности.",
                    "sub": "Эти направления работают отлично. Сохраняйте курс!",
                    "nivel_display": "Минимальный риск",
                },
            },
            "mediu": {
                "color": C_GRAY_LIGHT,
                "ro": {
                    "emoji": "",
                    "titlu": "În dezvoltare",
                    "mesaj_fn": lambda p: f"Sunteți la {p}% distanță de afacerea perfectă.",
                    "sub": "Există oportunități clare de îmbunătățire. Acționați acum!",
                    "nivel_display": "Risc Mediu",
                },
                "ru": {
                    "emoji": "",
                    "titlu": "В развитии",
                    "mesaj_fn": lambda p: f"Вы на {p}% пути к идеальному бизнесу.",
                    "sub": "Есть чёткие возможности для улучшения. Действуйте сейчас!",
                    "nivel_display": "Средний риск",
                },
            },
            "ridicat": {
                "color": C_GRAY_LIGHT,
                "ro": {
                    "emoji": "",
                    "titlu": "Necesită atenție urgentă",
                    "mesaj_fn": lambda p: f"Performanța actuală: {p}% din nivelul ideal.",
                    "sub": "Aceste domenii necesită intervenție imediată!",
                    "nivel_display": "Risc Ridicat",
                },
                "ru": {
                    "emoji": "",
                    "titlu": "Требует срочного внимания",
                    "mesaj_fn": lambda p: f"Текущий результат: {p}% от идеального уровня.",
                    "sub": "Эти направления требуют немедленного вмешательства!",
                    "nivel_display": "Высокий риск",
                },
            },
        }

        card_titlu_style = ParagraphStyle(
            "CardTitlu", fontName="DejaVu-Bold", fontSize=16,
            textColor=colors.HexColor(C_WHITE), leading=22,
            alignment=0, spaceAfter=8,
        )
        card_mesaj_style = ParagraphStyle(
            "CardMesaj", fontName="DejaVu-Bold", fontSize=15,
            textColor=colors.HexColor(C_WHITE), leading=22,
            alignment=0, spaceAfter=8,
        )
        card_sub_style = ParagraphStyle(
            "CardSub", fontName="DejaVu-Bold", fontSize=12,
            textColor=colors.HexColor(C_WHITE), leading=18,
            alignment=0,
        )
        cat_style = ParagraphStyle(
            "CatStyle", fontName="DejaVu-Bold", fontSize=11,
            textColor=colors.HexColor(C_WHITE), leading=16,
            alignment=0,
        )

        for nivel_key in ["ridicat", "mediu", "minim"]:
            categorii_nivel = grupe_risc[nivel_key]
            if not categorii_nivel:
                continue

            cfg      = config_risc[nivel_key]
            lang_cfg = cfg[language]

            procente_nivel = [
                int((scor / max_scor) * 100)
                for _, scor, max_scor, _ in categorii_nivel if max_scor > 0
            ]
            procent_nivel = int(sum(procente_nivel) / len(procente_nivel)) if procente_nivel else 0

            if procent_nivel >= 70:
                color = C_GREEN
                nivel_display = "Risc Minim" if language == "ro" else "Минимальный риск"
                mesaj_text = (f"Ati atins {procent_nivel}% din varful ideal de performanta."
                              if language == "ro" else
                              f"Вы достигли {procent_nivel}% от идеального пика ефф.")
            elif procent_nivel >= 40:
                color = C_ORANGE
                nivel_display = "Risc Mediu" if language == "ro" else "Средний риск"
                mesaj_text = (f"Sunteti la {procent_nivel}% distanta de afacerea perfecta."
                              if language == "ro" else
                              f"Вы на {procent_nivel}% пути к идеальному бизнесу.")
            else:
                color = C_RED
                nivel_display = "Risc Ridicat" if language == "ro" else "Высокий риск"
                mesaj_text = (f"Performanta actuala: {procent_nivel}% din nivelul ideal."
                              if language == "ro" else
                              f"Текущий результат : {procent_nivel}% от идеального уровня.")

            elements.append(PageBreak())
            elements.append(Spacer(1, 0.5 * cm))
            elements.append(_header_block(titlu_doc, subtitlu_doc))
            elements.append(Spacer(1, 0.45 * cm))
            elements.append(_section_bar(f"{lang_cfg['emoji']}  {lang_cfg['titlu']}"))
            elements.append(Spacer(1, 0.4 * cm))

            buf_nivel = io.BytesIO()
            fig, ax = plt.subplots(figsize=(3.6, 3.6), facecolor="none")
            ax.pie(
                [procent_nivel, 100 - procent_nivel],
                startangle=90,
                colors=[color, C_GRAY_LIGHT],
                wedgeprops={"width": 0.30, "edgecolor": C_WHITE, "linewidth": 2.5},
                counterclock=False
            )
            ax.text(0,  0.14, f"{procent_nivel}%",
                    ha="center", va="center",
                    fontsize=24, fontweight="bold",
                    color=C_GRAY_LIGHT, fontfamily="DejaVu Sans")
            ax.text(0, -0.20, nivel_display,
                    ha="center", va="center",
                    fontsize=9, fontweight="bold",
                    color=C_GRAY_LIGHT,
                    fontfamily="DejaVu Sans")
            ax.set_aspect("equal")
            plt.tight_layout(pad=0.4)
            plt.savefig(buf_nivel, format="PNG", bbox_inches="tight",
                        transparent=True, dpi=140)
            plt.close(fig)
            buf_nivel.seek(0)

            donut_img = Image(buf_nivel, width=7.0 * cm, height=7.0 * cm)

            lista_cat = [Spacer(1, 0.5 * cm)]
            lista_cat.append(Paragraph(mesaj_text, card_mesaj_style))
            lista_cat.append(Spacer(1, 0.2 * cm))
            lista_cat.append(Paragraph(lang_cfg["sub"], card_sub_style))
            lista_cat.append(Spacer(1, 0.3 * cm))

            for cat, _, _, _ in categorii_nivel:
                titlu_cat = _short_title(cat, max_len=150)
                lista_cat.append(Paragraph(f"• {titlu_cat}", cat_style))
            lista_cat.append(Spacer(1, 0.5 * cm))

            LEFT_W  = MAIN_W * 0.40
            RIGHT_W = MAIN_W * 0.60

            layout_tbl = Table([[donut_img, lista_cat]], colWidths=[LEFT_W, RIGHT_W])
            layout_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(color)),
                ("ALIGN",         (0, 0), (0, 0),   "CENTER"),
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN",         (1, 0), (1, 0),   "LEFT"),
                ("LEFTPADDING",   (0, 0), (0, 0),   10),
                ("RIGHTPADDING",  (0, 0), (0, 0),   10),
                ("LEFTPADDING",   (1, 0), (1, 0),   18),
                ("RIGHTPADDING",  (1, 0), (1, 0),   16),
                ("TOPPADDING",    (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]))
            elements.append(layout_tbl)
            elements.append(Spacer(1, 0.4 * cm))

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=1.0 * cm,
        bottomMargin=1.0 * cm
    )
    doc.build(
        elements,
        onFirstPage=draw_chart_background,
        onLaterPages=draw_chart_background
    )
    return filename


# ==================== BUILD RAPORT FINAL ====================

async def build_user_report(user_id: int, language: str):
    temp_pdf   = await generate_pdf(user_id, language, filename="temp_report.pdf")
    design_pdf = f"pdf/assets/pdf{'ro' if language == 'ro' else 'ru'}.pdf"
    final_pdf  = "BIZCHECK_RAPORT.pdf"
    append_existing_pdf(temp_pdf, design_pdf, final_pdf)
    return final_pdf