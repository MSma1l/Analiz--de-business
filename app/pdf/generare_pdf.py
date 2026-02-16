import io
import matplotlib
matplotlib.use("Agg")  # headless pentru Docker
import matplotlib.pyplot as plt
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfMerger

# Import funcții de bază de date
from bd_sqlite.fuction_bd import get_user_results

# ==================== FONT ====================
FONT_PATH = "pdf/assets/DejaVuSans.ttf"
pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))


# ==================== UTIL PDF ====================

def append_existing_pdf(generated_pdf: str, extra_pdf: str, output_pdf: str):
    """
    Combină două PDF-uri: design + raport generat
    """
    merger = PdfMerger()
    merger.append(extra_pdf)
    merger.append(generated_pdf)
    merger.write(output_pdf)
    merger.close()


def draw_background(canvas, doc):
    """
    Desenează background pe prima pagină (titlu)
    """
    import os
    bg_path = "pdf/assets/bg.jpg"
    if os.path.exists(bg_path):
        canvas.drawImage(bg_path, 0, 0, width=A4[0], height=A4[1])


def draw_chart_background(canvas, doc):
    """
    Desenează background pe paginile cu diagrame (pagina 3+)
    Background gradient: galben sus → alb jos
    """
    import os
    
    # Încearcă să folosești background-ul special pentru diagrame
    chart_bg_path = "pdf/assets/bg_charts.jpg"
    
    if os.path.exists(chart_bg_path):
        # Dacă ai un background special pentru diagrame
        canvas.drawImage(chart_bg_path, 0, 0, width=A4[0], height=A4[1])
    else:
        # Dacă nu, folosește background-ul standard
        bg_path = "pdf/assets/bg.jpg"
        if os.path.exists(bg_path):
            canvas.drawImage(bg_path, 0, 0, width=A4[0], height=A4[1])
        else:
            # Fallback: desenează gradient manual
            from reportlab.lib.colors import Color
            
            # Gradient de la galben la alb (ca în imagine)
            height = A4[1]
            width = A4[0]
            
            # Desenează linii pentru gradient
            for i in range(int(height)):
                # Calculează culoarea (galben → alb)
                ratio = i / height
                
                # Galben (#FFD966) → Alb (#FFFFFF)
                r = 1.0
                g = 0.85 + (0.15 * ratio)  # 0.85 → 1.0
                b = 0.4 + (0.6 * ratio)    # 0.4 → 1.0
                
                canvas.setStrokeColor(Color(r, g, b))
                canvas.setLineWidth(1)
                canvas.line(0, height - i, width, height - i)


# ==================== GRAFICE MEMORIE ====================

def generate_chart_bytes(scor: int, max_scor: int, nivel: str, categorie: str, language: str):
    """
    Generează grafic pie chart pentru o categorie în memorie
    Procent bazat pe scor/max_scor
    Culoare bazată pe nivel de risc
    """
    buf = io.BytesIO()
    
    plt.figure(figsize=(3, 3))
    
    # Calculăm procentul real
    if max_scor > 0:
        procent = int((scor / max_scor) * 100)
    else:
        procent = 0
    
    good = procent
    bad = 100 - procent
    
    # Determinăm culoarea bazată pe nivel de risc
    nivel_lower = nivel.lower()
    
    if language == "ro":
        if "ridicat" in nivel_lower or "înalt" in nivel_lower:
            color = "#ff4d4d"  # Roșu
        elif "mediu" in nivel_lower:
            color = "#ffcc00"  # Galben
        else:
            color = "#4CAF50"  # Verde
    else:  # ru
        if "высокий" in nivel_lower:
            color = "#ff4d4d"  # Roșu
        elif "средний" in nivel_lower:
            color = "#ffcc00"  # Galben
        else:
            color = "#4CAF50"  # Verde
    
    # Pie chart
    plt.pie(
        [good, bad],
        startangle=90,
        colors=[color, "#e6e6e6"],
        wedgeprops={"width": 0.3}
    )
    
    # Text în centru - afișează procentul
    plt.text(
        0, 0,
        f"{procent}%",
        ha="center",
        va="center",
        fontsize=18,
        fontweight="bold",
        color="#333333"
    )
    
    # ✅ FIX: Titlu scurt, doar partea relevantă
    # Extrage doar partea după "Blocul X. "
    if ". " in categorie:
        parts = categorie.split(". ", 1)
        if len(parts) > 1:
            titlu = parts[1]  # Ex: "Fondatori, management" sau "Учредители, управление"
        else:
            titlu = categorie
    else:
        titlu = categorie
    
    # Scurtează dacă e prea lung
    if len(titlu) > 35:
        titlu = titlu[:32] + "..."
    
    plt.title(titlu, fontsize=9, fontweight='bold', pad=10)
    plt.axis("equal")
    
    # Salvează în buffer
    plt.savefig(buf, format='PNG', bbox_inches="tight", transparent=True, dpi=100)
    plt.close()
    
    buf.seek(0)
    return buf


