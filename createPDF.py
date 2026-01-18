from fpdf import FPDF
import os
import warnings
from PIL import Image

warnings.simplefilter('ignore')

# ==================================================
# UTILITAIRE : taille image
# ==================================================
def image_size_mm(path, dpi=300):
    if not os.path.exists(path):
        return (0, 0)
    with Image.open(path) as img:
        w_px, h_px = img.size
    mm_per_inch = 25.4
    return (w_px * mm_per_inch / dpi, h_px * mm_per_inch / dpi)

# ==================================================
# CLASSE PDF - PITCH DECK
# ==================================================
class PitchDeck(FPDF):
    def __init__(self):
        super().__init__(unit='mm')
        self.set_auto_page_break(auto=False)

        # --- COULEURS ---
        self.col_bg = (10, 25, 40)       # Bleu Nuit
        self.col_white = (255, 255, 255)
        self.col_green = (0, 220, 160)   # Vert Tech
        self.col_cyan = (0, 180, 255)    # Cyan Accent
        self.col_grey = (80, 80, 80)     # Placeholders

        # --- TYPOGRAPHIE ---
        self.font_title = ('Helvetica', 'B', 24)
        self.font_block_title = ('Helvetica', 'B', 14)
        self.font_body = ('Helvetica', '', 11)
        self.font_emphasis = ('Helvetica', 'B', 11)
        self.line_height = 7

        # --- MARGES ---
        self.margin_left = 15
        self.margin_right = 15
        self.page_width_mm = 297
        self.page_height_mm = 210

    def safe_txt(self, text):
        return text.encode('latin-1', 'replace').decode('latin-1')

    def usable_width(self):
        return self.page_width_mm - self.margin_left - self.margin_right

