from fpdf import FPDF
import os

class PitchDeck(FPDF):
    def __init__(self):
        super().__init__(orientation='L', unit='mm', format='A4')
        # --- COULEURS CHARTE ---
        self.col_bg = (10, 25, 40)       # Bleu Nuit Profond
        self.col_white = (255, 255, 255) # Blanc
        self.col_green = (0, 220, 160)   # Vert Émeraude
        self.col_cyan = (0, 180, 255)    # Bleu Cyan
        self.col_gray = (200, 200, 200)  # Gris clair
        
        self.set_auto_page_break(auto=False)
        self.margin_left = 15
        self.margin_right = 15
        self.page_width_mm = 297

    def safe_txt(self, text):
         return text.encode('latin-1', 'replace').decode('latin-1')

    def _draw_background_and_title(self, title):
        self.add_page()
        # Fond
        self.set_fill_color(*self.col_bg)
        self.rect(0, 0, 297, 210, 'F')
        
        # Petit logo
        if os.path.exists("logo.png"):
            self.image("logo.png", x=265, y=10, w=25)

        # Titre de la slide
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(*self.col_cyan)
        self.set_xy(self.margin_left, 15)
        self.cell(0, 15, self.safe_txt(title), ln=True)
        
        # Ligne séparation décorative
        self.set_line_width(1)
        self.set_draw_color(*self.col_green)
        self.line(self.margin_left, 32, 100, 32)
        self.set_draw_color(*self.col_cyan)
        self.line(100, 32, 297-self.margin_right, 32)

    # --- MÉTHODE SOLUTION HARMONISÉE AVEC LA SLIDE PROBLÈME ---
    def add_slide_solution_visual(self, title, content_lines, image_path):
        self._draw_background_and_title(title)
        
        self.set_xy(self.margin_left, 42)
        
        for line in content_lines:
            safe_line = self.safe_txt(line)
            
            # Gestion des titres de blocs (commençant par •)
            if line.strip().startswith("•"):
                self.ln(2)
                self.set_font('Helvetica', 'B', 16) # Même taille que slide problème
                self.set_text_color(*self.col_green)
                # text_clean = safe_line.replace("•", "").strip()
                self.multi_cell(0, 8, safe_line)
                self.set_text_color(*self.col_white)
            
            # Gestion des sous-puces (commençant par -)
            elif line.strip().startswith("-"):
                self.set_font('Helvetica', '', 12) # Même taille que slide problème
                self.set_x(self.margin_left + 5)
                self.cell(5, 8, ">", ln=0)
                current_x = self.get_x()
                self.multi_cell(self.page_width_mm - current_x - self.margin_right, 8, safe_line.replace("-", "").strip())
            
            else:
                self.set_font('Helvetica', '', 13)
                self.set_x(self.margin_left)
                self.multi_cell(0, 8, safe_line)
        
        # Image en grand en bas
        if os.path.exists(image_path):
            img_w = 180
            x_pos = (self.page_width_mm - img_w) / 2
            self.image(image_path, x=x_pos, y=105, w=img_w)

    def add_slide_problem_visual(self, title, blocks):
        self._draw_background_and_title(title)
        current_y = 50
        for icon_path, block_title, bullets in blocks:
            image_width = 30
            if os.path.exists(icon_path):
                self.image(icon_path, x=self.margin_left, y=current_y, w=image_width)
            else:
                self.set_fill_color(50, 50, 50)
                self.rect(self.margin_left, current_y, image_width, image_width, 'F')
            
            text_x_start = self.margin_left + image_width + 10
            text_width = self.page_width_mm - text_x_start - self.margin_right
            self.set_xy(text_x_start, current_y)
            self.set_font('Helvetica', 'B', 16)
            self.set_text_color(*self.col_green)
            self.cell(text_width, 10, self.safe_txt(block_title), ln=True)
            self.set_text_color(*self.col_white)
            self.set_font('Helvetica', '', 12)
            for bullet in bullets:
                self.set_x(text_x_start)
                self.cell(5, 8, ">", ln=0)
                current_x = self.get_x()
                self.multi_cell(self.page_width_mm - current_x - self.margin_right, 8, self.safe_txt(bullet))
                self.ln(1)
            y_after_text = self.get_y()
            y_after_image = current_y + image_width + 5
            current_y = max(y_after_text, y_after_image) + 10

    def create_cover_big_logo(self):
        self.add_page()
        self.set_fill_color(*self.col_bg)
        self.rect(0, 0, 297, 210, 'F')
        img_width = 150
        x_pos = (297 - img_width) / 2
        y_pos = 30
        if os.path.exists("logo.png"):
            self.image("logo.png", x=x_pos, y=y_pos, w=img_width)
        self.set_y(120) 
        self.set_font('Helvetica', 'B', 24)
        self.set_text_color(*self.col_cyan)
        self.cell(0, 15, self.safe_txt("Transformer la fermentation industrielle"), align='C', ln=True)
        self.set_font('Helvetica', '', 18)
        self.set_text_color(*self.col_white)
        self.cell(0, 10, self.safe_txt("De la boite noire a la maitrise absolue"), align='C', ln=True)
        self.set_y(185)
        self.set_font('Helvetica', 'I', 13)
        self.set_text_color(*self.col_gray)
        self.cell(0, 10, self.safe_txt("Presentation Investisseurs & Partenaires"), align='C')

    def add_slide(self, title, content_lines=[], big_stat=None):
        self._draw_background_and_title(title)
        if big_stat:
            self._draw_big_stats(big_stat)
            return
        self.set_xy(self.margin_left, 45)
        self.set_text_color(*self.col_white)
        for line in content_lines:
            safe_line = self.safe_txt(line)
            if safe_line.strip().startswith("•"):
                self.set_font('Helvetica', 'B', 15)
                self.set_text_color(*self.col_green)
                self.set_x(self.margin_left)
                self.cell(10, 10, ">", ln=0)
                self.set_font('Helvetica', '', 14)
                self.set_text_color(*self.col_white)
                text_clean = safe_line.replace("•", "").strip()
                self.multi_cell(0, 10, text_clean)
                self.ln(2)
            elif safe_line.strip().startswith("-"):
                self.set_font('Helvetica', '', 12)
                self.set_x(25)
                self.cell(5, 8, "-", ln=0)
                self.multi_cell(0, 8, safe_line.replace("-", "").strip())
            else:
                self.set_font('Helvetica', '', 14)
                self.set_x(self.margin_left)
                self.multi_cell(0, 10, safe_line)
                self.ln(2)

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

