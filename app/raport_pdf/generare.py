import os  # Importam modulul os pentru lucrul cu caile de fisiere si directoare
import re  # Importam modulul re pentru curatarea caracterelor speciale din numele fisierului
import shutil  # Importam shutil pentru copierea fisierelor PDF in folderul de arhiva
from datetime import datetime  # Importam datetime pentru a adauga data in numele fisierului PDF
from reportlab.platypus import (  # Importam componentele de layout din reportlab pentru construirea PDF-ului
    Table, TableStyle, Paragraph, Spacer,  # Table=tabel, TableStyle=stil tabel, Paragraph=paragraf, Spacer=spatiu gol
    Image, SimpleDocTemplate, PageBreak  # Image=imagine, SimpleDocTemplate=sablon document, PageBreak=salt de pagina
)
from reportlab.lib.styles import ParagraphStyle  # Importam ParagraphStyle pentru stilizarea paragrafelor
from reportlab.lib.pagesizes import A4  # Importam dimensiunea paginii A4
from reportlab.lib.units import cm  # Importam unitatea de masura centimetru
from reportlab.lib import colors  # Importam modulul de culori al reportlab

from bd_sqlite.functii_bd import get_user_results  # Importam functia care obtine rezultatele utilizatorului din baza de date

from .constante import (  # Importam constantele necesare din modulul de constante
    C_NAVY, C_STEEL, C_WHITE, C_GOLD, C_SLATE,  # Culorile principale ale temei
    C_ORANGE_PRO, C_BG_GREEN, C_BG_ORANGE, C_BG_RED,  # Culorile semafor si carduri
    ASSETS_DIR, MAIN_W, MARGIN,  # Calea assets, dimensiunile paginii
)
from .utilitari import (  # Importam functiile helper din modulul de utilitari
    append_existing_pdf, draw_chart_background,  # Functia de merge PDF si de fundal grafice
    _calc_procent, _zona_for_procent,  # Functia de calcul procent si zona risc
)
from .componente import _header_block, _section_bar  # Importam componentele de layout (header si bara sectiune)
from .grafice import (  # Importam functiile de generare grafice
    generate_chart_bytes, _donut_nivel_bytes,  # Functia de generare donut individual si donut nivel
    _build_variants_block, _build_donut_pages,  # Functia de variante explicative si pagini donut
)


# ==================== GENERARE PDF ====================

