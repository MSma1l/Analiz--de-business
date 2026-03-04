import io  # Importam modulul io pentru lucrul cu fluxuri de date in memorie (BytesIO)
import matplotlib.pyplot as plt  # Importam submodulul pyplot pentru crearea graficelor
from reportlab.platypus import (  # Importam componentele de layout din reportlab
    Table, TableStyle, Paragraph, Spacer, Image, PageBreak  # Componente necesare pentru constructia paginilor
)
from reportlab.lib.styles import ParagraphStyle  # Importam ParagraphStyle pentru stilizarea paragrafelor
from reportlab.lib.units import cm  # Importam unitatea de masura centimetru
from reportlab.lib import colors  # Importam modulul de culori al reportlab

from .constante import (  # Importam constantele necesare din modulul de constante
    C_NAVY, C_STEEL, C_WHITE, C_GOLD, C_SLATE,  # Culorile principale ale temei
    C_ORANGE_PRO, C_BG_GREEN, C_BG_ORANGE, C_BG_RED,  # Culorile semafor si carduri
    C_ROW_A, C_ROW_B,  # Culorile alternante pentru randuri
    MAIN_W, DONUTS_PER_PAGE, IMG_W, IMG_H, COLS, COL_W,  # Dimensiunile paginii si graficelor
)
from .utilitari import _calc_procent, _color_for_procent  # Importam functiile helper pentru calcul procent si culoare
from .componente import _header_block, _section_bar  # Importam componentele de layout (header si bara sectiune)


# ==================== GRAFICE DONUT ====================

def generate_chart_bytes(scor: int, max_scor: int, nivel: str,  # Functie care genereaza un grafic donut ca imagine PNG in memorie
                         categorie: str, language: str) -> io.BytesIO:
    """
    Donut 8x8 — culoare bazata pe PROCENT, procent in mijloc.
    Blocurile cu scor=0 sau max_scor=0 apar cu 0% (inel complet gri).
    """
    buf     = io.BytesIO()  # Cream un buffer in memorie pentru a stoca imaginea PNG
    procent = _calc_procent(scor, max_scor)  # Calculam procentul din scor si scorul maxim
    color   = _color_for_procent(procent)  # Determinam culoarea pe baza procentului

    fig, ax = plt.subplots(figsize=(3.2, 3.2), facecolor="none")  # Cream o figura matplotlib de 3.2x3.2 inch cu fundal transparent

    if procent == 0:  # Daca procentul este 0
        ax.pie(  # Desenam un grafic pie complet gri
            [100],  # O singura felie de 100%
            startangle=90,  # Incepem de la 90 de grade (sus)
            colors=["#DDE3EA"],  # Culoare gri deschis
            wedgeprops={"width": 0.30, "edgecolor": "#FFFFFF", "linewidth": 2.5},  # Grosimea inelului 0.30, contur alb
            counterclock=False  # Directia de desenare in sensul acelor de ceasornic
        )
    else:  # Daca procentul este mai mare decat 0
        ax.pie(  # Desenam graficul pie cu doua felii
            [procent, 100 - procent],  # Felie colorata (procent) si felie gri (restul)
            startangle=90,  # Incepem de la 90 de grade (sus)
            colors=[color, "#DDE3EA"],  # Culoarea procentului si gri pentru rest
            wedgeprops={"width": 0.30, "edgecolor": "#FFFFFF", "linewidth": 2.5},  # Grosimea inelului 0.30, contur alb
            counterclock=False  # Directia de desenare in sensul acelor de ceasornic
        )

    ax.text(0, 0, f"{procent}%",  # Adaugam textul cu procentul in centrul donut-ului
            ha="center", va="center",  # Aliniere orizontala si verticala centrata
            fontsize=22, fontweight="bold",  # Dimensiune font 22 (marit de la 17 pentru vizibilitate pe telefon)
            color=color, fontfamily="DejaVu Sans")  # Culoarea textului corespunde culorii donut-ului
    ax.set_aspect("equal")  # Setam raportul de aspect egal pentru a obtine un cerc perfect
    plt.tight_layout(pad=0.1)  # Ajustam layout-ul pentru a minimiza spatiul gol
    plt.savefig(buf, format="PNG", bbox_inches="tight", transparent=True, dpi=150)  # Salvam graficul in buffer ca PNG transparent la 150 DPI
    plt.close(fig)  # Inchidem figura pentru a elibera memoria
    buf.seek(0)  # Resetam pozitia in buffer la inceput pentru citire ulterioara
    return buf  # Returnam buffer-ul cu imaginea PNG