def generate_general_risk_chart_bytes(niveluri: list, language: str):
    """
    Generează grafic pentru riscul general
    niveluri: lista de stringuri cu niveluri de risc
    """
    buf = io.BytesIO()
    
    plt.figure(figsize=(3, 3))
    
    # Determinăm culoarea și valorile bazat pe nivelul maxim de risc
    if language == "ro":
        if any("ridicat" in n.lower() or "înalt" in n.lower() for n in niveluri):
            values, colors = [70, 30], ["#ff4d4d", "#e6e6e6"]
            label = "Risc Înalt"
        elif any("mediu" in n.lower() for n in niveluri):
            values, colors = [50, 50], ["#ffcc00", "#e6e6e6"]
            label = "Risc Mediu"
        else:
            values, colors = [30, 70], ["#1f77ff", "#e6e6e6"]
            label = "Risc Minim"
    else:  # ru
        if any("высокий" in n.lower() for n in niveluri):
            values, colors = [70, 30], ["#ff4d4d", "#e6e6e6"]
            label = "Высокий риск"
        elif any("средний" in n.lower() for n in niveluri):
            values, colors = [50, 50], ["#ffcc00", "#e6e6e6"]
            label = "Средний риск"
        else:
            values, colors = [30, 70], ["#1f77ff", "#e6e6e6"]
            label = "Минимальный риск"
    
    # Pie chart
    plt.pie(
        values,
        startangle=90,
        colors=colors,
        wedgeprops={"width": 0.3}
    )
    
    plt.text(
        0, 0,
        f"{values[0]}%",
        ha="center",
        va="center",
        fontsize=16,
        fontweight="bold"
    )
    
    plt.title(label, fontsize=10)
    plt.axis("equal")
    
    plt.savefig(buf, format='PNG', bbox_inches="tight", transparent=True)
    plt.close()
    
    buf.seek(0)
    return buf


# ==================== GENERARE PDF ====================