async def generate_pdf(user_id: int, language: str, filename="raport.pdf"):  # Functie asincrona principala care genereaza PDF-ul cu raportul

    if language == "ro":  # Daca limba selectata este romana
        titlu_doc     = "Raport de Evaluare a Riscului"  # Titlul documentului in romana
        subtitlu_doc  = "Analiză detaliată pe categorii  ·  BizzCheck"  # Subtitlul documentului in romana
        titlu_general = "  Scor General pe Categorii"  # Titlul sectiunii generale in romana
        bloc_prefix   = "Bloc"  # Prefixul pentru numerotarea blocurilor in romana
    else:  # Daca limba selectata este rusa
        titlu_doc     = "Отчёт об оценке рисков"  # Titlul documentului in rusa
        subtitlu_doc  = "Детальный анализ по категориям  ·  BizzCheck"  # Subtitlul documentului in rusa
        titlu_general = "  Общий результат по категориям"  # Titlul sectiunii generale in rusa
        bloc_prefix   = "Блок"  # Prefixul pentru numerotarea blocurilor in rusa

    elements = []  # Initializam lista de elemente de layout ale PDF-ului
    elements.append(Spacer(1, 0.5 * cm))  # Adaugam spatiu gol de 0.5 cm la inceputul paginii
    elements.append(_header_block(titlu_doc, subtitlu_doc))  # Adaugam blocul header cu titlul si subtitlul
    elements.append(Spacer(1, 0.55 * cm))  # Adaugam spatiu dupa header

    results_dict = await get_user_results(user_id)  # Obtinem rezultatele utilizatorului din baza de date (apel asincron)

    if not results_dict:  # Daca nu exista rezultate pentru utilizator
        no_data_style = ParagraphStyle(  # Definim stilul pentru mesajul de lipsa date
            "ND", fontName="DejaVu", fontSize=13,  # Font regular, dimensiune 13 (marit de la 10 pentru vizibilitate pe telefon)
            textColor=colors.HexColor(C_NAVY)  # Text albastru inchis
        )
        no_data = ("Nu există rezultate disponibile."  # Mesajul in romana
                   if language == "ro" else "Нет доступных результатов.")  # Sau in rusa daca limba e rusa
        elements.append(Paragraph(no_data, no_data_style))  # Adaugam mesajul de lipsa date la elemente
    else:  # Daca exista rezultate
        # ---- TOATE blocurile intra in raport, inclusiv scor=0 ----
        raport = [  # Construim lista de tupluri cu datele fiecarui bloc
            (cat, d["scor"], d["max_scor"], d["nivel"])  # Tuplu: (categorie, scor, scor_maxim, nivel)
            for cat, d in results_dict.items()  # Iteram prin dictionarul de rezultate
        ]

        elements.append(_section_bar(titlu_general))  # Adaugam bara de sectiune cu titlul general
        elements.append(Spacer(1, 0.4 * cm))  # Adaugam spatiu dupa bara de sectiune

        # Media include TOATE blocurile; cele cu scor=0 contribuie cu 0%
        procente_all = [_calc_procent(scor, max_scor) for _, scor, max_scor, _ in raport]  # Calculam procentul pentru fiecare bloc
        procent_mediu = int(sum(procente_all) / len(procente_all)) if procente_all else 0  # Calculam media aritmetica a procentelor

        # ---- Pagini cu donuts: 4 per pagina, 2 coloane x 2 randuri, 8x8 cm ----
        for el in _build_donut_pages(raport, titlu_doc, subtitlu_doc,  # Iteram prin elementele paginilor cu grafice donut
                                     titlu_general, bloc_prefix,
                                     procent_mediu, language):
            elements.append(el)  # Adaugam fiecare element la lista principala

        # ==================== VARIANTE EXPLICATIVE (DUPA TOATE DONUTS) ====================
        elements.append(PageBreak())  # Adaugam salt de pagina inainte de sectiunea cu variante
        elements.append(Spacer(1, 0.5 * cm))  # Spatiu gol de 0.5 cm
        elements.append(_header_block(titlu_doc, subtitlu_doc))  # Adaugam header-ul paginii
        elements.append(Spacer(1, 0.45 * cm))  # Spatiu dupa header

        titlu_variants = "  Scor general" if language == "ro" else "  Интерпретация общего результата"  # Titlul sectiunii de variante in functie de limba
        elements.append(_section_bar(titlu_variants))  # Adaugam bara de sectiune cu titlul variantelor
        elements.append(Spacer(1, 0.4 * cm))  # Spatiu dupa bara de sectiune

        # ---- Donut simplu centrat cu scorul mediu general ----
        buf_general = generate_chart_bytes(procent_mediu, 100, "", "", language)  # Generam graficul donut cu scorul mediu general
        donut_general_img = Image(buf_general, width=9.0 * cm, height=9.0 * cm)  # Cream obiectul imagine de 9x9 cm (marit pentru vizibilitate pe telefon)

        donut_center_tbl = Table([[donut_general_img]], colWidths=[MAIN_W])  # Cream tabelul pentru centrarea donut-ului
        donut_center_tbl.setStyle(TableStyle([  # Aplicam stilul de centrare
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),  # Aliniere orizontala centrata
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),  # Aliniere verticala la mijloc
            ("TOPPADDING",    (0, 0), (-1, -1), 0),  # Fara padding sus
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),  # Fara padding jos
        ]))
        elements.append(donut_center_tbl)  # Adaugam tabelul cu donut-ul centrat
        elements.append(Spacer(1, 0.5 * cm))  # Spatiu dupa donut

        for el in _build_variants_block(procent_mediu, language):  # Iteram prin elementele blocului de variante explicative
            elements.append(el)  # Adaugam fiecare element

        # ==================== GRUPARE RISC PE PROCENT ====================
        grupe_risc = {"minim": [], "mediu": [], "ridicat": []}  # Initializam dictionarul de grupare pe zone de risc
        for cat, scor, max_scor, nivel in raport:  # Iteram prin fiecare bloc din raport
            procent = _calc_procent(scor, max_scor)  # Calculam procentul blocului
            zona    = _zona_for_procent(procent)  # Determinam zona de risc pe baza procentului
            print(f"[DEBUG] {cat[:40]} scor={scor} max={max_scor} procent={procent}% nivel_bd={nivel} zona={zona}")  # Afisam informatii de debug in consola
            grupe_risc[zona].append((cat, scor, max_scor, nivel))  # Adaugam blocul in zona corespunzatoare

        config_risc = {  # Definim configuratia pentru fiecare zona de risc
            "ridicat": {  # Configuratia pentru riscul ridicat
                "card_color": C_BG_RED,  # Culoarea cardului: rosu
                "ro": {  # Texte in romana
                    "titlu":    "  Zone cu risc ridicat",  # Titlul sectiunii
                    "mesaj_fn": lambda p: f"Performanța actuală: {p}% din nivelul ideal.",  # Functia care genereaza mesajul cu procentul
                    "sub":      "Aceste blocuri necesită intervenție imediată.",  # Subtitlul
                },
                "ru": {  # Texte in rusa
                    "titlu":    "  Зоны высокого риска ",  # Titlul sectiunii in rusa
                    "mesaj_fn": lambda p: f"Текущий результат: {p}% от идеального уровня.",  # Functia mesajului in rusa
                    "sub":      "Эти блоки требуют немедленного вмешательства.",  # Subtitlul in rusa
                },
            },
            "mediu": {  # Configuratia pentru riscul mediu
                "card_color": C_BG_ORANGE,  # Culoarea cardului: portocaliu
                "ro": {  # Texte in romana
                    "titlu":    "  Zone în dezvoltare ",  # Titlul sectiunii
                    "mesaj_fn": lambda p: f"Sunteți la {p}% distanță de afacerea perfectă.",  # Functia mesajului
                    "sub":      "Există oportunități clare de îmbunătățire.",  # Subtitlul
                },
                "ru": {  # Texte in rusa
                    "titlu":    "  Зоны развития ",  # Titlul sectiunii in rusa
                    "mesaj_fn": lambda p: f"Вы на {p}% пути к идеальному бизнесу.",  # Functia mesajului in rusa
                    "sub":      "Есть чёткие возможности для улучшения.",  # Subtitlul in rusa
                },
            },
            "minim": {  # Configuratia pentru riscul minim
                "card_color": C_BG_GREEN,  # Culoarea cardului: verde
                "ro": {  # Texte in romana
                    "titlu":    "  Zone cu performanță înaltă ",  # Titlul sectiunii
                    "mesaj_fn": lambda p: f"Ați atins {p}% din vârful ideal de performanță.",  # Functia mesajului
                    "sub":      "Aceste blocuri funcționează excelent. Mențineți direcția.",  # Subtitlul
                },
                "ru": {  # Texte in rusa
                    "titlu":    "  Зоны высокой эффективности ",  # Titlul sectiunii in rusa
                    "mesaj_fn": lambda p: f"Вы достигли {p}% от идеального пика эффективности.",  # Functia mesajului in rusa
                    "sub":      "Эти блоки работают отлично. Сохраняйте курс.",  # Subtitlul in rusa
                },
            },
        }

        card_mesaj_style = ParagraphStyle(  # Definim stilul pentru mesajul principal al cardului de risc
            "CardMesaj", fontName="DejaVu-Bold", fontSize=16,  # Font bold, dimensiune 16 (marit de la 14 pentru vizibilitate pe telefon)
            textColor=colors.HexColor(C_WHITE), leading=22, alignment=0, spaceAfter=6,  # Text alb, aliniat la stanga, spatiere 22
        )
        card_sub_style = ParagraphStyle(  # Definim stilul pentru subtitlul cardului de risc
            "CardSub", fontName="DejaVu", fontSize=13,  # Font regular, dimensiune 13 (marit de la 11 pentru vizibilitate pe telefon)
            textColor=colors.HexColor("#E8E8E8"), leading=18, alignment=0, spaceAfter=8,  # Text gri deschis, spatiere 18
        )
        cat_item_style = ParagraphStyle(  # Definim stilul pentru elementele listei de categorii din card
            "CatItem", fontName="DejaVu-Bold", fontSize=12,  # Font bold, dimensiune 12 (marit de la 10 pentru vizibilitate pe telefon)
            textColor=colors.HexColor(C_WHITE), leading=17, alignment=0,  # Text alb, aliniat la stanga, spatiere 17
        )

        for nivel_key in ["ridicat", "mediu", "minim"]:  # Iteram prin zonele de risc in ordinea: ridicat, mediu, minim
            categorii_nivel = grupe_risc[nivel_key]  # Obtinem lista de categorii pentru zona curenta
            if not categorii_nivel:  # Daca nu exista categorii in aceasta zona
                continue  # Trecem la zona urmatoare

            cfg        = config_risc[nivel_key]  # Obtinem configuratia pentru zona curenta
            lang_cfg   = cfg[language]  # Obtinem textele in limba selectata
            card_color = cfg["card_color"]  # Obtinem culoarea cardului

            procente_nivel = [_calc_procent(scor, max_scor) for _, scor, max_scor, _ in categorii_nivel]  # Calculam procentele pentru toate categoriile din zona
            procent_nivel = int(sum(procente_nivel) / len(procente_nivel)) if procente_nivel else 0  # Calculam media procentelor din zona
            mesaj_text    = lang_cfg["mesaj_fn"](procent_nivel)  # Generam mesajul cu procentul mediu al zonei

            elements.append(PageBreak())  # Adaugam salt de pagina pentru fiecare zona de risc
            elements.append(Spacer(1, 0.5 * cm))  # Spatiu gol de 0.5 cm
            elements.append(_header_block(titlu_doc, subtitlu_doc))  # Adaugam header-ul paginii
            elements.append(Spacer(1, 0.45 * cm))  # Spatiu dupa header
            elements.append(_section_bar(lang_cfg["titlu"]))  # Adaugam bara de sectiune cu titlul zonei de risc
            elements.append(Spacer(1, 0.4 * cm))  # Spatiu dupa bara de sectiune

            buf_nivel = _donut_nivel_bytes(procent_nivel, card_color)  # Generam graficul donut pentru zona de risc
            donut_img = Image(buf_nivel, width=8.5 * cm, height=8.5 * cm)  # Cream obiectul imagine de 8.5x8.5 cm (marit pentru vizibilitate pe telefon)

            lista_cat = [Spacer(1, 0.55 * cm)]  # Initializam lista de elemente din partea dreapta a cardului
            lista_cat.append(Paragraph(mesaj_text, card_mesaj_style))  # Adaugam mesajul principal
            lista_cat.append(Spacer(1, 0.18 * cm))  # Spatiu mic
            lista_cat.append(Paragraph(lang_cfg["sub"], card_sub_style))  # Adaugam subtitlul
            lista_cat.append(Spacer(1, 0.28 * cm))  # Spatiu inainte de lista de categorii

            for cat, scor, max_scor, nivel in categorii_nivel:  # Iteram prin categoriile din zona curenta
                full_title = cat.split(". ", 1)[1] if ". " in cat else cat  # Extragem titlul fara prefixul numeric
                bloc_idx   = next(  # Gasim indexul blocului in raportul complet
                    (i + 1 for i, (c, _, _, _) in enumerate(raport) if c == cat), "?"  # Cautam pozitia categoriei in lista de raport
                )
                procent_cat = _calc_procent(scor, max_scor)  # Calculam procentul categoriei
                lista_cat.append(  # Adaugam elementul de lista cu informatiile categoriei
                    Paragraph(
                        f"— {bloc_prefix} {bloc_idx}:  {full_title}  ({procent_cat}%)",  # Formatam textul: prefix, index, titlu, procent
                        cat_item_style  # Aplicam stilul elementului de lista
                    )
                )
                lista_cat.append(Spacer(1, 0.08 * cm))  # Spatiu mic intre elementele listei
            lista_cat.append(Spacer(1, 0.55 * cm))  # Spatiu gol la sfarsitul listei

            LEFT_W  = MAIN_W * 0.38  # Latimea coloanei din stanga (38% pentru donut)
            RIGHT_W = MAIN_W * 0.62  # Latimea coloanei din dreapta (62% pentru lista de categorii)

            layout_tbl = Table([[donut_img, lista_cat]], colWidths=[LEFT_W, RIGHT_W])  # Cream tabelul cu doua coloane: donut si lista
            layout_tbl.setStyle(TableStyle([  # Aplicam stilul cardului
                ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(card_color)),  # Fundalul cardului in culoarea zonei de risc
                ("ALIGN",         (0, 0), (0, 0),   "CENTER"),  # Aliniere centrata pentru coloana cu donut
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),  # Aliniere verticala la mijloc
                ("ALIGN",         (1, 0), (1, 0),   "LEFT"),  # Aliniere la stanga pentru coloana cu lista
                ("LEFTPADDING",   (0, 0), (0, 0),   12),  # Padding stanga pentru coloana cu donut
                ("RIGHTPADDING",  (0, 0), (0, 0),   12),  # Padding dreapta pentru coloana cu donut
                ("LEFTPADDING",   (1, 0), (1, 0),   20),  # Padding stanga pentru coloana cu lista
                ("RIGHTPADDING",  (1, 0), (1, 0),   16),  # Padding dreapta pentru coloana cu lista
                ("TOPPADDING",    (0, 0), (-1, -1), 0),  # Fara padding sus
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),  # Fara padding jos
                ("LINEABOVE",     (0, 0), (-1, 0),  2, colors.HexColor(C_GOLD)),  # Linie aurie decorativa deasupra cardului
                ("LINEBELOW",     (0, -1),(-1, -1), 2, colors.HexColor(C_GOLD)),  # Linie aurie decorativa dedesubtul cardului
                ("LINEAFTER",     (0, 0), (0, -1),  1, colors.HexColor("#FFFFFF50")),  # Linie semi-transparenta intre cele doua coloane
            ]))
            elements.append(layout_tbl)  # Adaugam cardul la lista de elemente
            elements.append(Spacer(1, 0.4 * cm))  # Spatiu dupa card

    doc = SimpleDocTemplate(  # Cream sablonul documentului PDF
        filename,  # Numele fisierului de iesire
        pagesize=A4,  # Dimensiunea paginii A4
        rightMargin=MARGIN,  # Marginea dreapta
        leftMargin=MARGIN,  # Marginea stanga
        topMargin=1.0 * cm,  # Marginea de sus de 1 cm
        bottomMargin=1.0 * cm  # Marginea de jos de 1 cm
    )
    doc.build(  # Construim documentul PDF din lista de elemente
        elements,  # Lista cu toate elementele de layout
        onFirstPage=draw_chart_background,  # Functia de desenare a fundalului pe prima pagina
        onLaterPages=draw_chart_background  # Functia de desenare a fundalului pe paginile urmatoare
    )
    return filename  # Returnam numele fisierului PDF generat


