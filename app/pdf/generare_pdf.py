import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy import select
from bd_sqlite.conexiune import async_session
from bd_sqlite.models import Raspuns, Intrebare

import os


async def get_category_scores(user_id: int):
    """
    returnează:
    {
        "Legal": 70,
        "Financiar": 40,
        ...
    }
    """
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
        if value:
            data[category]["yes"] += 1

    percentages = {}
    for cat, v in data.items():
        percentages[cat] = round(v["yes"] / v["total"] * 100)

    return percentages

def generate_charts(scores: dict):
    image_paths = []

    os.makedirs("charts", exist_ok=True)

    for category, percent in scores.items():
        plt.figure()
        plt.bar(["OK", "Probleme"], [percent, 100 - percent])
        plt.title(f"{category} – {percent}%")
        plt.ylim(0, 100)

        path = f"charts/{category}.png"
        plt.savefig(path)
        plt.close()

        image_paths.append(path)

    return image_paths

def generate_pdf(image_paths: list, scores: dict, filename="raport.pdf"):
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Raport Analiză Business", styles["Title"]))
    elements.append(Spacer(1, 20))

    for category, img_path in zip(scores.keys(), image_paths):
        text = f"{category}: {scores[category]}%"
        elements.append(Paragraph(text, styles["Heading2"]))
        elements.append(Image(img_path, width=400, height=300))
        elements.append(Spacer(1, 20))

    doc = SimpleDocTemplate(filename)
    doc.build(elements)

    return filename

async def build_user_report(user_id: int):
    scores = await get_category_scores(user_id)
    images = generate_charts(scores)
    pdf_path = generate_pdf(images, scores)
    return pdf_path