def _donut_nivel_bytes(procent: int, card_color: str) -> io.BytesIO:  # Functie care genereaza un donut pentru cardul de grupare risc
    """Donut pentru cardul de grupare — inel alb pe fond colorat, procent alb."""
    buf = io.BytesIO()  # Cream un buffer in memorie pentru imaginea PNG
    fig, ax = plt.subplots(figsize=(4.0, 4.0), facecolor="none")  # Cream o figura de 4x4 inch cu fundal transparent

    if procent == 0:  # Daca procentul este 0
        ax.pie(  # Desenam un inel complet semi-transparent
            [100],  # O singura felie de 100%
            startangle=90,  # Incepem de la 90 de grade (sus)
            colors=["#FFFFFF40"],  # Culoare alba semi-transparenta
            wedgeprops={"width": 0.32, "edgecolor": card_color, "linewidth": 2.5},  # Grosime inel 0.32, contur in culoarea cardului
            counterclock=False  # Directia de desenare in sensul acelor de ceasornic
        )
    else:  # Daca procentul este mai mare decat 0
        ax.pie(  # Desenam donut-ul cu doua felii
            [procent, 100 - procent],  # Felie alba (procent) si felie semi-transparenta (rest)
            startangle=90,  # Incepem de la 90 de grade (sus)
            colors=[C_WHITE, "#FFFFFF40"],  # Alb pentru procent, semi-transparent pentru rest
            wedgeprops={"width": 0.32, "edgecolor": card_color, "linewidth": 2.5},  # Grosime inel 0.32, contur in culoarea cardului
            counterclock=False  # Directia de desenare in sensul acelor de ceasornic
        )

    ax.text(0, 0, f"{procent}%",  # Adaugam textul cu procentul in centrul donut-ului
            ha="center", va="center",  # Aliniere centrata pe ambele axe
            fontsize=32, fontweight="bold",  # Dimensiune font 32 (marit de la 28 pentru vizibilitate pe telefon)
            color=C_WHITE, fontfamily="DejaVu Sans")  # Text alb cu fontul DejaVu Sans
    ax.set_aspect("equal")  # Setam raportul de aspect egal pentru cerc perfect
    plt.tight_layout(pad=0.3)  # Ajustam layout-ul cu padding de 0.3
    plt.savefig(buf, format="PNG", bbox_inches="tight", transparent=True, dpi=150)  # Salvam graficul in buffer ca PNG transparent
    plt.close(fig)  # Inchidem figura pentru a elibera memoria
    buf.seek(0)  # Resetam pozitia buffer-ului la inceput
    return buf  # Returnam buffer-ul cu imaginea


# ==================== BLOC VARIANTE EXPLICATIVE ====================

