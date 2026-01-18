from fpdf import FPDF
import os
import math
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
        # Format 297x180mm
        self.page_width_mm = 297
        self.page_height_mm = 180 
        
        super().__init__(unit='mm', format=(self.page_width_mm, self.page_height_mm))
        self.set_auto_page_break(auto=False)

        # --- COULEURS ---
        self.col_bg = (10, 25, 40)
        # self.col_border = (0, 180, 255) # Plus utilisé car plus de cadre
        
        self.col_white = (255, 255, 255)
        self.col_green = (0, 220, 160)
        self.col_cyan = (0, 180, 255)
        self.col_grey = (80, 80, 80)

        # --- TYPOGRAPHIE (TAILLES AGRANDIES) ---
        self.font_title = ('Helvetica', 'B', 32)
        self.font_block_title = ('Helvetica', 'B', 20)
        self.font_body = ('Helvetica', '', 15)
        self.font_emphasis = ('Helvetica', 'B', 15)
        self.line_height = 10 

        # --- MARGES ---
        self.margin_left = 15
        self.margin_right = 15

    def safe_txt(self, text):
        return text.encode('latin-1', 'replace').decode('latin-1')

    def usable_width(self):
        return self.page_width_mm - self.margin_left - self.margin_right

    # --- PARSER LE CONTENU ---
    def parse_content(self, content_lines):
        blocks = []
        current_block = None
        for line in content_lines:
            safe = self.safe_txt(line)
            if safe.strip().startswith("-"):
                if current_block:
                    blocks.append(current_block)
                clean_title = safe.replace("-", "").strip()
                current_block = {'title': clean_title, 'text': ""}
            else:
                if current_block:
                    # REMPLACER l'espace par \n pour garder le formatage de liste
                    current_block['text'] += safe + "\n" 
        
        if current_block:
            blocks.append(current_block)
        return blocks

    # ==================================================
    # LOGIQUE D'AJUSTEMENT (SANS DESSIN DU CADRE)
    # ==================================================
    def estimate_lines(self, text, width_mm, font_family, font_style, font_size):
        """Estime le nombre de lignes qu'un texte va prendre"""
        self.set_font(font_family, font_style, font_size)
        total_width = self.get_string_width(text)
        if total_width == 0: return 0
        return math.ceil(total_width / width_mm * 1.1)

    def draw_smart_card(self, x, y, w, title, text):
        """
        Calcule la hauteur nécessaire et place le texte.
        NE DESSINE PLUS DE RECTANGLE, mais garde la logique de positionnement.
        """
        padding = 5
        content_w = w - (2 * padding)
        
        # 1. Calculer la hauteur nécessaire (On garde ça pour le layout)
        lines_title = self.estimate_lines(title, content_w, *self.font_block_title)
        h_title = max(1, lines_title) * (self.line_height + 1)
        
        lines_text = self.estimate_lines(text, content_w, *self.font_body)
        h_text = max(1, lines_text) * self.line_height
        
        total_h = padding + h_title + 2 + h_text + padding
        
        # 2. Dessiner le cadre -> SUPPRIMÉ
        # self.rect(x, y, w, total_h, 'D') 
        
        # 3. Ecrire le Titre
        self.set_xy(x + padding, y + padding)
        self.set_font(*self.font_block_title)
        self.set_text_color(*self.col_green)
        self.multi_cell(content_w, self.line_height + 1, title, align='L')
        
        # 4. Ecrire le Texte
        self.set_xy(x + padding, y + padding + h_title + 2)
        self.set_font(*self.font_body)
        self.set_text_color(*self.col_white)
        self.multi_cell(content_w, self.line_height, text, align='L')
        
        # On retourne la hauteur totale virtuelle pour que la mise en page continue de fonctionner
        return total_h

    # ==================================================
    # PAGE ET HEADER
    # ==================================================
    def add_page_with_background(self, image_path):
        self.add_page() 
        if os.path.exists(image_path):
            self.image(image_path, x=0, y=0, w=self.page_width_mm, h=self.page_height_mm)
        else:
            self.set_fill_color(*self.col_bg)
            self.rect(0, 0, self.page_width_mm, self.page_height_mm, 'F')

    def draw_header(self, title):
        self.set_font(*self.font_title)
        self.set_text_color(*self.col_white)
        title_x = 45 
        title_y = 15 
        self.set_xy(title_x, title_y)
        self.cell(0, 18, self.safe_txt(title), ln=True)
        self.set_fill_color(*self.col_green)
        self.rect(title_x, self.get_y() - 3, 20, 1, 'F')

    def draw_placeholder(self, x, y, w, h, label="Image manquante"):
        self.set_fill_color(*self.col_grey)
        self.set_draw_color(200, 200, 200)
        self.rect(x, y, w, h, 'DF')
        self.set_xy(x, y + h/2 - 5)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(255, 255, 255)
        self.cell(w, 5, self.safe_txt(label), align='C')

    # ==================================================
    # RENDU DES BLOCS (LOGIQUE INCHANGÉE)
    # ==================================================
    def render_blocks(self, blocks, start_y):
        self.set_xy(self.margin_left, start_y)
        
        # MODE 2 COLONNES
        if len(blocks) == 2:
            col_width = (self.usable_width() / 2) - 5
            col_gap = 10
            y_top = self.get_y()
            
            h1 = self.draw_smart_card(self.margin_left, y_top, col_width, blocks[0]['title'], blocks[0]['text'])
            h2 = self.draw_smart_card(self.margin_left + col_width + col_gap, y_top, col_width, blocks[1]['title'], blocks[1]['text'])
            
            # DIMINUTION ICI : passage de + 5 à + 2
            self.set_y(y_top + max(h1, h2) + 2)

        # MODE LISTE
        else:
            current_y = start_y
            for b in blocks:
                height_used = self.draw_smart_card(self.margin_left, current_y, self.usable_width(), b['title'], b['text'])
                # DIMINUTION ICI : passage de + 5 à + 2
                current_y += height_used + 2

    # ==================================================
    # SLIDE STANDARD
    def add_slide(self, title, content_lines=[], big_stat=None):
        self.add_page_with_background("banner.png")
        self.draw_header(title)

        # 1. Gestion du texte
        if content_lines:
            is_block = any(line.strip().startswith("-") for line in content_lines)
            
            if is_block:
                blocks = self.parse_content(content_lines)
                self.render_blocks(blocks, start_y=55)
            else:
                # MODE TEXTE SIMPLE DESCENDU ET CENTRÉ
                # On le place à y=65 pour qu'il soit proche des stats
                self.set_xy(self.margin_left, 65) 
                self.set_font(*self.font_body)
                self.set_text_color(*self.col_white)
                for line in content_lines:  
                    # align='C' pour centrer le texte sur toute la largeur utilisable
                    self.multi_cell(self.usable_width(), self.line_height, self.safe_txt(line), align='C')

        # 2. Gestion des statistiques
        if big_stat:
            # On descend un peu les chiffres pour laisser de la place au texte au-dessus
            y_start = 85 if content_lines else 70
            
            col_width = self.usable_width() / len(big_stat)
            for i, (number, text) in enumerate(big_stat):
                x_pos = self.margin_left + (i * col_width)
                self.set_xy(x_pos, y_start)
                self.set_font('Helvetica', 'B', 60)
                self.set_text_color(*self.col_green)
                self.cell(col_width, 25, number, align='C', ln=True)
                
                self.set_xy(x_pos + 5, self.get_y() + 5)
                self.set_font('Helvetica', 'B', 18)
                self.set_text_color(*self.col_white)
                self.multi_cell(col_width - 10, 8, self.safe_txt(text), align='C')

    # ==================================================
    # SLIDE : VISUEL LARGE
    # ==================================================
    def add_slide_top_down_visual(self, title, content_lines, image_path):
        self.add_page_with_background("banner.png")
        self.draw_header(title)

        # 1. Le Texte
        blocks = self.parse_content(content_lines)
        self.render_blocks(blocks, start_y=45) 

        # 2. L'Image
        y_current = self.get_y() + 5
        target_w = self.page_width_mm * 0.85 
        target_x = (self.page_width_mm - target_w) / 2 
        
        available_h = self.page_height_mm - 5 - y_current
        if available_h < 40: available_h = 40

        if os.path.exists(image_path):
            w_orig, h_orig = image_size_mm(image_path)
            ratio = h_orig / w_orig if w_orig > 0 else 0.5
            display_h = target_w * ratio
            
            if display_h > available_h:
                display_h = available_h
                target_w = display_h / ratio
                target_x = (self.page_width_mm - target_w) / 2
            
            self.image(image_path, x=target_x, y=y_current, w=target_w)
        else:
            h_ph = min(60, available_h)
            self.draw_placeholder(target_x, y_current, target_w, h_ph, f"Visuel: {image_path}")

    # ==================================================
    # SLIDE TEAM
    # ==================================================
    def add_slide_team_photos(self, title, members, team_img_path="team_group.jpg"):
        self.add_page_with_background("banner.png")
        self.draw_header(title)

        # --- PHOTO DE GROUPE (Légèrement remontée pour laisser de la place) ---
        team_img_w = 95    # Largeur équilibrée
        team_img_x = (self.page_width_mm - team_img_w) / 2
        team_img_y = 32    # Positionnée plus haut pour gagner de l'espace en bas
        
        group_h_used = 0
        if os.path.exists(team_img_path):
            with Image.open(team_img_path) as img:
                w_px, h_px = img.size
                ratio = h_px / w_px
                team_img_h = team_img_w * ratio
            self.image(team_img_path, x=team_img_x, y=team_img_y, w=team_img_w)
            group_h_used = team_img_h
        else:
            group_h_used = 35
            self.draw_placeholder(team_img_x, team_img_y, team_img_w, group_h_used, "Team Group Photo")

        # --- PHOTOS INDIVIDUELLES AGRANDIES ET ESPACÉES ---
        photo_size = 32    # AGRANDI (était à 25)
        gap = 18           # ESPACÉ (était à 12) pour un rendu moins tassé
        
        total_width = len(members) * photo_size + (len(members) - 1) * gap
        current_x = (self.page_width_mm - total_width) / 2
        
        # Point de départ vertical (sous la photo de groupe)
        y_start = team_img_y + group_h_used + 10

        for name, email, img_path in members:
            # 1. PHOTO PORTRAIT
            if os.path.exists(img_path):
                self.image(img_path, x=current_x, y=y_start, w=photo_size, h=photo_size)
            else:
                self.draw_placeholder(current_x, y_start, photo_size, photo_size, "Photo")
            
            # 2. NOM (Espacement augmenté sous la photo)
            name_y = y_start + photo_size + 5
            self.set_xy(current_x - 10, name_y) # Marge négative élargie pour noms longs
            self.set_font(*self.font_emphasis)
            self.set_text_color(*self.col_green)
            self.cell(photo_size + 20, 6, self.safe_txt(name), align='C')

            # 3. EMAIL (Placé précisément sous le nom)
            mail_y = name_y + 7
            center_photo = current_x + (photo_size / 2)
            mail_cell_width = 70 # Plus large pour éviter les coupures d'emails
            mail_start_x = center_photo - (mail_cell_width / 2)
            
            self.set_xy(mail_start_x, mail_y)
            self.set_font('Helvetica', '', 8.5) # Un tout petit peu plus lisible
            self.set_text_color(*self.col_cyan)
            self.cell(mail_cell_width, 4, self.safe_txt(email), align='C')
            
            current_x += photo_size + gap

    # ==================================================
    # COUVERTURE
    # ==================================================
    def create_cover(self):
        self.add_page_with_background("first.png")
        self.set_xy(49, self.page_height_mm * 0.21)
        self.set_font('Helvetica', 'B', 15)
        self.set_text_color(*self.col_white)
        self.cell(self.page_width_mm, 15, self.safe_txt("Bioreactor Optimization"), ln=True)


