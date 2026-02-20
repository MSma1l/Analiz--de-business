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
C_BLUE_DARK   = "#1A3A5C"   # albastru închis  → header, titluri
C_BLUE_MID    = "#1E6FA8"   # albastru mediu   → bare secțiuni
C_BLUE_LIGHT  = "#D6E8F7"   # albastru pal     → rânduri alternate
C_ORANGE      = "#F59E0B"   # galben-orange    → subtitlu header, risc mediu
C_GREEN       = "#2E7D5E"   # verde smarald    → risc minim
C_RED         = "#C0392B"   # roșu sobru       → risc ridicat
C_GRAY_LIGHT  = "#EEF2F7"   # gri albăstrui    → arc background donut
C_GRAY_TEXT   = "#4A5568"   # gri              → text secundar, mesaj italic
C_WHITE       = "#FFFFFF"
C_SEPARATOR   = "#B8D0E8"   # albastru pal     → linie separator

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


def _short_title(categorie: str, max_len: int = 26) -> str:
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
    """Header cu fundal albastru închis, titlu alb, subtitlu galben-orange."""
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
    """Bară de secțiune albastru mediu, text alb."""
    style = ParagraphStyle(
        "SecBar",
        fontName="DejaVu-Bold",
        fontSize=11,
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
    """Donut compact per categorie."""
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
            fontsize=13, fontweight="bold",
            color=C_BLUE_DARK, fontfamily="DejaVu Sans")

    ax.text(0, -0.22, label,
            ha="center", va="center",
            fontsize=6.5, fontweight="bold",
            color=color, fontfamily="DejaVu Sans")

    ax.set_aspect("equal")

    fig.text(0.5, 0.01, titlu,
             ha="center", va="bottom",
             fontsize=7, fontweight="bold",
             color=C_BLUE_DARK, fontfamily="DejaVu Sans")

    plt.tight_layout(pad=0.2)
    plt.savefig(buf, format="PNG", bbox_inches="tight",
                transparent=True, dpi=130)
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_general_risk_chart_bytes(raport: list, language: str) -> io.BytesIO:
    """Donut mare — procent mediu real + mesaj motivațional."""
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
        if procent_mediu >= 75:
            mesaj = f"Ați atins {procent_mediu}% din vârful ideal de performanță."
        elif procent_mediu >= 40:
            mesaj = f"Sunteți la {procent_mediu}% distanță de afacerea perfectă."
        else:
            mesaj = f"Performanța actuală: {procent_mediu}% din nivelul ideal."
    else:
        nivel_text = (
            "Высокий риск"     if color == C_RED else
            "Средний риск"     if color == C_ORANGE else
            "Минимальный риск"
        )
        if procent_mediu >= 75:
            mesaj = f"Вы достигли {procent_mediu}% от идеального пика эффективности."
        elif procent_mediu >= 40:
            mesaj = f"Вы на {procent_mediu}% пути к идеальному бизнесу."
        else:
            mesaj = f"Текущий результат: {procent_mediu}% от идеального уровня."

    fig, ax = plt.subplots(figsize=(4.0, 4.0), facecolor="none")

    ax.pie(
        [procent_mediu, 100 - procent_mediu],
        startangle=90,
        colors=[color, C_GRAY_LIGHT],
        wedgeprops={"width": 0.30, "edgecolor": C_WHITE, "linewidth": 2.5},
        counterclock=False
    )

    ax.text(0,  0.14, f"{procent_mediu}%",
            ha="center", va="center",
            fontsize=26, fontweight="bold",
            color=C_BLUE_DARK, fontfamily="DejaVu Sans")

    ax.text(0, -0.20, nivel_text,
            ha="center", va="center",
            fontsize=10, fontweight="bold",
            color=color, fontfamily="DejaVu Sans")

    ax.set_aspect("equal")

    fig.text(0.5, 0.01, mesaj,
             ha="center", va="bottom",
             fontsize=8.5, style="italic",
             color=C_GRAY_TEXT, fontfamily="DejaVu Sans")

    plt.tight_layout(pad=0.5)
    plt.savefig(buf, format="PNG", bbox_inches="tight",
                transparent=True, dpi=140)
    plt.close(fig)
    buf.seek(0)
    return buf


