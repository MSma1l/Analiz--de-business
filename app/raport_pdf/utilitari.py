import os  # Importam modulul os pentru lucrul cu caile de fisiere si directoare
from PyPDF2 import PdfMerger  # Importam PdfMerger pentru concatenarea mai multor fisiere PDF
from reportlab.lib.pagesizes import A4  # Importam dimensiunea paginii A4

from .constante import ASSETS_DIR  # Importam calea catre directorul assets din modulul de constante


# ==================== MERGE PDF ====================

def append_existing_pdf(generated_pdf: str, extra_pdf: str, output_pdf: str):  # Functie care concateneaza doua PDF-uri intr-unul singur
    merger = PdfMerger()  # Cream un obiect PdfMerger pentru imbinarea fisierelor PDF
    merger.append(extra_pdf)  # Adaugam primul PDF (cel de design/coperta) la merger
    merger.append(generated_pdf)  # Adaugam al doilea PDF (cel generat cu datele) la merger
    merger.write(output_pdf)  # Scriem PDF-ul rezultat in fisierul de iesire
    merger.close()  # Inchidem merger-ul si eliberam resursele


# ==================== FUNDAL PAGINI ====================

def draw_background(canvas, doc):  # Functie care deseneaza imaginea de fundal pe pagina
    bg_path = os.path.join(ASSETS_DIR, "bg.jpg")  # Construim calea catre imaginea de fundal
    if os.path.exists(bg_path):  # Verificam daca fisierul de fundal exista
        canvas.drawImage(bg_path, 0, 0, width=A4[0], height=A4[1])  # Desenam imaginea pe intreaga pagina


def draw_chart_background(canvas, doc):  # Functie care deseneaza fundalul paginilor cu grafice
    bg_charts_path = os.path.join(ASSETS_DIR, "bg_charts.jpg")  # Calea catre fundalul specific pentru grafice
    bg_path = os.path.join(ASSETS_DIR, "bg.jpg")  # Calea catre fundalul general (backup)
    if os.path.exists(bg_charts_path):  # Daca exista fundalul specific pentru grafice
        canvas.drawImage(bg_charts_path, 0, 0, width=A4[0], height=A4[1])  # Folosim fundalul pentru grafice
    elif os.path.exists(bg_path):  # Altfel, daca exista fundalul general
        canvas.drawImage(bg_path, 0, 0, width=A4[0], height=A4[1])  # Folosim fundalul general ca fallback


# ==================== HELPERS ====================

def _calc_procent(scor: int, max_scor: int) -> int:  # Functie care calculeaza procentul dintr-un scor si scorul maxim
    """
    Calculeaza procentul unui bloc.
    Daca max_scor == 0 SAU scor == 0 → returnează 0 (blocul apare cu 0%).
    """
    if max_scor <= 0 or scor <= 0:  # Daca scorul maxim sau scorul obtinut este 0 sau negativ
        return 0  # Returnam 0% pentru a evita impartirea la zero
    return int((scor / max_scor) * 100)  # Calculam si returnam procentul ca numar intreg


def _color_for_procent(procent: int) -> str:  # Functie care returneaza culoarea corespunzatoare unui procent
    """Culoare bazata STRICT pe procent: <65 rosu, 65-79 portocaliu, >=80 verde."""
    from .constante import C_GREEN_PRO, C_ORANGE_PRO, C_RED_PRO  # Importam culorile semafor din constante
    if procent >= 80:  # Daca procentul este 80% sau mai mare
        return C_GREEN_PRO  # Returnam culoarea verde (performanta buna)
    elif procent >= 65:  # Daca procentul este intre 65% si 79%
        return C_ORANGE_PRO  # Returnam culoarea portocalie (performanta medie)
    return C_RED_PRO  # Altfel returnam culoarea rosie (performanta slaba)


def _zona_for_procent(procent: int) -> str:  # Functie care determina zona de risc pe baza procentului
    """Returneaza zona de risc bazata pe procent."""
    if procent >= 80:  # Daca procentul este 80% sau mai mare
        return "minim"  # Zona de risc minim
    elif procent >= 65:  # Daca procentul este intre 65% si 79%
        return "mediu"  # Zona de risc mediu
    return "ridicat"  # Altfel zona de risc ridicat


def _short_title(categorie: str, max_len: int = 200) -> str:  # Functie care scurteaza titlul unei categorii la o lungime maxima
    titlu = categorie.split(". ", 1)[1] if ". " in categorie else categorie  # Eliminam prefixul numeric (ex: "1. ") daca exista
    return titlu if len(titlu) <= max_len else titlu[:max_len - 1] + "…"  # Returnam titlul intreg sau trunchiat cu "..." daca e prea lung
