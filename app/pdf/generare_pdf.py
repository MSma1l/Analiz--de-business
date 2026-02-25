import io
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.platypus import (
    Table, TableStyle, Paragraph, Spacer,
    Image, SimpleDocTemplate, PageBreak
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

# ==================== PALETA BUSINESS PREMIUM ====================
C_NAVY        = "#1C3F6E"
C_STEEL       = "#2E6DA4"
C_WHITE       = "#FFFFFF"
C_GOLD        = "#D4A017"
C_SLATE       = "#2C3E50"

# Culori semafor — bazate pe PROCENT
C_GREEN_PRO   = "#1E9E5E"   # >= 80%
C_ORANGE_PRO  = "#D4861E"   # 65-79%
C_RED_PRO     = "#B03030"   # < 65%

# Carduri grupare risc — aceleasi culori
C_BG_GREEN    = "#1E9E5E"
C_BG_ORANGE   = "#C97520"
C_BG_RED      = "#B03030"

C_ROW_A       = "#EAF0F6"
C_ROW_B       = "#FFFFFF"

PAGE_W  = A4[0]
MAIN_W  = PAGE_W * 0.82
MARGIN  = (PAGE_W - MAIN_W) / 2

DONUTS_PER_PAGE = 4
IMG_W = 8.0 * cm
IMG_H = 8.0 * cm
COLS  = 2
COL_W = MAIN_W / COLS


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

def _calc_procent(scor: int, max_scor: int) -> int:
    """
    Calculeaza procentul unui bloc.
    Daca max_scor == 0 SAU scor == 0 → returnează 0 (blocul apare cu 0%).
    """
    if max_scor <= 0 or scor <= 0:
        return 0
    return int((scor / max_scor) * 100)


def _color_for_procent(procent: int) -> str:
    """Culoare bazata STRICT pe procent: <65 rosu, 65-79 portocaliu, >=80 verde."""
    if procent >= 80:
        return C_GREEN_PRO
    elif procent >= 65:
        return C_ORANGE_PRO
    return C_RED_PRO


def _zona_for_procent(procent: int) -> str:
    """Returneaza zona de risc bazata pe procent."""
    if procent >= 80:
        return "minim"
    elif procent >= 65:
        return "mediu"
    return "ridicat"


def _short_title(categorie: str, max_len: int = 200) -> str:
    titlu = categorie.split(". ", 1)[1] if ". " in categorie else categorie
    return titlu if len(titlu) <= max_len else titlu[:max_len - 1] + "…"


# ==================== COMPONENTE LAYOUT ====================

def _header_block(titlu_doc: str, subtitlu_doc: str) -> Table:
    title_style = ParagraphStyle(
        "HdrTitle", fontName="DejaVu-Bold", fontSize=20,
        textColor=colors.HexColor(C_WHITE), alignment=1, leading=28, spaceAfter=4,
    )
    sub_style = ParagraphStyle(
        "HdrSub", fontName="DejaVu", fontSize=9,
        textColor=colors.HexColor(C_GOLD), alignment=1, leading=14,
    )
    cell = [
        Spacer(1, 0.5 * cm),
        Paragraph(titlu_doc, title_style),
        Spacer(1, 0.1 * cm),
        Paragraph(subtitlu_doc, sub_style),
        Spacer(1, 0.5 * cm),
    ]
    tbl = Table([[cell]], colWidths=[MAIN_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(C_NAVY)),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 24),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 24),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LINEBELOW",     (0, 0), (-1, -1), 3, colors.HexColor(C_GOLD)),
    ]))
    return tbl


def _section_bar(text: str) -> Table:
    style = ParagraphStyle(
        "SecBar", fontName="DejaVu-Bold", fontSize=11,
        textColor=colors.HexColor(C_WHITE), alignment=0, leading=16,
    )
    tbl = Table([[Paragraph(text, style)]], colWidths=[MAIN_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(C_STEEL)),
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 16),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBEFORE",    (0, 0), (0, -1),  5, colors.HexColor(C_GOLD)),
    ]))
    return tbl


# ==================== GRAFICE ====================

