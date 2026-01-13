from fpdf import FPDF
import os
import warnings
from PIL import Image

warnings.simplefilter('ignore')


# ==================================================
# UTILITAIRE : taille image → mm
# ==================================================
def image_size_mm(path, dpi=300):
    with Image.open(path) as img:
        w_px, h_px = img.size
    mm_per_inch = 25.4
    return (
        w_px * mm_per_inch / dpi,
        h_px * mm_per_inch / dpi
    )


# ==================================================
# CLASSE PDF
# ==================================================
class PitchDeck(FPDF):
    def __init__(self):
        super().__init__(unit='mm')
        self.set_auto_page_break(auto=False)

        # --- COULEURS ---
        self.col_bg = (10, 25, 40)
        self.col_white = (255, 255, 255)
        self.col_green = (0, 220, 160)
        self.col_cyan = (0, 180, 255)

        # --- TYPOGRAPHIE ---
        self.font_title = ('Helvetica', 'B', 24)
        self.font_block_title = ('Helvetica', 'B', 16)
        self.font_body = ('Helvetica', '', 12)
        self.font_emphasis = ('Helvetica', 'B', 12)
        self.line_height = 8

        self.margin_left = 15
        self.margin_right = 15
        self.page_width_mm = 0
        self.page_height_mm = 0

    def safe_txt(self, text):
        return text.encode('latin-1', 'replace').decode('latin-1')
    
    def usable_width(self):
        return self.page_width_mm - self.margin_left - self.margin_right

    # ==================================================
    # PAGE AVEC IMAGE DE FOND (DYNAMIQUE)
    # ==================================================
    def add_page_with_background(self, image_path):
        if os.path.exists(image_path):
            w_mm, h_mm = image_size_mm(image_path)
            self.add_page(format=(w_mm, h_mm))
            self.image(image_path, x=0, y=0, w=w_mm, h=h_mm)
            self.page_width_mm = w_mm
            self.page_height_mm = h_mm
        else:
            self.add_page(format=(297, 210))
            self.page_width_mm = 297
            self.page_height_mm = 210
            self.set_fill_color(*self.col_bg)
            self.rect(0, 0, 297, 210, 'F')

    # ==================================================
    # HEADER STANDARD (BANNER)
    # ==================================================
    def draw_header(self, title):
        self.set_font(*self.font_title)
        self.set_text_color(*self.col_white)
        self.set_xy(self.margin_left, 15)
        self.cell(0, 15, self.safe_txt(title), ln=True)

    # ==================================================
    # SLIDES
    # ==================================================
    def add_slide(self, title, content_lines=[], big_stat=None):
        self.add_page_with_background("banner.png")
        self.draw_header(title)

        if big_stat:
            y = 60
            for number, text in big_stat:
                self.set_xy(20, y)
                self.set_font('Helvetica', 'B', 45)
                self.set_text_color(*self.col_green)
                self.cell(60, 20, number)

                self.set_font('Helvetica', 'B', 16)
                self.set_text_color(*self.col_white)
                self.set_xy(85, y + 5)
                self.multi_cell(0, 10, self.safe_txt(text))
                y += 40
            return

        self.set_xy(self.margin_left, 50)
        for line in content_lines:
            safe = self.safe_txt(line)
            if safe.startswith("-"):
                self.set_font(*self.font_block_title)
                self.set_text_color(*self.col_green)
                width = self.page_width_mm - self.margin_left - self.margin_right
                if width < 10:  # largeur minimale
                    width = self.usable_width()
                self.multi_cell(width, self.line_height, safe.replace("-", "").strip())
                self.ln(2)
            else:
                self.set_font(*self.font_body)
                self.set_text_color(*self.col_white)
                self.cell(5, self.line_height, ">", ln=0)
                x = self.get_x()
                width = self.page_width_mm - x - self.margin_right
                if width < 10:  # largeur minimale
                    width = self.usable_width()
                self.multi_cell(width, self.line_height, safe)


    def add_slide_solution_visual(self, title, content_lines, image_path):
        self.add_page_with_background("banner.png")
        self.draw_header(title)

        self.set_xy(self.margin_left, 50)

        for line in content_lines:
            safe = self.safe_txt(line)

            if safe.startswith("-"):
                self.set_font(*self.font_block_title)
                self.set_text_color(*self.col_green)
                self.multi_cell(
                    self.usable_width(),
                    self.line_height,
                    safe.replace("-", "").strip()
                )
                self.ln(2)
            else:
                self.set_font(*self.font_body)
                self.set_text_color(*self.col_white)
                self.cell(5, self.line_height, ">", ln=0)
                x = self.get_x()

                usable = self.page_width_mm - x - self.margin_right
                if usable > 10:
                    self.multi_cell(usable, self.line_height, safe)

        if os.path.exists(image_path):
            img_w = self.page_width_mm * 0.6
            self.image(
                image_path,
                x=(self.page_width_mm - img_w) / 2,
                y=110,
                w=img_w
            )

    def add_slide_problem_visual(self, title, blocks):
        self.add_page_with_background("banner.png")
        self.draw_header(title)

        current_y = 50
        icon_size = 30

        for icon_path, block_title, bullets in blocks:
            # Icône
            if os.path.exists(icon_path):
                self.image(icon_path, x=self.margin_left, y=current_y, w=icon_size)
            else:
                self.set_fill_color(80, 80, 80)
                self.rect(self.margin_left, current_y, icon_size, icon_size, 'F')

            text_x = self.margin_left + icon_size + 10
            self.set_xy(text_x, current_y)

            self.set_font(*self.font_block_title)
            self.set_text_color(*self.col_green)
            self.cell(0, 10, self.safe_txt(block_title), ln=True)

            self.set_font(*self.font_body)
            self.set_text_color(*self.col_white)

            for bullet in bullets:
                self.set_x(text_x)
                self.cell(5, self.line_height, ">", ln=0)
                x = self.get_x()
                usable = self.page_width_mm - x - self.margin_right
                if usable > 10:
                    self.multi_cell(usable, self.line_height, self.safe_txt(bullet))
                self.ln(1)

            current_y = max(self.get_y(), current_y + icon_size) + 10

    def add_slide_prototype(self, title, content_lines, image_path):
        self.add_page_with_background("banner.png")
        self.draw_header(title)

        self.set_xy(self.margin_left, 50)
        for line in content_lines:
            safe = self.safe_txt(line)
            if safe.startswith("-"):
                self.set_font(*self.font_block_title)
                self.set_text_color(*self.col_green)
                self.multi_cell(self.usable_width(), self.line_height, safe.replace("-", "").strip())
                self.ln(2)
            else:
                self.set_font(*self.font_body)
                self.set_text_color(*self.col_white)
                self.cell(5, self.line_height, ">", ln=0)
                x = self.get_x()
                usable = self.page_width_mm - x - self.margin_right
                if usable < 10:  # largeur minimale pour éviter l'erreur
                    usable = self.usable_width()
                self.multi_cell(usable, self.line_height, safe)

        if os.path.exists(image_path):
            img_w = self.page_width_mm * 0.6
            self.image(image_path, x=(self.page_width_mm - img_w) / 2, y=110, w=img_w)

    def add_slide_team_photos(self, title, members):
        self.add_page_with_background("banner.png")
        self.draw_header(title)

        y = 70
        photo = 35
        gap = 15
        total = len(members) * photo + (len(members) - 1) * gap
        x = (self.page_width_mm - total) / 2

        for name, role, img in members:
            if os.path.exists(img):
                self.image(img, x=x, y=y, w=photo, h=photo)
            self.set_xy(x, y + photo + 5)
            self.set_font(*self.font_emphasis)
            self.set_text_color(*self.col_green)
            self.cell(photo, 5, self.safe_txt(name), align='C', ln=True)

            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(*self.col_cyan)
            self.multi_cell(photo + 10, 8, self.safe_txt(role), align='C')
            x += photo + gap

    # ==================================================
    # COUVERTURE
    # ==================================================
    def create_cover(self):
        self.add_page_with_background("first.png")