def _build_variants_block(procent_mediu: int, language: str) -> list:  # Functie care construieste blocul cu variantele explicative
    elements = []  # Lista goala pentru elementele de layout
    is_ro = language == "ro"  # Verificam daca limba selectata este romana

    label_style = ParagraphStyle(  # Definim stilul pentru eticheta variantei (ex: "Varianta A")
        "VarLabel", fontName="DejaVu-Bold", fontSize=11,  # Font bold, dimensiune 11 (marit de la 9 pentru vizibilitate pe telefon)
        textColor=colors.HexColor(C_STEEL), leading=15, spaceAfter=2,  # Text albastru otel, spatiere 15
    )
    text_style = ParagraphStyle(  # Definim stilul pentru textul explicativ al variantei
        "VarText", fontName="DejaVu", fontSize=13,  # Font regular, dimensiune 13 (marit de la 11 pentru vizibilitate pe telefon)
        textColor=colors.HexColor(C_SLATE), leading=18, spaceAfter=0, leftIndent=8,  # Text gri-albastru, indent stanga 8
    )

    if is_ro:  # Daca limba este romana
        variants = [  # Definim cele trei variante de interpretare in romana
            {"label": "Varianta A",  # Eticheta primei variante
             "text": f"Ați atins {procent_mediu}% din vârful ideal de performanță.",  # Textul explicativ cu procentul mediu
             "bg": "#EAF0F6", "accent": C_STEEL},  # Culoare fundal si accent
            {"label": "Varianta B",  # Eticheta celei de-a doua variante
             "text": f"Sunteți la {procent_mediu}% distanță de afacerea perfectă.",  # Textul explicativ cu procentul mediu
             "bg": "#FDF6E3", "accent": C_ORANGE_PRO},  # Culoare fundal si accent portocaliu
            {"label": "Varianta C",  # Eticheta celei de-a treia variante
             "text": f"Performanța actuală: {procent_mediu}% din nivelul ideal.",  # Textul explicativ cu procentul mediu
             "bg": "#EAF0F6", "accent": C_STEEL},  # Culoare fundal si accent
        ]
    else:  # Daca limba este rusa
        variants = [  # Definim cele trei variante de interpretare in rusa
            {"label": "Вариант A",  # Eticheta primei variante in rusa
             "text": f"Вы достигли {procent_mediu}% от идеального пика эффективности.",  # Textul explicativ in rusa
             "bg": "#EAF0F6", "accent": C_STEEL},  # Culoare fundal si accent
            {"label": "Вариант B",  # Eticheta celei de-a doua variante in rusa
             "text": f"Вы на {procent_mediu}% пути к идеальному бизнесу.",  # Textul explicativ in rusa
             "bg": "#FDF6E3", "accent": C_ORANGE_PRO},  # Culoare fundal si accent portocaliu
            {"label": "Вариант C",  # Eticheta celei de-a treia variante in rusa
             "text": f"Текущий результат: {procent_mediu}% от идеального уровня.",  # Textul explicativ in rusa
             "bg": "#EAF0F6", "accent": C_STEEL},  # Culoare fundal si accent
        ]

    elements.append(Spacer(1, 0.2 * cm))  # Adaugam un spatiu gol de 0.2 cm inainte de variante
    for v in variants:  # Iteram prin fiecare varianta
        cell_content = [  # Construim continutul celulei variantei
            Spacer(1, 0.14 * cm),  # Spatiu gol sus de 0.14 cm
            Paragraph(v["label"], label_style),  # Paragraf cu eticheta variantei
            Paragraph(v["text"], text_style),  # Paragraf cu textul explicativ
            Spacer(1, 0.14 * cm),  # Spatiu gol jos de 0.14 cm
        ]
        row_tbl = Table([[cell_content]], colWidths=[MAIN_W])  # Cream tabelul cu continutul variantei
        row_tbl.setStyle(TableStyle([  # Aplicam stilul tabelului
            ("BACKGROUND",   (0, 0), (-1, -1), colors.HexColor(v["bg"])),  # Fundalul variantei
            ("LEFTPADDING",  (0, 0), (-1, -1), 14),  # Padding stanga 14 puncte
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),  # Padding dreapta 14 puncte
            ("TOPPADDING",   (0, 0), (-1, -1), 0),  # Fara padding sus
            ("BOTTOMPADDING",(0, 0), (-1, -1), 0),  # Fara padding jos
            ("LINEBEFORE",   (0, 0), (0, -1),  4, colors.HexColor(v["accent"])),  # Linie verticala de accent in stanga
        ]))
        elements.append(row_tbl)  # Adaugam tabelul variantei la lista de elemente
        elements.append(Spacer(1, 0.14 * cm))  # Adaugam spatiu intre variante

    return elements  # Returnam lista cu toate elementele variantelor


# ==================== PAGINI CU DONUTS ====================