def generate_chart_bytes(scor: int, max_scor: int, nivel: str,
                         categorie: str, language: str) -> io.BytesIO:
    """
    Donut 8x8 — culoare bazata pe PROCENT, procent in mijloc.
    Blocurile cu scor=0 sau max_scor=0 apar cu 0% (inel complet gri).
    """
    buf     = io.BytesIO()
    procent = _calc_procent(scor, max_scor)
    color   = _color_for_procent(procent)

    fig, ax = plt.subplots(figsize=(3.2, 3.2), facecolor="none")

    if procent == 0:
        # Inel complet gri — nicio felie colorata
        ax.pie(
            [100],
            startangle=90,
            colors=["#DDE3EA"],
            wedgeprops={"width": 0.30, "edgecolor": "#FFFFFF", "linewidth": 2.5},
            counterclock=False
        )
    else:
        ax.pie(
            [procent, 100 - procent],
            startangle=90,
            colors=[color, "#DDE3EA"],
            wedgeprops={"width": 0.30, "edgecolor": "#FFFFFF", "linewidth": 2.5},
            counterclock=False
        )

    ax.text(0, 0, f"{procent}%",
            ha="center", va="center",
            fontsize=17, fontweight="bold",
            color=color, fontfamily="DejaVu Sans")
    ax.set_aspect("equal")
    plt.tight_layout(pad=0.1)
    plt.savefig(buf, format="PNG", bbox_inches="tight", transparent=True, dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def _donut_nivel_bytes(procent: int, card_color: str) -> io.BytesIO:
    """Donut pentru cardul de grupare — inel alb pe fond colorat, procent alb."""
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(4.0, 4.0), facecolor="none")

    if procent == 0:
        ax.pie(
            [100],
            startangle=90,
            colors=["#FFFFFF40"],
            wedgeprops={"width": 0.32, "edgecolor": card_color, "linewidth": 2.5},
            counterclock=False
        )
    else:
        ax.pie(
            [procent, 100 - procent],
            startangle=90,
            colors=[C_WHITE, "#FFFFFF40"],
            wedgeprops={"width": 0.32, "edgecolor": card_color, "linewidth": 2.5},
            counterclock=False
        )

    ax.text(0, 0, f"{procent}%",
            ha="center", va="center",
            fontsize=28, fontweight="bold",
            color=C_WHITE, fontfamily="DejaVu Sans")
    ax.set_aspect("equal")
    plt.tight_layout(pad=0.3)
    plt.savefig(buf, format="PNG", bbox_inches="tight", transparent=True, dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def _build_variants_block(procent_mediu: int, language: str) -> list:
    elements = []
    is_ro = language == "ro"

    label_style = ParagraphStyle(
        "VarLabel", fontName="DejaVu-Bold", fontSize=9,
        textColor=colors.HexColor(C_STEEL), leading=13, spaceAfter=2,
    )
    text_style = ParagraphStyle(
        "VarText", fontName="DejaVu", fontSize=11,
        textColor=colors.HexColor(C_SLATE), leading=16, spaceAfter=0, leftIndent=8,
    )

    if is_ro:
        variants = [
            {"label": "Varianta A",
             "text": f"Ați atins {procent_mediu}% din vârful ideal de performanță.",
             "bg": "#EAF0F6", "accent": C_STEEL},
            {"label": "Varianta B",
             "text": f"Sunteți la {procent_mediu}% distanță de afacerea perfectă.",
             "bg": "#FDF6E3", "accent": C_ORANGE_PRO},
            {"label": "Varianta C",
             "text": f"Performanța actuală: {procent_mediu}% din nivelul ideal.",
             "bg": "#EAF0F6", "accent": C_STEEL},
        ]
    else:
        variants = [
            {"label": "Вариант A",
             "text": f"Вы достигли {procent_mediu}% от идеального пика эффективности.",
             "bg": "#EAF0F6", "accent": C_STEEL},
            {"label": "Вариант B",
             "text": f"Вы на {procent_mediu}% пути к идеальному бизнесу.",
             "bg": "#FDF6E3", "accent": C_ORANGE_PRO},
            {"label": "Вариант C",
             "text": f"Текущий результат: {procent_mediu}% от идеального уровня.",
             "bg": "#EAF0F6", "accent": C_STEEL},
        ]

    elements.append(Spacer(1, 0.2 * cm))
    for v in variants:
        cell_content = [
            Spacer(1, 0.14 * cm),
            Paragraph(v["label"], label_style),
            Paragraph(v["text"], text_style),
            Spacer(1, 0.14 * cm),
        ]
        row_tbl = Table([[cell_content]], colWidths=[MAIN_W])
        row_tbl.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, -1), colors.HexColor(v["bg"])),
            ("LEFTPADDING",  (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),
            ("TOPPADDING",   (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
            ("LINEBEFORE",   (0, 0), (0, -1),  4, colors.HexColor(v["accent"])),
        ]))
        elements.append(row_tbl)
        elements.append(Spacer(1, 0.14 * cm))

    return elements


