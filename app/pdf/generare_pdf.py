import matplotlib.pyplot as plt
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy import select
from bd_sqlite.conexiune import async_session
from bd_sqlite.models import Raspuns, Intrebare
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak


def draw_background(canvas, doc):
    canvas.drawImage(
        "pdf/assets/background.jpg",
        0, 0,
        width=A4[0],
        height=A4[1]
    )
    
    
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


def generate_charts(scores: dict, language: str):
    image_paths = []
    os.makedirs("charts", exist_ok=True)

    labels = {
        "ro": ("OK", "Probleme"),
        "ru": ("Хорошо", "Проблемы")
    }

    ok_label, bad_label = labels[language]

    for category, percent in scores.items():
        good = percent
        bad = 100 - percent

        # ===== PIE CHART (disc rotund) =====
        plt.figure()
        plt.pie(
            [good, bad],
            labels=[ok_label, bad_label],
            autopct="%1.0f%%",
            colors=["green", "red"],
            startangle=90
        )
        plt.title(f"{category}")
        plt.axis("equal")

        pie_path = f"charts/{category}_{language}_pie.png"
        plt.savefig(pie_path)
        plt.close()

        image_paths.append(pie_path)

        plt.figure()
        plt.bar([ok_label, bad_label], [good, bad], color=["green", "red"])
        plt.ylim(0, 100)
        plt.title(f"{category}")

        bar_path = f"charts/{category}_{language}_bar.png"
        plt.savefig(bar_path)
        plt.close()

        image_paths.append(bar_path)

    return image_paths



def generate_pdf(image_paths: list, scores: dict, language: str, filename="raport.pdf"):
    styles = getSampleStyleSheet()
    elements = []

    title_style = styles["Title"]
    title_style.alignment = 1  # centru

    subtitle_style = styles["Heading2"]
    subtitle_style.spaceAfter = 12

    text_style = styles["Normal"]
    text_style.spaceAfter = 8

    titles = {
        "ro": "Raport Analiza Business",
        "ru": "Отчёт бизнес-анализа"
    }

    elements.append(Spacer(1, 2 * cm))
    elements.append(Paragraph(titles[language], title_style))
    elements.append(Spacer(1, 1 * cm))



    for i, (category, img_path) in enumerate(zip(scores.keys(), image_paths)):
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
        elements.append(Image(img_path, width=14 * cm, height=10 * cm))

        # 🔹 dacă nu e ultima pagină → page break
        if i < len(image_paths) - 1:
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


async def build_user_report(user_id: int, language: str):
    scores = await get_category_scores(user_id)
    images = generate_charts(scores, language)
    pdf_path = generate_pdf(images, scores, language)
    return pdf_path
