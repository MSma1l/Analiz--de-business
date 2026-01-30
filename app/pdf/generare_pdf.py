import matplotlib.pyplot as plt
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy import select
from bd_sqlite.conexiune import async_session
from bd_sqlite.models import Raspuns, Intrebare
import os
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from PyPDF2 import PdfMerger


FONT_PATH = "pdf/assets/DejaVuSans.ttf"
pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))


def append_existing_pdf(generated_pdf: str, extra_pdf: str, output_pdf: str):
    merger = PdfMerger()
    merger.append(extra_pdf) 
    merger.append(generated_pdf)      
    merger.write(output_pdf)
    merger.close()


def draw_background(canvas, doc):
    canvas.drawImage(
        "pdf/assets/bg.jpg",
        0, 0,
        width=A4[0],
        height=A4[1]
    )


async def get_category_scores(user_id: int, language: str):
    async with async_session() as session:
        result = await session.execute(
            select(Raspuns.valoare, Intrebare.categorie)
            .join(Intrebare, Raspuns.intrebare_id == Intrebare.id)
            .where(
                Raspuns.user_id == user_id,
                Intrebare.language == language
            )
        )

        rows = result.all()

    data = {}

    for value, category in rows:
        if category not in data:
            data[category] = {"yes": 0, "total": 0}

        data[category]["total"] += 1
        if value.lower() in ["da", "yes", "true", "1"]:
            data[category]["yes"] += 1

    percentages = {}
    for cat, v in data.items():
        percentages[cat] = round(v["yes"] / v["total"] * 100)

    return percentages



# ================= CHARTS =================

def generate_charts(scores: dict, language: str):
    charts = {}
    os.makedirs("charts", exist_ok=True)

    for category, percent in scores.items():
        good = percent
        bad = 100 - percent

        plt.figure(figsize=(3, 3))
        plt.pie(
            [good, bad],
            startangle=90,
            colors=["#1f77ff", "#e6e6e6"],
            wedgeprops={"width": 0.3}
        )

        plt.text(0, 0, f"{percent}%", ha="center", va="center", fontsize=16, fontweight="bold")
        plt.title(category, fontsize=10)
        plt.axis("equal")

        path = f"charts/{category}_{language}.png"
        plt.savefig(path, bbox_inches="tight", transparent=True)
        plt.close()

        charts[category] = path

    return charts




def generate_pdf(charts: dict, scores: dict, language: str, filename="raport.pdf"):
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleDejaVu",
        parent=styles["Title"],
        fontName="DejaVu",
        alignment=1
    )

    titles = {
        "ro": "Raport de analiză a business-ului",
        "ru": "Отчет бизнес-анализа"
    }

    elements = []
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Paragraph(titles[language], title_style))
    elements.append(Spacer(1, 0.5 * cm))

    data = []
    row = []

    for i, (category, img_path) in enumerate(charts.items()):
        img = Image(img_path, width=6 * cm, height=6 * cm)

        cell_table = Table(
            [[img]],
            colWidths=7 * cm
        )

        row.append(cell_table)

        if len(row) == 2:
            data.append(row)
            row = []

    if row:
        data.append(row)


    main_table = Table(data, colWidths=[8 * cm, 8 * cm, 8 * cm])
    main_table.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 12),
    ]))

    elements.append(main_table)

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm,
    )

    doc.build(elements, onFirstPage=draw_background)

    return filename


# ================= MAIN =================

async def build_user_report(user_id: int, language: str):
    scores = await get_category_scores(user_id, language)

    charts = generate_charts(scores, language)
    temp_pdf = generate_pdf(charts, scores, language, filename="temp_report.pdf")
  
    if language == "ro":
        design_pdf = "pdf/assets/pdfro.pdf"
    else:
        design_pdf = "pdf/assets/pdfru.pdf"
    
    final_pdf = "BIZCHECK_RAPORT.pdf"

    append_existing_pdf(temp_pdf, design_pdf, final_pdf)

    return final_pdf