# ==================================================
    # PAGE ET HEADER (CORRIGÉ)
    # ==================================================
    def add_page_with_background(self, image_path):
        # CORRECTION : On force l'orientation Paysage ('L') au lieu de passer un 'format' tuple
        # La version standard de FPDF ne supporte pas format=(w, h) ici.
        self.add_page(orientation='L') 
        
        # Dimensions standard A4 Paysage
        target_w = 297
        target_h = 210

        if os.path.exists(image_path):
            # On étire l'image pour qu'elle remplisse la page A4
            self.image(image_path, x=0, y=0, w=target_w, h=target_h)
            
            # On met à jour les dimensions internes
            self.page_width_mm = target_w
            self.page_height_mm = target_h
        else:
            # Fond bleu par défaut si pas d'image
            self.page_width_mm = target_w
            self.page_height_mm = target_h
            self.set_fill_color(*self.col_bg)
            self.rect(0, 0, target_w, target_h, 'F')

    def draw_header(self, title):
        self.set_font(*self.font_title)
        self.set_text_color(*self.col_white)
        
        # Titre à côté du logo (X=35 pour ne pas être dessus)
        title_x = 35 
        title_y = 15
        
        self.set_xy(title_x, title_y)
        self.cell(0, 15, self.safe_txt(title), ln=True)
        
        # Ligne verte décorative
        self.set_fill_color(*self.col_green)
        self.rect(title_x, self.get_y(), 20, 1, 'F')

    def draw_placeholder(self, x, y, w, h, label="Image manquante"):
        self.set_fill_color(*self.col_grey)
        self.set_draw_color(200, 200, 200)
        self.rect(x, y, w, h, 'DF')
        self.set_xy(x, y + h/2 - 5)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(255, 255, 255)
        self.cell(w, 5, self.safe_txt(label), align='C')

    # ==================================================
    # SLIDE STANDARD
    # ==================================================
    def add_slide(self, title, content_lines=[], big_stat=None):
        self.add_page_with_background("banner.png")
        self.draw_header(title)

        if big_stat:
            y_start = 80
            col_width = self.usable_width() / len(big_stat)
            for i, (number, text) in enumerate(big_stat):
                x_pos = self.margin_left + (i * col_width)
                self.set_xy(x_pos, y_start)
                self.set_font('Helvetica', 'B', 45)
                self.set_text_color(*self.col_green)
                self.cell(col_width, 20, number, align='C', ln=True)
                self.set_xy(x_pos + 5, y_start + 22)
                self.set_font('Helvetica', 'B', 14)
                self.set_text_color(*self.col_white)
                self.multi_cell(col_width - 10, 6, self.safe_txt(text), align='C')
            return

        self.set_xy(self.margin_left, 50)
        for line in content_lines:
            safe = self.safe_txt(line)
            if safe.startswith("-"):
                self.ln(4)
                self.set_font(*self.font_block_title)
                self.set_text_color(*self.col_green)
                self.multi_cell(self.usable_width(), self.line_height, safe.replace("-", "").strip())
            else:
                self.set_font(*self.font_body)
                self.set_text_color(*self.col_white)
                self.set_x(self.margin_left + 2)
                self.cell(5, self.line_height, ">", ln=0)
                x = self.get_x()
                self.multi_cell(self.page_width_mm - x - self.margin_right, self.line_height, safe)

    # ==================================================
    # SLIDE : VISUEL LARGE
    # ==================================================
    def add_slide_top_down_visual(self, title, content_lines, image_path):
        self.add_page_with_background("banner.png")
        self.draw_header(title)

        # 1. Le Texte
        self.set_xy(self.margin_left, 40)
        
        for line in content_lines:
            safe = self.safe_txt(line)
            if safe.startswith("-"):
                self.ln(1) 
                self.set_font(*self.font_block_title)
                self.set_text_color(*self.col_green)
                self.multi_cell(self.usable_width(), self.line_height, safe.replace("-", "").strip())
            else:
                self.set_font(*self.font_body)
                self.set_text_color(*self.col_white)
                self.set_x(self.margin_left + 2)
                self.cell(5, self.line_height, ">", ln=0)
                x = self.get_x()
                self.multi_cell(self.page_width_mm - x - self.margin_right, self.line_height, safe)

        # 2. L'Image (Légèrement réduite et centrée)
        y_current = self.get_y() + 2 
        
        # On réduit la largeur à 90% de la page pour éviter le bord à bord total
        target_w = self.page_width_mm * 0.9 
        target_x = (self.page_width_mm - target_w) / 2 # Recentrage automatique
        
        # Marge de sécurité en bas
        available_h = self.page_height_mm - 10 - y_current
        
        if os.path.exists(image_path):
            w_orig, h_orig = image_size_mm(image_path)
            ratio = h_orig / w_orig if w_orig > 0 else 0.5
            display_h = target_w * ratio
            
            # Ajustement si l'image est trop haute pour l'espace restant
            if display_h > available_h:
                display_h = available_h
                target_w = display_h / ratio
                target_x = (self.page_width_mm - target_w) / 2
            
            self.image(image_path, x=target_x, y=y_current, w=target_w)
        else:
            h_ph = min(80, available_h)
            self.draw_placeholder(target_x, y_current, target_w, h_ph, f"Visuel: {image_path}")

    # ==================================================
    # SLIDE TEAM (CORRECTION VISIBILITÉ MAIL)
    # ==================================================
    def add_slide_team_photos(self, title, members):
        self.add_page_with_background("banner.png")
        self.draw_header(title)

        y_start = 60 # Position verticale des photos
        photo_size = 35
        gap = 10
        
        total_width = len(members) * photo_size + (len(members) - 1) * gap
        current_x = (self.page_width_mm - total_width) / 2
        
        for name, email, img_path in members:
            # 1. PHOTO
            if os.path.exists(img_path):
                self.image(img_path, x=current_x, y=y_start, w=photo_size, h=photo_size)
            else:
                self.draw_placeholder(current_x, y_start, photo_size, photo_size, "Photo")
            
            # 2. NOM (Sous la photo)
            self.set_xy(current_x - 5, y_start + photo_size + 4)
            self.set_font(*self.font_emphasis)
            self.set_text_color(*self.col_green)
            self.cell(photo_size + 10, 5, self.safe_txt(name), align='C')

            # 3. EMAIL (CORRECTION ICI)
            # On calcule le centre de la photo
            center_photo = current_x + (photo_size / 2)
            
            # On définit une largeur de cellule suffisante pour le mail long (55mm)
            mail_cell_width = 55
            
            # On démarre la cellule pour que le texte soit centré sous la photo
            mail_start_x = center_photo - (mail_cell_width / 2)
            
            self.set_xy(mail_start_x, y_start + photo_size + 10)
            self.set_font('Helvetica', '', 7) # Police 7 pour garantir l'affichage
            self.set_text_color(*self.col_cyan)
            self.cell(mail_cell_width, 4, self.safe_txt(email), align='C')
            
            # Décalage pour le prochain membre
            current_x += photo_size + gap

    # ==================================================
    # COUVERTURE
    # ==================================================
    def create_cover(self):
        self.add_page_with_background("first.png")
        
        self.set_xy(0, 140)
        self.set_font('Helvetica', 'B', 28)
        self.set_text_color(*self.col_white)
        self.cell(297, 15, self.safe_txt("ReaKt"), align='C', ln=True)
        
        self.set_font('Helvetica', '', 18)
        self.set_text_color(*self.col_green)
        self.cell(297, 12, self.safe_txt("Optimisation des Bioréacteurs par IA"), align='C', ln=True)


# ==================================================
# SCÉNARIO
# ==================================================
pdf = PitchDeck()

