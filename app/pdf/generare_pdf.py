import matplotlib.pyplot as plt
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy import select
from bd_sqlite.conexiune import async_session
from bd_sqlite.models import Raspuns, Intrebare
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle


# ================= FONT =================

FONT_PATH = "pdf/assets/DejaVuSans.ttf"
pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))


# ================= BACKGROUND =================

def draw_background(canvas, doc):
    canvas.drawImage(
        "pdf/assets/background.jpg",
        0, 0,
        width=A4[0],
        height=A4[1]
    )


# ================= DATABASE =================

async def get_category_scores(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Raspuns.valoare, Intrebare.categorie)
            .join(Intrebare, Raspuns.intrebare_id == Intrebare.id)
            .where(Raspuns.user_id == user_id)
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

    labels = {
        "ro": ("OK", "Probleme"),
        "ru": ("Хорошо", "Проблемы")
    }

    ok_label, bad_label = labels[language]

    for category, percent in scores.items():
        good = percent
        bad = 100 - percent

        plt.figure()
        plt.pie(
            [good, bad],
            labels=[ok_label, bad_label],
            autopct="%1.0f%%",
            startangle=90
        )
        plt.title(category)
        plt.axis("equal")

        path = f"charts/{category}_{language}.png"
        plt.savefig(path)
        plt.close()

        charts[category] = path

    return charts


# ================= PDF =================

def generate_pdf(charts: dict, scores: dict, language: str, filename="raport.pdf"):
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleDejaVu",
        parent=styles["Title"],
        fontName="DejaVu",
        alignment=1
    )

    subtitle_style = ParagraphStyle(
        "SubtitleDejaVu",
        parent=styles["Heading2"],
        fontName="DejaVu",
        spaceAfter=12
    )

    normal_style = ParagraphStyle(
        "NormalDejaVu",
        parent=styles["Normal"],
        fontName="DejaVu"
    )

    titles = {
        "ro": "Raport Analiză Business",
        "ru": "Отчёт бизнес-анализа"
    }

    elements = []
    elements.append(Spacer(1, 2 * cm))
    elements.append(Paragraph(titles[language], title_style))
    elements.append(Spacer(1, 1 * cm))

    for i, (category, img_path) in enumerate(charts.items()):
        percent = scores[category]

        if percent <= 40:
            status = "🔴 Risc ridicat" if language == "ro" else "🔴 Высокий риск"
        elif percent <= 70:
            status = "🟠 Nivel mediu" if language == "ro" else "🟠 Средний уровень"
        else:
            status = "🟢 Stare bună" if language == "ro" else "🟢 Хорошее состояние"

        text = f"<b>{category}</b>: {percent}% — {status}"

        elements.append(Paragraph(text, subtitle_style))
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(Image(img_path, width=12 * cm, height=12 * cm))

        if i < len(charts) - 1:
            elements.append(PageBreak())

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    doc.build(
        elements,
        onFirstPage=draw_background,
        onLaterPages=draw_background
    )

    return filename


# ================= MAIN =================

async def build_user_report(user_id: int, language: str):
    scores = await get_category_scores(user_id)
    charts = generate_charts(scores, language)
    pdf_path = generate_pdf(charts, scores, language)
    return pdf_path