def _build_donut_pages(raport: list, titlu_doc: str, subtitlu_doc: str,
                       titlu_general: str, bloc_prefix: str,
                       procent_mediu: int, language: str) -> list:
    """
    Construieste paginile cu donuts: 4 per pagina (2 coloane x 2 randuri), 8x8 cm.
    Prima pagina include header + section_bar + variants.
    Paginile urmatoare incep cu PageBreak + header + section_bar.
    TOATE blocurile apar, inclusiv cele cu scor=0.
    """
    elements = []

    bloc_num_style = ParagraphStyle(
        "BlocNum", fontName="DejaVu-Bold", fontSize=13,
        textColor=colors.HexColor(C_NAVY), alignment=1, leading=18, spaceAfter=3,
    )
    bloc_title_style = ParagraphStyle(
        "BlocTitle", fontName="DejaVu-Bold", fontSize=10,
        textColor=colors.HexColor(C_STEEL), alignment=1, leading=14, spaceAfter=2,
    )

    chunks = [raport[i:i + DONUTS_PER_PAGE] for i in range(0, len(raport), DONUTS_PER_PAGE)]

    for page_idx, chunk in enumerate(chunks):
        if page_idx == 0:
            pass
        else:
            elements.append(PageBreak())
            elements.append(Spacer(1, 0.5 * cm))
            elements.append(_header_block(titlu_doc, subtitlu_doc))
            elements.append(Spacer(1, 0.45 * cm))
            elements.append(_section_bar(titlu_general))
            elements.append(Spacer(1, 0.4 * cm))

        gen_data = []
        gen_row  = []
        start_idx = page_idx * DONUTS_PER_PAGE

        for local_idx, (cat, scor, max_scor, nivel) in enumerate(chunk):
            g_idx      = start_idx + local_idx + 1
            g_buf      = generate_chart_bytes(scor, max_scor, nivel, cat, language)
            full_title = cat.split(". ", 1)[1] if ". " in cat else cat
            cell = [
                Paragraph(f"{bloc_prefix} {g_idx}", bloc_num_style),
                Spacer(1, 0.06 * cm),
                Paragraph(full_title, bloc_title_style),
                Spacer(1, 0.08 * cm),
                Image(g_buf, width=IMG_W, height=IMG_H),
                Spacer(1, 0.1 * cm),
            ]
            gen_row.append(cell)
            if len(gen_row) == COLS:
                gen_data.append(gen_row)
                gen_row = []

        if gen_row:
            while len(gen_row) < COLS:
                gen_row.append(Spacer(COL_W, IMG_H))
            gen_data.append(gen_row)

        row_styles = []
        for i in range(len(gen_data)):
            bg = C_ROW_A if i % 2 == 0 else C_ROW_B
            row_styles.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor(bg)))

        gen_tbl = Table(gen_data, colWidths=[COL_W] * COLS)
        gen_tbl.setStyle(TableStyle([
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
            ("LINEAFTER",     (0, 0), (0, -1),  1, colors.HexColor("#C8D6E5")),
            ("LINEBELOW",     (0, 0), (-1, -2), 1, colors.HexColor("#C8D6E5")),
            *row_styles,
        ]))
        elements.append(gen_tbl)

    return elements


# ==================== GENERARE PDF ====================