# --- EXÉCUTION DU SCRIPT ---
pdf = PitchDeck()
pdf.create_cover_big_logo()

# Slide Problème
problem_blocks = [
    ("money.png", "L'Instabilite Biologique : Un Gouffre Financier", 
     ["Deviations infimes = consequences exponentielles.", "Cout direct de milliers d'euros par lot jete."]),
    ("blind.png", "Le Constat : Une Gestion Reactive et Aveugle", 
     ["Boite Noire : Manque de visibilite sur l'interieur des cellules.", "Pilotage dans le retroviseur : On agit souvent trop tard."])
]
pdf.add_slide_problem_visual("Le Probleme : La Fermentation est une Boite Noire", problem_blocks)

# --- SLIDE SOLUTION HARMONISÉE ---
pdf.add_slide_solution_visual("La Solution ReaKt : L'IA qui Anticipe", [
    "• Au-dela du monitoring",
    "- ReaKt ne se contente pas de surveiller : il anticipe.",
    "- Un veritable pilote automatique biologique.",
    "• Technologie de Deep Learning",
    "- Notre reseau de neurones predit les comportements cellulaires complexes.",
    "- Notre algorithme reagit avant meme que l'incident ne soit visible."], "example.png")

# Reste des slides
pdf.add_slide("La Preuve : Un Prototype Fonctionnel", ["• Ajustement autonome des flux d'alimentation.", "• Prediction fiable des pics de biomasse."])
pdf.add_slide("L'Impact : Resultats de la Simulation", big_stat=[("+20%", "d'augmentation de la production sur un an."), ("0", "perte de lot detectee.")])
pdf.add_slide("Stade de Developpement & Traction", ["• Iteration avancee : +20% production.", "• Validation experts metiers."])
pdf.add_slide("Vision : L'Industrie 4.0 de la Biologie", ["• Transformer un art risqué en processus industriel stable."])
pdf.add_slide("L'Equipe & Partenaires", ["• Expertise hybride Biologie & IA.", "• Soutien Hack the Fork."])
pdf.add_slide("Prochaines Etapes", ["• Recherche de Partenaires Industriels pour pilotes en echelle reelle."])
pdf.add_slide("Contactez-nous", ["• contact@reakt-bio.com", "• www.reakt-bio.com"])

pdf.output("ReaKt_Full_Deck.pdf")
print("✅ PDF genere avec style de police harmonise.")