# ==================================================
# SCÉNARIO
# ==================================================
pdf = PitchDeck()

# 1. Cover
pdf.create_cover()

# 2. PROBLÈME
pdf.add_slide(
    "The Problem: A Major Industrial Risk",
    [
        "- Fermentation Uncertainty",
        "Biological processes are inherently unstable. Today, manufacturers often operate 'blindly' between manual samples.",
        "- The Real Cost (Lost Revenue)",
        "On average, 8% of the total yield is lost or degraded (contamination, pH drift). This results in direct and significant financial losses.",
    ],
)

# 3. Solution
pdf.add_slide_top_down_visual(
    "The ReaKt Solution: Deep Learning Control",
    [
        "- Cellular Anticipation",
        "Our Deep Learning algorithm goes beyond monitoring: it predicts biomass behavior before it shifts.",
        "- Industrial Autopilot",
        "The algorithm automatically adjusts bioreactor inputs (O2, Temperature, Acid/Base, ...) in real-time to maintain optimal conditions."
    ],
    "example.png"
)

# 4. Prototype
pdf.add_slide_top_down_visual(
    "Proof Of Concept (POC)",
    [
        "- Validated Model",
        "Our model is currently being validated using our proprietary custom-built simulator.",
        "- Performance Metrics",
        "Less than 2% prediction error on biomass growth curves. Proven ability to stabilize process drifts without human intervention."
    ],
    "predictions.png"
)