# 1. Cover
pdf.create_cover()


# 2. PROBLÈME (Le manque à gagner réel)
# Feedback : "Le problème de rendement est identifié... précisez que c'est un défi d'aujourd'hui"
pdf.add_slide(
    "Le Problème : Un Risque Industriel Majeur",
    [
        "- L'Incertitude de la Fermentation",
        "Les processus biologiques sont instables. Aujourd'hui, un industriel pilote souvent 'à l'aveugle' entre deux prélèvements.",
        
        "- Le Coût Réel (Manque à Gagner)",
        "En moyenne, 1 lot sur 10 est perdu ou dégradé (contamination, dérive de pH).",
        "Cela représente des pertes financières directes et des retards de production critiques.",
    ],
)

# 3. Solution
pdf.add_slide_top_down_visual(
    "La Solution ReaK : Pilotage par Deep Learning",
    [
        "- Anticipation Cellulaire",
        "Notre algorithme de Deep Learning ne se contente pas de suivre : il anticipe les comportements de la biomasse.",
        "- Autopilote Industriel",
        "Correction des paramètres (O2, Agitation, pH) en temps réel pour éviter les incidents avant qu'ils n'arrivent."
    ],
    "example.png"
)


# 4. Prototype
pdf.add_slide_top_down_visual(
    "Validation (POC) : Résultats Techniques",
    [
        "- Modèle Validé",
        "Nous validons actuellement notre modèle sur le simulateur que nous avons développé.",
        
        "- Performance",
        "Marge d'erreur de prédiction < 2% sur les courbes de croissance biomasse.",
        "Capacité démontrée à stabiliser une dérive simulée sans intervention humaine."
    ],
    "predictions.png"
)

# 5. Impact
pdf.add_slide(
    "L'Impact Financier & Opérationnel",
    big_stat=[
        ("0", "Lot Perdu"),
        ("+20%", "Productivité"),
        ("-15%", "Coût Énergie")
    ]
)

# 6. MARCHÉ
pdf.add_slide(
    "Marché Cible & Potentiel",
    [
         "- Secteurs Prioritaires",
        "1. FoodTech (Agriculture cellulaire, besoin de scalabilité).",
        "2. Pharma (Haute valeur ajoutée, tolérance zéro défaut).",
        "3. Chimie Verte (Optimisation des coûts).",
        
        "- Taille du Marché (TAM)",
        "Marché global des bioréacteurs : 30 Milliards $.",
        "Segment logiciel d'optimisation : En croissance de 12% / an."
    ]
)

# 7. Business Plan
pdf.add_slide(
    "Business Model : Revenus Récurrents",
    [
        "- 1. Setup & Calibration (One-off)",
        "Installation des sondes virtuelles et calibration du modèle sur les données historiques du client.",
        
        "- 2. Licence SaaS (Récurrent)",
        "Abonnement mensuel par bioréacteur connecté.",
        
        "- 3. Success Fees (Scale-up)",
        "Commission indexée sur le gain de rendement net généré par l'algorithme."
    ]
)

# 8. Roadmap
pdf.add_slide(
    "Roadmap R&D : Améliorations Futures",
    [
        "- Optimisation Énergétique (Smart Grid)",
        "Relier le lancement des batchs aux prix spot de l'électricité.",
        "Simulateur déjà fonctionnel pour arbitrer coût énergie vs rendement bio.",
        "- Maintenance Prédictive des Capteurs",
        "Détection précoce des dérives de sondes (pH, O2) avant qu'elles ne faussent la production.",
        "Réduction des temps d'arrêt technique.",
    ]
)

# 9. Team
pdf.add_slide_team_photos(
    "L'Équipe ReaKt",
    [
        ("Paul Chevalier", "paul.chevalier@edu.ece.fr", "paul.jpg"),
        ("Elias Moussouni", "elias.moussouni@edu.ece.fr", "mouss.jpg"),
        ("Ziyad Amzil", "ziyad.amzil@edu.ece.fr", "ziyad.jpg"),
        ("Malik Hassane", "malik.hassane@edu.ece.fr", "malik.png"),
        ("Gabriel Guiet-Dupré", "gabriel.guietdupre@edu.ece.fr", "gab.jpg")
    ]
)

# 10. VISION
pdf.add_slide(
    "Vision : L'Industrie 4.0 de la Biologie",
    [
        "- Standardisation",
        "Rendre la bioproduction aussi prévisible et standardisée que l'industrie automobile.",
        
        "- Scalabilité",
        "Permettre le passage du laboratoire à l'usine sans perte de rendement grâce à l'IA."
    ]
)

pdf.output("ReaKt_Full_Deck_Final_v3.pdf")
print("✅ PDF corrigé : Paul et son mail sont maintenant visibles !")