# ==================================================
# EXÉCUTION
# ==================================================
pdf = PitchDeck()

pdf.create_cover()

# Slide 1
pdf.add_slide_solution_visual(
    "La Solution ReaKt",
    [
        "- IA prédictive",
        "Anticipe les comportements cellulaires",
        "- Pilotage automatique",
        "Action avant l’incident"
    ],
    "example.png"
)

# Slide 2 : prototype
pdf.add_slide_prototype(
    "La Preuve : Un Prototype Fonctionnel",
    [
        "- Performance Technique :",
        "Ajustement autonome des flux d'alimentation en temps réel.",
        "Prédiction des pics de biomasse avec une marge d'erreur < 2%.",
        "- Validation :",
        "Modèle entraîné sur notre simulateur de fermentation.",
    ],
    "predictions.png"
)

# Slide 3
pdf.add_slide(
    "L'Impact : Résultats de la Simulation",
    big_stat=[("+20%", "d'augmentation de la production sur un an."), ("0", "perte de lot.")]
)

# Slide 4
pdf.add_slide(
    "Vision : L'Industrie 4.0 de la Biologie",
    [
        "- Notre Mission : La Standardisation",
        "Faire passer la bioproduction du stade artisanal et incertain...",
        "...à un standard industriel reproductible, fiable et scalable.",
        "L'IA comme chef d'orchestre de la biologie.",
        "- Comment y arriver ?",
        "Proposer un logiciel affiné sur les données du client.",
        "Une solution pérene qui analyse les données du jour quotidiennement.",
    ]
)