# 5. Impact
pdf.add_slide(
    "Financial & Operational Impact",
    ["Results for one year simulation"], # Ajout du sous-titre ici
    big_stat=[
        ("0", "Lost Batches"),
        ("+20%", "Productivity"),
        ("-15%", "Energy Costs")
    ]
)

# 6. MARCHÉ
pdf.add_slide(
    "Target Market & Potential",
    [
        "- Priority Sectors",
        "1. FoodTech (Cellular agriculture).",
        "2. Pharma (High value-added).",
        "3. Green Chemistry.",
        "- Market Size (TAM)",
        "Global Bioreactor Market: $30 Billion.",
        "Optimization Software Market: 12% annual growth (CAGR)."
    ]
)

# 7. Business Plan
pdf.add_slide(
    "Business Model: Strategic Rollout",
    [
        "- Early Adopters Program (Launch Phase)",
        "The first 2-3 partners will receive free software access to validate the solution in real-world industrial conditions. In exchange, ReaKt collects anonymized operational data to continuously refine and improve the algorithm.",
        "- Scaling Phase: Subscription Model",
        "Monthly SaaS license fee based on the number of connected bioreactors.",
        "- Performance Incentive (Success Fees)",
        "A commission indexed on the net financial gain generated by the algorithm's yield optimization."
    ]
)

