from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class SGGameSpaceSizeManager:
    """
    Gestionnaire de taille spécifique aux game_spaces.
    
    Cette classe gère le calcul et l'adaptation des dimensions des game_spaces
    basés sur leur contenu interne (widgets, labels, etc.).
    """
    
    def __init__(self):
        # Marges et espacements spécifiques aux game_spaces
        self.right_margin = 9
        self.vertical_gap_between_labels = 5
        self.border_padding = 3
        
        # Tailles minimales pour les game_spaces
        self.min_width = 100
        self.min_height = 50
        
        # Facteurs de calcul basés sur l'analyse de SGLegend
        self.char_width_factor = 12  # Largeur approximative par caractère
        self.line_height_factor = 20  # Hauteur par ligne de texte
    
    def calculate_content_width(self, content_widgets):
        """
        Calcule la largeur nécessaire basée sur les widgets de contenu.
        
        Args:
            content_widgets (list): Liste des widgets contenus dans le game_space
            
        Returns:
            int: Largeur calculée en pixels
        """
        if not content_widgets:
            return self.min_width
            
        max_width = 0
        for widget in content_widgets:
            if hasattr(widget, 'geometry'):
                widget_width = widget.geometry().size().width()
                max_width = max(max_width, widget_width)
            elif hasattr(widget, 'text'):
                # Calcul basé sur la longueur du texte
                text_width = len(widget.text) * self.char_width_factor
                max_width = max(max_width, text_width)
        
        return max_width + self.right_margin + self.border_padding
    
    def calculate_content_height(self, content_items):
        """
        Calcule la hauteur nécessaire basée sur le nombre d'éléments de contenu.
        
        Args:
            content_items (list): Liste des éléments de contenu
            
        Returns:
            int: Hauteur calculée en pixels
        """
        if not content_items:
            return self.min_height
            
        # Calcul basé sur le nombre d'éléments et l'espacement
        num_items = len(content_items)
        total_height = num_items * self.line_height_factor
        gaps_height = (num_items - 1) * self.vertical_gap_between_labels
        
        return total_height + gaps_height + self.border_padding
    
    def calculate_text_width(self, text_content):
        """
        Calcule la largeur nécessaire pour un contenu textuel.
        
        Args:
            text_content (str): Le contenu textuel
            
        Returns:
            int: Largeur calculée en pixels
        """
        if not text_content:
            return self.min_width
            
        # Calcul basé sur la longueur du texte le plus long
        lines = text_content.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else 0
        
        return max_line_length * self.char_width_factor + self.right_margin + self.border_padding
    
    def calculate_text_height(self, text_content):
        """
        Calcule la hauteur nécessaire pour un contenu textuel.
        
        Args:
            text_content (str): Le contenu textuel
            
        Returns:
            int: Hauteur calculée en pixels
        """
        if not text_content:
            return self.min_height
            
        # Calcul basé sur le nombre de lignes
        lines = text_content.split('\n')
        num_lines = len(lines)
        
        return num_lines * self.line_height_factor + self.border_padding
    
    def adjust_game_space_to_content(self, game_space, content_widgets=None, content_items=None, text_content=None):
        """
        Ajuste la taille du game_space à son contenu.
        
        Args:
            game_space: L'instance du game_space à ajuster
            content_widgets (list, optional): Widgets de contenu
            content_items (list, optional): Éléments de contenu
            text_content (str, optional): Contenu textuel
        """
        width = self.min_width
        height = self.min_height
        
        # Calcul de la largeur
        if content_widgets:
            width = max(width, self.calculate_content_width(content_widgets))
        elif text_content:
            width = max(width, self.calculate_text_width(text_content))
        
        # Calcul de la hauteur
        if content_items:
            height = max(height, self.calculate_content_height(content_items))
        elif text_content:
            height = max(height, self.calculate_text_height(text_content))
        
        # Application de la taille calculée
        game_space.setMinimumSize(width, height)
        game_space.resize(width, height)
    
    def set_right_margin(self, margin):
        """
        Définir la marge droite.
        
        Args:
            margin (int): Nouvelle marge en pixels
        """
        self.right_margin = margin
    
    def set_vertical_gap(self, gap):
        """
        Définir l'espacement vertical entre les labels.
        
        Args:
            gap (int): Nouvel espacement en pixels
        """
        self.vertical_gap_between_labels = gap
    
    def set_border_padding(self, padding):
        """
        Définir le padding de bordure.
        
        Args:
            padding (int): Nouveau padding en pixels
        """
        self.border_padding = padding
    
    def set_minimum_size(self, min_width, min_height):
        """
        Définir les tailles minimales.
        
        Args:
            min_width (int): Largeur minimale
            min_height (int): Hauteur minimale
        """
        self.min_width = min_width
        self.min_height = min_height
