import os  # Importam modulul os pentru lucrul cu caile de fisiere si directoare
import matplotlib  # Importam biblioteca matplotlib pentru generarea graficelor
matplotlib.use("Agg")  # Setam backend-ul matplotlib la "Agg" (fara interfata grafica, doar export in fisier)
from reportlab.lib.pagesizes import A4  # Importam dimensiunea paginii A4
from reportlab.lib.units import cm  # Importam unitatea de masura centimetru
from reportlab.pdfbase import pdfmetrics  # Importam pdfmetrics pentru inregistrarea fonturilor custom
from reportlab.pdfbase.ttfonts import TTFont  # Importam TTFont pentru incarcarea fonturilor TrueType

# ==================== FONTURI ====================
ASSETS_DIR     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")  # Construim calea catre directorul assets din folderul curent
FONT_PATH      = os.path.join(ASSETS_DIR, "DejaVuSans.ttf")  # Calea catre fontul DejaVu Sans regular
FONT_BOLD_PATH = os.path.join(ASSETS_DIR, "DejaVuSans-Bold.ttf")  # Calea catre fontul DejaVu Sans bold
pdfmetrics.registerFont(TTFont("DejaVu", FONT_PATH))  # Inregistram fontul regular sub numele "DejaVu"
try:  # Incercam sa inregistram fontul bold
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", FONT_BOLD_PATH))  # Inregistram fontul bold sub numele "DejaVu-Bold"
except Exception:  # Daca fontul bold nu exista sau e corupt
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", FONT_PATH))  # Folosim fontul regular ca inlocuitor pentru bold

# ==================== PALETA BUSINESS PREMIUM ====================
C_NAVY        = "#1C3F6E"  # Culoare albastru inchis (navy) pentru fundal header
C_STEEL       = "#2E6DA4"  # Culoare albastru otel pentru sectiuni si accente
C_WHITE       = "#FFFFFF"  # Culoare alba
C_GOLD        = "#D4A017"  # Culoare aurie pentru linii decorative si subtitluri
C_SLATE       = "#2C3E50"  # Culoare gri-albastru inchis pentru text

# Culori semafor — bazate pe PROCENT
C_GREEN_PRO   = "#1E9E5E"   # Verde — pentru procent >= 80%
C_ORANGE_PRO  = "#D4861E"   # Portocaliu — pentru procent intre 65-79%
C_RED_PRO     = "#B03030"   # Rosu — pentru procent < 65%

# Carduri grupare risc — aceleasi culori
C_BG_GREEN    = "#1E9E5E"  # Fundal verde pentru cardul de risc minim
C_BG_ORANGE   = "#C97520"  # Fundal portocaliu pentru cardul de risc mediu
C_BG_RED      = "#B03030"  # Fundal rosu pentru cardul de risc ridicat

C_ROW_A       = "#EAF0F6"  # Culoare de fundal pentru randurile pare din tabel
C_ROW_B       = "#FFFFFF"  # Culoare de fundal pentru randurile impare din tabel

# ==================== DIMENSIUNI PAGINA ====================
PAGE_W  = A4[0]  # Latimea paginii A4 in puncte
MAIN_W  = PAGE_W * 0.86  # Latimea zonei principale de continut (86% din pagina — usor marit pentru vizibilitate pe telefon)
MARGIN  = (PAGE_W - MAIN_W) / 2  # Marginea laterala calculata (centreaza continutul)

# ==================== DIMENSIUNI DONUT ====================
DONUTS_PER_PAGE = 4  # Numarul maxim de grafice donut pe o pagina
IMG_W = 8.5 * cm  # Latimea imaginii graficului donut (usor marita pentru vizibilitate pe telefon)
IMG_H = 8.5 * cm  # Inaltimea imaginii graficului donut (usor marita pentru vizibilitate pe telefon)
COLS  = 2  # Numarul de coloane pe pagina pentru grafice
COL_W = MAIN_W / COLS  # Latimea unei coloane (jumatate din zona principala)