# ==================== GENERARE PDF ====================

async def generate_pdf(user_id: int, language: str, filename="raport.pdf"):

    if language == "ro":
        titlu_doc     = "Raport de Evaluare a Riscului"
        subtitlu_doc  = "Analiză detaliată pe categorii · BizzCheck"
        titlu_sectie  = "📊  Evaluare pe categorii"
        titlu_general = "🎯  Scor General"
    else:
        titlu_doc     = "Отчёт об оценке рисков"
        subtitlu_doc  = "Детальный анализ по категориям · BizzCheck"
        titlu_sectie  = "📊  Оценка по категориям"
        titlu_general = "🎯  Общий результат"

    elements = []
    elements.append(Spacer(1, 0.5 * cm))

    # Header
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

        # ---- Categorii ----
        elements.append(_section_bar(titlu_sectie))
        elements.append(Spacer(1, 0.45 * cm))

        IMG_SIZE = 5.0 * cm
        COLS     = 3
        COL_W    = MAIN_W / COLS

        chart_data = []
        row = []
        for cat, scor, max_scor, nivel in raport:
            buf = generate_chart_bytes(scor, max_scor, nivel, cat, language)
            row.append(Image(buf, width=IMG_SIZE, height=IMG_SIZE))
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

        # ---- Pagină nouă pentru scor general ----
        elements.append(PageBreak())
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(_header_block(titlu_doc, subtitlu_doc))
        elements.append(Spacer(1, 0.6 * cm))
        elements.append(_section_bar(titlu_general))
        elements.append(Spacer(1, 0.35 * cm))

        # ---- Grafic donut general ----
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
        elements.append(Spacer(1, 0.5 * cm))

        # ---- Calculăm procentul mediu real ----
        procente_carduri = [
            int((d["scor"] / d["max_scor"]) * 100)
            for d in results_dict.values() if d["max_scor"] > 0
        ]
        procent_card = int(sum(procente_carduri) / len(procente_carduri)) if procente_carduri else 0

        niveluri_toate = [d["nivel"] for d in results_dict.values()]
        worst          = _worst_nivel(niveluri_toate, language)
        color_general  = _color_for_nivel(worst, language)

        # Definim cele 3 scenarii — culoare + text bazate pe risc real
        if language == "ro":
            scenarii = [
                {
                    "nivel_key": "minim",
                    "color":  C_GREEN,
                    "emoji":  "🏆",
                    "titlu":  "Performanță înaltă",
                    "mesaj":  f"Ați atins {procent_card}% din vârful ideal de performanță.",
                    "sub":    "Afacerea ta funcționează la un nivel excelent. Menține această direcție!",
                    "nivel_display": "Risc Minim",
                },
                {
                    "nivel_key": "mediu",
                    "color":  C_ORANGE,
                    "emoji":  "📈",
                    "titlu":  "În dezvoltare",
                    "mesaj":  f"Sunteți la {procent_card}% distanță de afacerea perfectă.",
                    "sub":    "Există oportunități clare de îmbunătățire. Acționați acum!",
                    "nivel_display": "Risc Mediu",
                },
                {
                    "nivel_key": "ridicat",
                    "color":  C_RED,
                    "emoji":  "⚠️",
                    "titlu":  "Necesită atenție urgentă",
                    "mesaj":  f"Performanța actuală: {procent_card}% din nivelul ideal.",
                    "sub":    "Recomandăm o analiză urgentă a punctelor slabe.",
                    "nivel_display": "Risc Ridicat",
                },
            ]
        else:
            scenarii = [
                {
                    "nivel_key": "minim",
                    "color":  C_GREEN,
                    "emoji":  "🏆",
                    "titlu":  "Высокая эффективность",
                    "mesaj":  f"Вы достигли {procent_card}% от идеального пика эффективности.",
                    "sub":    "Ваш бизнес работает на отличном уровне. Сохраняйте этот курс!",
                    "nivel_display": "Минимальный риск",
                },
                {
                    "nivel_key": "mediu",
                    "color":  C_ORANGE,
                    "emoji":  "📈",
                    "titlu":  "В развитии",
                    "mesaj":  f"Вы на {procent_card}% пути к идеальному бизнесу.",
                    "sub":    "Есть чёткие возможности для улучшения. Действуйте сейчас!",
                    "nivel_display": "Средний риск",
                },
                {
                    "nivel_key": "ridicat",
                    "color":  C_RED,
                    "emoji":  "⚠️",
                    "titlu":  "Требует срочного внимания",
                    "mesaj":  f"Текущий результат: {procent_card}% от идеального уровня.",
                    "sub":    "Рекомендуем срочный анализ слабых мест.",
                    "nivel_display": "Высокий риск",
                },
            ]

        # Stiluri text card
        card_titlu_style = ParagraphStyle(
            "CardTitlu",
            fontName="DejaVu-Bold",
            fontSize=18,
            textColor=colors.HexColor(C_WHITE),
            leading=24,
            alignment=1,
            spaceAfter=10,
        )
        card_mesaj_style = ParagraphStyle(
            "CardMesaj",
            fontName="DejaVu-Bold",
            fontSize=12,
            textColor=colors.HexColor(C_WHITE),
            leading=18,
            alignment=1,
            spaceAfter=8,
        )
        card_sub_style = ParagraphStyle(
            "CardSub",
            fontName="DejaVu",
            fontSize=10,
            textColor=colors.HexColor(C_WHITE),
            leading=15,
            alignment=1,
        )

        # O pagină per scenariu
        for scenariu in scenarii:
            elements.append(PageBreak())
            elements.append(Spacer(1, 0.5 * cm))
            elements.append(_header_block(titlu_doc, subtitlu_doc))
            elements.append(Spacer(1, 0.5 * cm))
            elements.append(_section_bar(f"{scenariu['emoji']}  {scenariu['titlu']}"))
            elements.append(Spacer(1, 0.4 * cm))

            # Diagrama donut pentru acest scenariu
            buf_scenariu = io.BytesIO()
            fig, ax = plt.subplots(figsize=(3.8, 3.8), facecolor="none")
            ax.pie(
                [procent_card, 100 - procent_card],
                startangle=90,
                colors=[scenariu["color"], C_GRAY_LIGHT],
                wedgeprops={"width": 0.30, "edgecolor": C_WHITE, "linewidth": 2.5},
                counterclock=False
            )
            ax.text(0,  0.14, f"{procent_card}%",
                    ha="center", va="center",
                    fontsize=26, fontweight="bold",
                    color=C_BLUE_DARK, fontfamily="DejaVu Sans")
            ax.text(0, -0.20, scenariu["nivel_display"],
                    ha="center", va="center",
                    fontsize=10, fontweight="bold",
                    color=scenariu["color"], fontfamily="DejaVu Sans")
            ax.set_aspect("equal")
            plt.tight_layout(pad=0.5)
            plt.savefig(buf_scenariu, format="PNG", bbox_inches="tight",
                        transparent=True, dpi=140)
            plt.close(fig)
            buf_scenariu.seek(0)

            donut_img = Image(buf_scenariu, width=7.5 * cm, height=7.5 * cm)

            # Text bloc dreapta
            text_cell = [
                Spacer(1, 0.6 * cm),
                Paragraph(scenariu["mesaj"], card_mesaj_style),
                Spacer(1, 0.3 * cm),
                Paragraph(scenariu["sub"], card_sub_style),
                Spacer(1, 0.6 * cm),
            ]

            # Layout: donut stânga | text dreapta
            LEFT_W  = MAIN_W * 0.42
            RIGHT_W = MAIN_W * 0.58

            layout_tbl = Table(
                [[donut_img, text_cell]],
                colWidths=[LEFT_W, RIGHT_W]
            )
            layout_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(scenariu["color"])),
                ("ALIGN",         (0, 0), (0, 0),   "CENTER"),
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN",         (1, 0), (1, 0),   "LEFT"),
                ("LEFTPADDING",   (0, 0), (0, 0),   8),
                ("RIGHTPADDING",  (0, 0), (0, 0),   8),
                ("LEFTPADDING",   (1, 0), (1, 0),   16),
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