# ==================== FOLDER RAPOARTE ====================

# Calea catre folderul unde se salveaza toate rapoartele PDF ale utilizatorilor
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Obtine calea catre directorul app/
RAPOARTE_DIR = os.path.join(BASE_DIR, "data", "rapoarte")  # Folderul dedicat pentru rapoarte: app/data/rapoarte/
os.makedirs(RAPOARTE_DIR, exist_ok=True)  # Cream folderul daca nu exista (inclusiv subdirectoare)


def _safe_filename(text: str) -> str:  # Functie care curata un text pentru a fi folosit in numele fisierului
    if not text:  # Daca textul este gol sau None
        return "unknown"  # Returnam "unknown" ca valoare implicita
    clean = re.sub(r'[^\w\-]', '_', text)  # Inlocuim toate caracterele speciale cu underscore (pastram litere, cifre, -, _)
    return clean[:30]  # Limitam la 30 de caractere pentru a evita nume de fisier prea lungi


# ==================== BUILD RAPORT FINAL ====================

async def build_user_report(user_id: int, language: str,  # Functie asincrona care construieste raportul final complet
                            username: str = "", first_name: str = ""):  # Parametri optionali: username si prenumele utilizatorului
    temp_pdf   = await generate_pdf(user_id, language, filename="temp_report.pdf")  # Generam PDF-ul cu datele utilizatorului intr-un fisier temporar
    design_pdf = os.path.join(ASSETS_DIR, f"pdf{'ro' if language == 'ro' else 'ru'}.pdf")  # Construim calea catre PDF-ul de design (coperta) in functie de limba

    # --- PDF pentru utilizator (trimis in Telegram cu nume generic frumos) ---
    send_pdf = "BIZCHECK_RAPORT.pdf"  # Numele fisierului care se trimite utilizatorului in Telegram
    append_existing_pdf(temp_pdf, design_pdf, send_pdf)  # Concatenam PDF-ul de design cu cel generat

    # --- Copie in folderul rapoarte (cu ID-ul din BD, username si prenumele) ---
    data_azi      = datetime.now().strftime("%Y-%m-%d")  # Obtinem data curenta in formatul AAAA-LL-ZZ
    safe_username = _safe_filename(username)  # Curatam username-ul de caractere speciale
    safe_first    = _safe_filename(first_name)  # Curatam prenumele de caractere speciale
    arhiva_name   = f"raport_{user_id}_{safe_username}_{safe_first}_{data_azi}.pdf"  # Construim numele: raport_5_ion_popescu_Ion_2026-03-04.pdf
    arhiva_pdf    = os.path.join(RAPOARTE_DIR, arhiva_name)  # Calea completa catre copia din folderul rapoarte

    shutil.copy2(send_pdf, arhiva_pdf)  # Copiem PDF-ul final in folderul rapoarte cu numele personalizat

    # Stergem fisierul temporar dupa merge
    if os.path.exists(temp_pdf):  # Verificam daca fisierul temporar exista
        os.remove(temp_pdf)  # Stergem fisierul temporar pentru a nu ocupa spatiu

    return send_pdf  # Returnam calea catre PDF-ul care se trimite utilizatorului (cu nume generic)
