from fpdf import FPDF
import os
import warnings

# On masque les avertissements rouges (DeprecationWarning) pour avoir une console propre
warnings.simplefilter('ignore')

class PitchDeck(FPDF):
    def __init__(self):
        super().__init__(orientation='L', unit='mm', format='A4')

        # --- COULEURS ---
        self.col_bg = (10, 25, 40)
        self.col_white = (255, 255, 255)
        self.col_green = (0, 220, 160)
        self.col_cyan = (0, 180, 255)
        self.col_gray = (200, 200, 200)

        # --- TYPOGRAPHIE ---
        self.font_title = ('Helvetica', 'B', 24)
        self.font_block_title = ('Helvetica', 'B', 16)
        self.font_body = ('Helvetica', '', 12)
        self.font_emphasis = ('Helvetica', 'B', 12)
        self.line_height = 8

        self.set_auto_page_break(auto=False)
        self.margin_left = 15
        self.margin_right = 15
        self.page_width_mm = 297

    def safe_txt(self, text):
        return text.encode('latin-1', 'replace').decode('latin-1')

    # --------------------------------------------------
    # HEADERS & UTILITAIRES
    # --------------------------------------------------
    def _draw_background_and_title(self, title):
        self.add_page()
        self.set_fill_color(*self.col_bg)
        self.rect(0, 0, 297, 210, 'F')

        if os.path.exists("logo.png"):
            self.image("logo.png", x=265, y=10, w=25)

        self.set_font(*self.font_title)
        self.set_text_color(*self.col_cyan)
        self.set_xy(self.margin_left, 15)
        self.cell(0, 15, self.safe_txt(title), ln=True)

        self.set_line_width(1)
        self.set_draw_color(*self.col_green)
        self.line(self.margin_left, 32, 100, 32)
        self.set_draw_color(*self.col_cyan)
        self.line(100, 32, 297 - self.margin_right, 32)

    def _draw_big_stats(self, stats):
        y_pos = 60
        for number, text in stats:
            self.set_xy(20, y_pos)
            self.set_font('Helvetica', 'B', 45)
            self.set_text_color(*self.col_green)
            self.cell(60, 20, self.safe_txt(number), ln=0)
            
            self.set_font('Helvetica', 'B', 16)
            self.set_text_color(*self.col_white)
            self.set_xy(85, y_pos + 5)
            self.multi_cell(0, 10, self.safe_txt(text))
            y_pos += 40

    # --------------------------------------------------
    # SLIDES CONTENU (Standard + Visuel)
    # --------------------------------------------------
    # CORRECTION ICI : content_lines=[] permet de rendre le texte optionnel
    def add_slide(self, title, content_lines=[], big_stat=None):
        self._draw_background_and_title(title)
        
        if big_stat:
            self._draw_big_stats(big_stat)
            return

        self.set_xy(self.margin_left, 50)
        # On vérifie qu'il y a bien du texte avant de boucler dessus
        if content_lines:
            for line in content_lines:
                safe_line = self.safe_txt(line)
                if safe_line.strip().startswith("-"):
                    self.set_font(*self.font_block_title)
                    self.set_text_color(*self.col_green)
                    usable_width = self.page_width_mm - self.margin_left - self.margin_right
                    self.set_x(self.margin_left)
                    self.multi_cell(usable_width, self.line_height, safe_line.replace("-", "").strip())
                    self.ln(2)
                else:
                    self.set_font(*self.font_body)
                    self.set_text_color(*self.col_white)
                    self.set_x(self.margin_left)
                    self.cell(5, self.line_height, ">", ln=0)
                    x = self.get_x()
                    self.multi_cell(self.page_width_mm - x - self.margin_right, self.line_height, safe_line)

    def add_slide_solution_visual(self, title, content_lines, image_path):
        self._draw_background_and_title(title)
        self.set_xy(self.margin_left, 50)
        for line in content_lines:
            safe_line = self.safe_txt(line)
            if safe_line.strip().startswith("-"):
                self.set_font(*self.font_block_title)
                self.set_text_color(*self.col_green)
                self.set_x(self.margin_left)
                self.multi_cell(0, self.line_height, safe_line.replace("-", "").strip())
                self.ln(2)
            else:
                self.set_font(*self.font_body)
                self.set_text_color(*self.col_white)
                self.set_x(self.margin_left)
                self.cell(5, self.line_height, ">", ln=0)
                x = self.get_x()
                self.multi_cell(self.page_width_mm - x - self.margin_right, self.line_height, safe_line)
        
        if os.path.exists(image_path):
            img_w = 180
            x_pos = (self.page_width_mm - img_w) / 2
            self.image(image_path, x=x_pos, y=110, w=img_w)

    def add_slide_problem_visual(self, title, blocks):
        self._draw_background_and_title(title)
        current_y = 50
        for icon_path, block_title, bullets in blocks:
            image_width = 30
            if os.path.exists(icon_path):
                self.image(icon_path, x=self.margin_left, y=current_y, w=image_width)
            else:
                self.set_fill_color(60, 60, 60)
                self.rect(self.margin_left, current_y, image_width, image_width, 'F')
            
            text_x = self.margin_left + image_width + 10
            text_width = self.page_width_mm - text_x - self.margin_right
            self.set_xy(text_x, current_y)
            self.set_font(*self.font_block_title)
            self.set_text_color(*self.col_green)
            self.cell(text_width, 10, self.safe_txt(block_title), ln=True)
            self.set_font(*self.font_body)
            self.set_text_color(*self.col_white)
            for bullet in bullets:
                self.set_x(text_x)
                self.cell(5, self.line_height, ">", ln=0)
                x = self.get_x()
                self.multi_cell(self.page_width_mm - x - self.margin_right, self.line_height, self.safe_txt(bullet))
                self.ln(1)
            current_y = max(self.get_y(), current_y + image_width) + 10

    def add_slide_prototype(self, title, content_lines, chart_path):
        self._draw_background_and_title(title)
        self.set_xy(self.margin_left, 50)
        for line in content_lines:
            safe_line = self.safe_txt(line)
            if safe_line.strip().startswith("-"):
                self.set_font(*self.font_block_title)
                self.set_text_color(*self.col_green)
                self.set_x(self.margin_left)
                self.multi_cell(0, self.line_height, safe_line.replace("-", "").strip())
                self.ln(2)
            else:
                self.set_font(*self.font_body)
                self.set_text_color(*self.col_white)
                self.set_x(self.margin_left)
                self.cell(5, self.line_height, ">", ln=0)
                x = self.get_x()
                self.multi_cell(self.page_width_mm - x - self.margin_right, self.line_height, safe_line)

        img_w = 150
        x_pos = (self.page_width_mm - img_w) / 2
        y_pos = 100
        if os.path.exists(chart_path):
            self.image(chart_path, x=x_pos, y=y_pos, w=img_w)
            
            # Légende investisseur
            self.set_xy(x_pos, y_pos + 85)
            self.set_font('Helvetica', 'B', 12)
            self.set_text_color(*self.col_cyan)
            self.multi_cell(img_w, 6, self.safe_txt("Conclusion : Corrélation > 98%. Incertitude biologique transformée en variable mathématique."), align='C')

    # --------------------------------------------------
    # SLIDE ÉQUIPE (AVEC TEXTE INVESTISSEUR)
    # --------------------------------------------------
    def add_slide_team_photos(self, title, members):
        self._draw_background_and_title(title)

        # Intro
        self.set_xy(self.margin_left, 45)
        self.set_font(*self.font_body)
        self.set_text_color(*self.col_white)
        self.multi_cell(0, self.line_height, self.safe_txt(
            "5 ingénieurs ECE Paris. Une synergie totale entre Hardware & Intelligence Artificielle."
        ))

        y = 70
        photo = 35
        gap = 15
        total_w = (len(members) * photo) + ((len(members) - 1) * gap)
        x = (self.page_width_mm - total_w) / 2
        
        current_x = x
        for name, role, img in members:
            if os.path.exists(img):
                self.image(img, x=current_x, y=y, w=photo, h=photo)
            else:
                self.set_fill_color(80, 80, 80)
                self.rect(current_x, y, photo, photo, 'F')
            
            self.set_xy(current_x, y + photo + 5)
            self.set_font(*self.font_emphasis)
            self.set_text_color(*self.col_green)
            self.cell(photo, 5, self.safe_txt(name.split()[0]), align='C', ln=True)
            self.set_x(current_x)
            self.set_font('Helvetica', 'I', 9)
            self.set_text_color(*self.col_cyan)
            self.multi_cell(photo, 4, self.safe_txt(role), align='C')
            current_x += photo + gap

        # Bloc Investisseur en bas
        self.set_xy(self.margin_left, 150)
        self.set_fill_color(15, 35, 55)
        self.rect(self.margin_left, 145, 267, 40, 'F')
        
        self.set_xy(self.margin_left + 5, 150)
        self.set_font(*self.font_block_title)
        self.set_text_color(*self.col_white)
        self.cell(0, 10, self.safe_txt("Pourquoi cette équipe va réussir ?"), ln=True)
        
        self.set_font(*self.font_body)
        self.set_x(self.margin_left + 5)
        txt_invest = (
            "• Complémentarité technique : maîtrise de l'ensemble de la chaîne technologique, du capteur physique aux algorithmes avancés d'IA et aux technologies émergentes.\n"
            "• Excellence opérationnelle : Une équipe motivée, dynamique et rigoureuse, habituée à travailler en mode Agile et à itérer rapidement pour délivrer des solutions robustes.\n"
            "• Rigueur scientifique et innovation : Une approche méthodique fondée sur la donnée, l'expérimentation et la validation par les résultats."
        )
        self.multi_cell(250, 8, self.safe_txt(txt_invest))

    def create_cover_big_logo(self):
        self.add_page()
        self.set_fill_color(*self.col_bg)
        self.rect(0, 0, 297, 210, 'F')
        if os.path.exists("logo.png"):
            self.image("logo.png", x=108, y=50, w=80)
        self.set_xy(0, 135)
        self.set_font(*self.font_title)
        self.set_text_color(*self.col_cyan)
        self.cell(297, 15, "ReaKt", align='C', ln=True)
        self.set_font(*self.font_body)
        self.set_text_color(*self.col_white)
        self.cell(297, 10, "L'IA qui anticipe la fermentation", align='C')