async def generate_pdf(user_id: int, language: str, filename="raport.pdf"):

    if language == "ro":
        titlu_doc     = "Raport de Evaluare a Riscului"
        subtitlu_doc  = "Analiză detaliată pe categorii  ·  BizzCheck"
        titlu_general = "  Scor General pe Categorii"
        bloc_prefix   = "Bloc"
    else:
        titlu_doc     = "Отчёт об оценке рисков"
        subtitlu_doc  = "Детальный анализ по категориям  ·  BizzCheck"
        titlu_general = "  Общий результат по категориям"
        bloc_prefix   = "Блок"

    elements = []
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(_header_block(titlu_doc, subtitlu_doc))
    elements.append(Spacer(1, 0.55 * cm))

    results_dict = await get_user_results(user_id)

    if not results_dict:
        no_data_style = ParagraphStyle(
            "ND", fontName="DejaVu", fontSize=10,
            textColor=colors.HexColor(C_NAVY)
        )
        no_data = ("Nu există rezultate disponibile."
                   if language == "ro" else "Нет доступных результатов.")
        elements.append(Paragraph(no_data, no_data_style))
    else:
        # ---- TOATE blocurile intra in raport, inclusiv scor=0 ----
        raport = [
            (cat, d["scor"], d["max_scor"], d["nivel"])
            for cat, d in results_dict.items()
        ]

        elements.append(_section_bar(titlu_general))
        elements.append(Spacer(1, 0.4 * cm))

        # Media include TOATE blocurile; cele cu scor=0 contribuie cu 0%
        procente_all = [_calc_procent(scor, max_scor) for _, scor, max_scor, _ in raport]
        procent_mediu = int(sum(procente_all) / len(procente_all)) if procente_all else 0

        # ---- Pagini cu donuts: 4 per pagina, 2 coloane x 2 randuri, 8x8 cm ----
        for el in _build_donut_pages(raport, titlu_doc, subtitlu_doc,
                                     titlu_general, bloc_prefix,
                                     procent_mediu, language):
            elements.append(el)

        # ==================== VARIANTE EXPLICATIVE (DUPĂ TOATE DONUTS) ====================
        elements.append(PageBreak())
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(_header_block(titlu_doc, subtitlu_doc))
        elements.append(Spacer(1, 0.45 * cm))

        titlu_variants = "  Scor general" if language == "ro" else "  Интерпретация общего результата"
        elements.append(_section_bar(titlu_variants))
        elements.append(Spacer(1, 0.4 * cm))

        # ---- Donut simplu centrat cu scorul mediu general (fara fundal, fara text lateral) ----
        buf_general = generate_chart_bytes(procent_mediu, 100, "", "", language)
        donut_general_img = Image(buf_general, width=8.0 * cm, height=8.0 * cm)

        donut_center_tbl = Table([[donut_general_img]], colWidths=[MAIN_W])
        donut_center_tbl.setStyle(TableStyle([
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        elements.append(donut_center_tbl)
        elements.append(Spacer(1, 0.5 * cm))

        for el in _build_variants_block(procent_mediu, language):
            elements.append(el)

        # ==================== GRUPARE RISC PE PROCENT ====================
        # IMPORTANT: gruparea se face pe PROCENT calculat, NU pe eticheta din BD
        # Blocurile cu scor=0 → procent=0 → zona "ridicat" (apar obligatoriu)
        grupe_risc = {"minim": [], "mediu": [], "ridicat": []}
        for cat, scor, max_scor, nivel in raport:
            procent = _calc_procent(scor, max_scor)
            zona    = _zona_for_procent(procent)
            print(f"[DEBUG] {cat[:40]} scor={scor} max={max_scor} procent={procent}% nivel_bd={nivel} zona={zona}")
            grupe_risc[zona].append((cat, scor, max_scor, nivel))

        config_risc = {
            "ridicat": {
                "card_color": C_BG_RED,
                "ro": {
                    "titlu":    "  Zone cu risc ridicat",
                    "mesaj_fn": lambda p: f"Performanța actuală: {p}% din nivelul ideal.",
                    "sub":      "Aceste blocuri necesită intervenție imediată.",
                },
                "ru": {
                    "titlu":    "  Зоны высокого риска ",
                    "mesaj_fn": lambda p: f"Текущий результат: {p}% от идеального уровня.",
                    "sub":      "Эти блоки требуют немедленного вмешательства.",
                },
            },
            "mediu": {
                "card_color": C_BG_ORANGE,
                "ro": {
                    "titlu":    "  Zone în dezvoltare ",
                    "mesaj_fn": lambda p: f"Sunteți la {p}% distanță de afacerea perfectă.",
                    "sub":      "Există oportunități clare de îmbunătățire.",
                },
                "ru": {
                    "titlu":    "  Зоны развития ",
                    "mesaj_fn": lambda p: f"Вы на {p}% пути к идеальному бизнесу.",
                    "sub":      "Есть чёткие возможности для улучшения.",
                },
            },
            "minim": {
                "card_color": C_BG_GREEN,
                "ro": {
                    "titlu":    "  Zone cu performanță înaltă ",
                    "mesaj_fn": lambda p: f"Ați atins {p}% din vârful ideal de performanță.",
                    "sub":      "Aceste blocuri funcționează excelent. Mențineți direcția.",
                },
                "ru": {
                    "titlu":    "  Зоны высокой эффективности ",
                    "mesaj_fn": lambda p: f"Вы достигли {p}% от идеального пика эффективности.",
                    "sub":      "Эти блоки работают отлично. Сохраняйте курс.",
                },
            },
        }

        card_mesaj_style = ParagraphStyle(
            "CardMesaj", fontName="DejaVu-Bold", fontSize=14,
            textColor=colors.HexColor(C_WHITE), leading=20, alignment=0, spaceAfter=6,
        )
        card_sub_style = ParagraphStyle(
            "CardSub", fontName="DejaVu", fontSize=11,
            textColor=colors.HexColor("#E8E8E8"), leading=16, alignment=0, spaceAfter=8,
        )
        cat_item_style = ParagraphStyle(
            "CatItem", fontName="DejaVu-Bold", fontSize=10,
            textColor=colors.HexColor(C_WHITE), leading=15, alignment=0,
        )

        for nivel_key in ["ridicat", "mediu", "minim"]:
            categorii_nivel = grupe_risc[nivel_key]
            if not categorii_nivel:
                continue

            cfg        = config_risc[nivel_key]
            lang_cfg   = cfg[language]
            card_color = cfg["card_color"]

            procente_nivel = [_calc_procent(scor, max_scor) for _, scor, max_scor, _ in categorii_nivel]
            procent_nivel = int(sum(procente_nivel) / len(procente_nivel)) if procente_nivel else 0
            mesaj_text    = lang_cfg["mesaj_fn"](procent_nivel)

            elements.append(PageBreak())
            elements.append(Spacer(1, 0.5 * cm))
            elements.append(_header_block(titlu_doc, subtitlu_doc))
            elements.append(Spacer(1, 0.45 * cm))
            elements.append(_section_bar(lang_cfg["titlu"]))
            elements.append(Spacer(1, 0.4 * cm))

            buf_nivel = _donut_nivel_bytes(procent_nivel, card_color)
            donut_img = Image(buf_nivel, width=8.0 * cm, height=8.0 * cm)

            lista_cat = [Spacer(1, 0.55 * cm)]
            lista_cat.append(Paragraph(mesaj_text, card_mesaj_style))
            lista_cat.append(Spacer(1, 0.18 * cm))
            lista_cat.append(Paragraph(lang_cfg["sub"], card_sub_style))
            lista_cat.append(Spacer(1, 0.28 * cm))

            for cat, scor, max_scor, nivel in categorii_nivel:
                full_title = cat.split(". ", 1)[1] if ". " in cat else cat
                bloc_idx   = next(
                    (i + 1 for i, (c, _, _, _) in enumerate(raport) if c == cat), "?"
                )
                procent_cat = _calc_procent(scor, max_scor)
                lista_cat.append(
                    Paragraph(
                        f"— {bloc_prefix} {bloc_idx}:  {full_title}  ({procent_cat}%)",
                        cat_item_style
                    )
                )
                lista_cat.append(Spacer(1, 0.08 * cm))
            lista_cat.append(Spacer(1, 0.55 * cm))

            LEFT_W  = MAIN_W * 0.38
            RIGHT_W = MAIN_W * 0.62

            layout_tbl = Table([[donut_img, lista_cat]], colWidths=[LEFT_W, RIGHT_W])
            layout_tbl.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(card_color)),
                ("ALIGN",         (0, 0), (0, 0),   "CENTER"),
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN",         (1, 0), (1, 0),   "LEFT"),
                ("LEFTPADDING",   (0, 0), (0, 0),   12),
                ("RIGHTPADDING",  (0, 0), (0, 0),   12),
                ("LEFTPADDING",   (1, 0), (1, 0),   20),
                ("RIGHTPADDING",  (1, 0), (1, 0),   16),
                ("TOPPADDING",    (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ("LINEABOVE",     (0, 0), (-1, 0),  2, colors.HexColor(C_GOLD)),
                ("LINEBELOW",     (0, -1),(-1, -1), 2, colors.HexColor(C_GOLD)),
                ("LINEAFTER",     (0, 0), (0, -1),  1, colors.HexColor("#FFFFFF50")),
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