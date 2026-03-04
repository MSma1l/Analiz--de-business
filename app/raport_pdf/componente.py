from reportlab.platypus import Table, TableStyle, Paragraph, Spacer  # Importam componentele de layout din reportlab
from reportlab.lib.styles import ParagraphStyle  # Importam ParagraphStyle pentru stilizarea paragrafelor
from reportlab.lib.units import cm  # Importam unitatea de masura centimetru
from reportlab.lib import colors  # Importam modulul de culori al reportlab

from .constante import C_NAVY, C_WHITE, C_GOLD, C_STEEL, MAIN_W  # Importam constantele de culoare si dimensiune


# ==================== COMPONENTE LAYOUT ====================

def _header_block(titlu_doc: str, subtitlu_doc: str) -> Table:  # Functie care construieste blocul de header al paginii
    title_style = ParagraphStyle(  # Definim stilul pentru titlul principal
        "HdrTitle", fontName="DejaVu-Bold", fontSize=22,  # Font bold, dimensiune 22 (marit pentru vizibilitate pe telefon)
        textColor=colors.HexColor(C_WHITE), alignment=1, leading=30, spaceAfter=4,  # Text alb, centrat, spatiere intre linii 30
    )
    sub_style = ParagraphStyle(  # Definim stilul pentru subtitlu
        "HdrSub", fontName="DejaVu", fontSize=11,  # Font regular, dimensiune 11 (marit de la 9 pentru vizibilitate pe telefon)
        textColor=colors.HexColor(C_GOLD), alignment=1, leading=16,  # Text auriu, centrat, spatiere 16
    )
    cell = [  # Construim continutul celulei header-ului
        Spacer(1, 0.5 * cm),  # Spatiu gol sus de 0.5 cm
        Paragraph(titlu_doc, title_style),  # Paragraf cu titlul documentului
        Spacer(1, 0.1 * cm),  # Spatiu mic intre titlu si subtitlu
        Paragraph(subtitlu_doc, sub_style),  # Paragraf cu subtitlul documentului
        Spacer(1, 0.5 * cm),  # Spatiu gol jos de 0.5 cm
    ]
    tbl = Table([[cell]], colWidths=[MAIN_W])  # Cream tabelul cu o singura celula de latimea zonei principale
    tbl.setStyle(TableStyle([  # Aplicam stilul tabelului
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(C_NAVY)),  # Fundal albastru inchis
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),  # Aliniere orizontala centrata
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),  # Aliniere verticala la mijloc
        ("LEFTPADDING",   (0, 0), (-1, -1), 24),  # Padding stanga 24 puncte
        ("RIGHTPADDING",  (0, 0), (-1, -1), 24),  # Padding dreapta 24 puncte
        ("TOPPADDING",    (0, 0), (-1, -1), 0),  # Fara padding sus
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),  # Fara padding jos
        ("LINEBELOW",     (0, 0), (-1, -1), 3, colors.HexColor(C_GOLD)),  # Linie aurie decorativa dedesubt de 3 puncte grosime
    ]))
    return tbl  # Returnam tabelul header


def _section_bar(text: str) -> Table:  # Functie care construieste o bara de sectiune cu titlu
    style = ParagraphStyle(  # Definim stilul textului din bara de sectiune
        "SecBar", fontName="DejaVu-Bold", fontSize=13,  # Font bold, dimensiune 13 (marit de la 11 pentru vizibilitate pe telefon)
        textColor=colors.HexColor(C_WHITE), alignment=0, leading=18,  # Text alb, aliniat la stanga, spatiere 18
    )
    tbl = Table([[Paragraph(text, style)]], colWidths=[MAIN_W])  # Cream tabelul cu textul sectiunii
    tbl.setStyle(TableStyle([  # Aplicam stilul barei de sectiune
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor(C_STEEL)),  # Fundal albastru otel
        ("LEFTPADDING",   (0, 0), (-1, -1), 16),  # Padding stanga 16 puncte
        ("RIGHTPADDING",  (0, 0), (-1, -1), 16),  # Padding dreapta 16 puncte
        ("TOPPADDING",    (0, 0), (-1, -1), 8),  # Padding sus 8 puncte
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),  # Padding jos 8 puncte
        ("LINEBEFORE",    (0, 0), (0, -1),  5, colors.HexColor(C_GOLD)),  # Linie aurie verticala in stanga de 5 puncte grosime
    ]))
    return tbl  # Returnam bara de sectiune