# ==================================================
# EXÉCUTION
# ==================================================
pdf = PitchDeck()
pdf.create_cover_big_logo()

pdf.add_slide_problem_visual(
    "Le Problème : La Fermentation est une Boîte Noire",
    [
        ("money.png", "L'Instabilité Biologique : Un Gouffre Financier",
         ["Déviations infimes = conséquences exponentielles.",
          "Coût direct de milliers d'euros par lot jeté."]),
        ("blind.png", "Le Constat : Une Gestion Réactive et Aveugle",
         ["Boîte Noire : Manque de visibilité sur l'intérieur des cellules.",
          "Pilotage dans le rétroviseur : On agit souvent trop tard."])
    ]
)

pdf.add_slide_solution_visual(
    "La Solution ReaKt : L'IA qui Anticipe",
    [
        "- Au-delà du monitoring",
        "ReaKt ne se contente pas de surveiller : il anticipe.",
        "Un véritable pilote automatique biologique.",
        "- Technologie",
        "Notre réseau de neurones prédit les comportements cellulaires complexes.",
        "Notre algorithme réagit avant même que l'incident ne soit visible."
    ],
    "example.png"
)

pdf.add_slide(
    "Vision : L'Industrie 4.0 de la Biologie",
    [
        "- Notre Mission : La Standardisation",
        "Faire passer la bioproduction du stade artisanal et incertain...",
        "...à un standard industriel reproductible, fiable et scalable.",
        "L'IA comme chef d'orchestre de la biologie.",
        "- Marchés Cibles (TAM)",
        "1. Protéines Alternatives (FoodTech) : Réduire les coûts.",
        "2. Pharmaceutique : Optimisation des rendements.",
        "3. Chimie Verte : Production durable."
    ]
)

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