# 8. Roadmap
pdf.add_slide(
    "R&D Roadmap",
    [
        "- Energy Optimization",
        "Linking batch launches to real-time electricity spot prices. Arbitrating energy costs vs. biological yield.",
        "- Predictive Maintenance",
        "Early detection of biomass shifts based on sensor data and Raman spectroscopy."
    ]
)

# 9. Team
pdf.add_slide_team_photos(
    "The ReaKt Team: From Hackathon to Start-up",
    [
        ("Paul Chevalier", "paul.chevalier@edu.ece.fr", "paul.jpg"),
        ("Elias Moussouni", "elias.moussouni@edu.ece.fr", "mouss.jpg"),
        ("Ziyad Amzil", "ziyad.amzil@edu.ece.fr", "ziyad.jpg"),
        ("Malik Hassane", "malik.hassane@edu.ece.fr", "malik.png"),
        ("Gabriel Guiet-Dupré", "gabriel.guietdupre@edu.ece.fr", "gab.jpg")
    ],
    "HTF.jpeg"
)

# 10. VISION
pdf.add_slide(
    "Vision: Biology’s Industry 4.0",
    [
        "- Global Standardization",
        "We aim to transform bioproduction into a process as predictable and reliable as the automotive industry. By integrating AI-driven control, we turn biological complexity into a standardized industrial asset.",
        "- Seamless Scalability",
        "Our goal is to bridge the gap between laboratory innovation and factory-scale production. We empower companies to scale up without yield loss, making sustainable bio-manufacturing commercially viable at any volume."
    ]
)

pdf.output("ReaKt_Full_Deck_Clean_No_Borders.pdf")
print("✅ PDF généré : Textes libres (sans encadré) mais bien alignés !")