# Slide 5
pdf.add_slide(
    "Business Plan : Une Strategie Data-First",
    [
        "- Phase 1 : Acquisition & Calibration (Gratuite)",
        "Offre : Accès gratuit pour les 2 à 3 premiers partenaires industriels.",
        "Objectif : Valider la solution sur site et lever les barrières à l'entrée.",
        "Data-Leverage : Récolte de données réelles pour affiner le Deep Learning.",
        "- Phase 2 : Transition SaaS (Abonnement)",
        "Déploiement : Une fois la PoC validée, passage au modèle récurrent.",
        "Tiering : Monitoring Standard (Alertes) vs Contrôle Premium (Autonome).",
        "Revenu : Tarif annuel par bioréacteur connecté.",
        "- Phase 3 : Success Fees (Partage de la Valeur)",
        "Performance : Commission sur le gain net de production (ex: % sur les +20%).",
        "Alignement : Intérêts de ReaKt et de l'industriel parfaitement liés.",
        "- Marchés Cibles (TAM)",
        "1. Protéines Alternatives (FoodTech) : Réduire les coûts.",
        "2. Pharmaceutique : Optimisation des rendements.",
        "3. Chimie Verte : Production durable."
    ]
)

# Slide 6
pdf.add_slide(
    "Prochaines Étapes : De la Simulation à la Réalité",
    [
        "- Consolidation de la Preuve de Concept (PoC) :", 
        "Explorations de différentes technologies.",
        "- Co-développement avec Experts Métiers :",
        "Partenariat avec des spécialistes pour affiner les paramètres biologiques.",
        "- Pilotes Industriels :",
        "Mise en place de tests sur bioréacteurs réels."
    ]
)

# Slide 7
pdf.add_slide_team_photos(
    "L'Équipe derrière ce projet",
    [
        ("Paul Chevalier", "paul.chevalier@edu.ece.fr", "paul.jpg"),
        ("Elias Moussouni", "elias.moussouni@edu.ece.fr", "mouss.jpg"),
        ("Ziyad Amzil", "ziyad.amzil@edu.ece.fr", "ziyad.jpg"),
        ("Malik Hassane", "malik.hassane@edu.ece.fr", "malik.png"),
        ("Gabriel Guiet-Dupré", "gabriel.guietdupre@edu.ece.fr", "gab.jpg")
    ]
)

pdf.output("ReaKt_Full_Deck.pdf")
print("✅ Deck généré avec images de fond !")