# C'EST ICI QUE CA PLANTAIT AVANT (maintenant c'est corrigé)
pdf.add_slide("L'Impact : Résultats de la Simulation", big_stat=[("+20%", "d'augmentation de la production sur un an."), ("0", "perte de lot détectée.")])

pdf.add_slide("Prochaines Étapes : Du Modèle à la Réalité", [
    "- Consolidation de la Preuve de Concept (PoC) :", 
    "Transition de notre modèle IA vers une validation concrète sur données physiques.",
    "- Co-développement avec Experts Métiers :",
    "Partenariat avec des spécialistes pour affiner les paramètres biologiques.",
    "- Pilotes Industriels :",
    "Mise en place de tests sur bioréacteurs réels."
])

pdf.add_slide_team_photos(
    "L'Équipe : L'Alliance Hardware & Software",
    [
        ("Paul Chevalier", "IA & Data", "paul.png"),
        ("Elias Moussouni", "IA & Data", "mouss.png"),
        ("Ziyad Amzil", "IA & Data", "ziyad.png"),
        ("Malik Hassane", "Systèmes embarqués", "malik.png"),
        ("Gabriel Guiet-Dupre", "Systèmes embarqués", "gab.png")
    ]
)

pdf.add_slide(
    "Contactez-nous",
    ["- gabriel.guietdupre@edu.ece.fr", "- Mousslapuenta sur Snap pour les meufs"]
)

pdf.output("ReaKt_Full_Deck.pdf")
print("✅ Deck généré sans erreurs !")