async def generate_pdf(user_id: int, language: str, filename="raport.pdf"):
    """
    Generează PDF-ul cu raportul complet
    
    Args:
        user_id: ID-ul utilizatorului
        language: "ro" sau "ru"
        filename: numele fișierului de output
    
    Returns:
        str: calea către fișierul PDF generat
    """
    
    # Stiluri
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleDejaVu",
        parent=styles["Title"],
        fontName="DejaVu",
        alignment=1
    )
    normal_style = ParagraphStyle(
        "NormalDejaVu",
        parent=styles["Normal"],
        fontName="DejaVu"
    )
    
    # Titlu bazat pe limbă
    titles = {
        "ro": "Raport de evaluare risc",
        "ru": "Отчет оценки риска"
    }
    
    # Elemente PDF
    elements = []
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Paragraph(titles.get(language, "Raport"), title_style))
    elements.append(Spacer(1, 0.5 * cm))
    
    # Preluare rezultate din BD
    results_dict = await get_user_results(user_id)
    
    if not results_dict:
        # Dacă nu sunt rezultate
        no_data_text = "Nu există rezultate disponibile." if language == "ro" else "Нет доступных результатов."
        elements.append(Paragraph(no_data_text, normal_style))
    else:
        # Construim raportul
        raport = [
            (categorie, data["scor"], data["max_scor"], data["nivel"])
            for categorie, data in results_dict.items()
        ]
        
        # ❌ ELIMINAT: Text raport - doar grafice
        
        # Grafice pentru categorii (2 pe rând cu spacing mai bun)
        chart_data = []
        row = []
        
        for categorie, scor, max_scor, nivel in raport:
            # Generează diagramă cu limba corectă
            buf = generate_chart_bytes(scor, max_scor, nivel, categorie, language)
            img = Image(buf, width=7 * cm, height=7 * cm)
            row.append(img)
            
            if len(row) == 2:
                chart_data.append(row)
                row = []
        
        # Completăm ultima linie dacă e nevoie
        if row:
            while len(row) < 2:
                row.append(Spacer(7 * cm, 7 * cm))
            chart_data.append(row)
        
        # Adăugăm tabelul cu grafice
        if chart_data:
            table = Table(chart_data, colWidths=[9 * cm, 9 * cm])
            table.setStyle(TableStyle([
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 15),
                ("TOPPADDING", (0, 0), (-1, -1), 15),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5)
            ]))
            elements.append(table)
        
        # Risc general
        niveluri = [nivel for _, _, _, nivel in raport]  # ✅ Fix: 4 elemente acum
        
        if language == "ro":
            if any("ridicat" in n.lower() or "înalt" in n.lower() for n in niveluri):
                general_text = "📌 Risc general: <b>Înalt</b> - acționați urgent"
            elif any("mediu" in n.lower() for n in niveluri):
                general_text = "📌 Risc general: <b>Mediu</b> - verificați periodic"
            else:
                general_text = "📌 Risc general: <b>Minim</b> - recomandat control anual"
        else:
            if any("высокий" in n.lower() for n in niveluri):
                general_text = "📌 Общий риск: <b>Высокий</b> - действовать срочно"
            elif any("средний" in n.lower() for n in niveluri):
                general_text = "📌 Общий риск: <b>Средний</b> - проверять периодически"
            else:
                general_text = "📌 Общий риск: <b>Минимальный</b> - рекомендован ежегодный контроль"
        
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(Paragraph(general_text, normal_style))
        
        # Grafic risc general
        general_buf = generate_general_risk_chart_bytes(niveluri, language)
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(Image(general_buf, width=8 * cm, height=8 * cm))
    
    # Construim PDF-ul
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm
    )
    
    # ✅ FIX: Aplică background pentru diagrame pe TOATE paginile
    # Prima pagină = titlu (bg normal)
    # Toate paginile următoare = diagrame (bg_charts)
    doc.build(
        elements,
        onFirstPage=draw_chart_background,
        onLaterPages=draw_chart_background
    )
    
    return filename


# ==================== BUILD RAPORT FINAL ====================

async def build_user_report(user_id: int, language: str):
    """
    Construiește raportul final combinând PDF-ul generat cu designul
    
    Args:
        user_id: ID-ul utilizatorului
        language: "ro" sau "ru"
    
    Returns:
        str: calea către PDF-ul final
    """
    
    # Generăm PDF-ul temporar
    temp_pdf = await generate_pdf(user_id, language, filename="temp_report.pdf")
    
    # PDF-ul cu design (paginile inițiale)
    design_pdf = f"pdf/assets/pdf{'ro' if language == 'ro' else 'ru'}.pdf"
    
    # PDF-ul final
    final_pdf = "BIZCHECK_RAPORT.pdf"
    
    # Combinăm PDF-urile
    append_existing_pdf(temp_pdf, design_pdf, final_pdf)
    
    return final_pdf