def _build_donut_pages(raport: list, titlu_doc: str, subtitlu_doc: str,  # Functie care construieste paginile cu grafice donut
                       titlu_general: str, bloc_prefix: str,
                       procent_mediu: int, language: str) -> list:
    """
    Construieste paginile cu donuts: 4 per pagina (2 coloane x 2 randuri), 8x8 cm.
    Prima pagina include header + section_bar + variants.
    Paginile urmatoare incep cu PageBreak + header + section_bar.
    TOATE blocurile apar, inclusiv cele cu scor=0.
    """
    elements = []  # Lista goala pentru elementele de layout ale paginilor

    bloc_num_style = ParagraphStyle(  # Definim stilul pentru numarul blocului (ex: "Bloc 1")
        "BlocNum", fontName="DejaVu-Bold", fontSize=15,  # Font bold, dimensiune 15 (marit de la 13 pentru vizibilitate pe telefon)
        textColor=colors.HexColor(C_NAVY), alignment=1, leading=20, spaceAfter=3,  # Text navy, centrat, spatiere 20
    )
    bloc_title_style = ParagraphStyle(  # Definim stilul pentru titlul blocului
        "BlocTitle", fontName="DejaVu-Bold", fontSize=11,  # Font bold, dimensiune 11 (marit de la 10 pentru vizibilitate pe telefon)
        textColor=colors.HexColor(C_STEEL), alignment=1, leading=15, spaceAfter=2,  # Text albastru otel, centrat, spatiere 15
    )

    chunks = [raport[i:i + DONUTS_PER_PAGE] for i in range(0, len(raport), DONUTS_PER_PAGE)]  # Impartim raportul in grupuri de cate 4 blocuri (DONUTS_PER_PAGE)

    for page_idx, chunk in enumerate(chunks):  # Iteram prin fiecare grup de blocuri (fiecare grup = o pagina)
        if page_idx == 0:  # Prima pagina nu necesita PageBreak (deja avem header-ul adaugat in generate_pdf)
            pass  # Nu adaugam nimic suplimentar pentru prima pagina
        else:  # Pentru paginile urmatoare
            elements.append(PageBreak())  # Adaugam salt de pagina
            elements.append(Spacer(1, 0.5 * cm))  # Spatiu gol de 0.5 cm dupa salt
            elements.append(_header_block(titlu_doc, subtitlu_doc))  # Adaugam header-ul paginii
            elements.append(Spacer(1, 0.45 * cm))  # Spatiu dupa header
            elements.append(_section_bar(titlu_general))  # Adaugam bara de sectiune cu titlul general
            elements.append(Spacer(1, 0.4 * cm))  # Spatiu dupa bara de sectiune

        gen_data = []  # Lista pentru randurile tabelului de grafice
        gen_row  = []  # Lista pentru celulele randului curent
        start_idx = page_idx * DONUTS_PER_PAGE  # Calculam indexul de start pentru numerotarea blocurilor

        for local_idx, (cat, scor, max_scor, nivel) in enumerate(chunk):  # Iteram prin fiecare bloc din grup
            g_idx      = start_idx + local_idx + 1  # Calculam numarul global al blocului (incepe de la 1)
            g_buf      = generate_chart_bytes(scor, max_scor, nivel, cat, language)  # Generam imaginea donut pentru acest bloc
            full_title = cat.split(". ", 1)[1] if ". " in cat else cat  # Extragem titlul fara prefixul numeric
            cell = [  # Construim continutul celulei pentru acest graf
                Paragraph(f"{bloc_prefix} {g_idx}", bloc_num_style),  # Numarul blocului (ex: "Bloc 1")
                Spacer(1, 0.06 * cm),  # Spatiu mic dupa numar
                Paragraph(full_title, bloc_title_style),  # Titlul categoriei
                Spacer(1, 0.08 * cm),  # Spatiu mic dupa titlu
                Image(g_buf, width=IMG_W, height=IMG_H),  # Imaginea donut 8x8 cm
                Spacer(1, 0.1 * cm),  # Spatiu mic dupa imagine
            ]
            gen_row.append(cell)  # Adaugam celula la randul curent
            if len(gen_row) == COLS:  # Daca randul are 2 coloane (COLS=2)
                gen_data.append(gen_row)  # Adaugam randul complet la tabelul de date
                gen_row = []  # Resetam randul curent

        if gen_row:  # Daca ultimul rand este incomplet (un singur grafic)
            while len(gen_row) < COLS:  # Completam cu spatii goale pana la numarul de coloane
                gen_row.append(Spacer(COL_W, IMG_H))  # Adaugam un spatiu gol de dimensiunea unei coloane
            gen_data.append(gen_row)  # Adaugam randul completat

        row_styles = []  # Lista pentru stilurile de fundal alternativ ale randurilor
        for i in range(len(gen_data)):  # Iteram prin fiecare rand
            bg = C_ROW_A if i % 2 == 0 else C_ROW_B  # Alternativa de culori: rand par = gri deschis, rand impar = alb
            row_styles.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor(bg)))  # Adaugam stilul de fundal pentru rand

        gen_tbl = Table(gen_data, colWidths=[COL_W] * COLS)  # Cream tabelul cu graficele, fiecare coloana de latime COL_W
        gen_tbl.setStyle(TableStyle([  # Aplicam stilul tabelului
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),  # Aliniere orizontala centrata
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),  # Aliniere verticala la mijloc
            ("TOPPADDING",    (0, 0), (-1, -1), 10),  # Padding sus 10 puncte
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),  # Padding jos 10 puncte
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),  # Padding stanga 6 puncte
            ("RIGHTPADDING",  (0, 0), (-1, -1), 6),  # Padding dreapta 6 puncte
            ("LINEAFTER",     (0, 0), (0, -1),  1, colors.HexColor("#C8D6E5")),  # Linie verticala separatoare intre coloane
            ("LINEBELOW",     (0, 0), (-1, -2), 1, colors.HexColor("#C8D6E5")),  # Linii orizontale separatoare intre randuri
            *row_styles,  # Aplicam stilurile de fundal alternativ
        ]))
        elements.append(gen_tbl)  # Adaugam tabelul cu grafice la lista de elemente

    return elements  # Returnam toate elementele construite
