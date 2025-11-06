from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class SGGameSpaceSizeManager:
    """
    Size manager specific to game_spaces.
    
    This class manages the calculation and adaptation of game_spaces dimensions
    based on their internal content (widgets, labels, etc.).
    """
    
    def __init__(self):
        # Margins and spacing specific to game_spaces
        self.right_margin = 9
        self.vertical_gap_between_labels = 5
        self.border_padding = 3
        
        # Minimum sizes for game_spaces
        self.min_width = 100
        self.min_height = 50
        
        # Calculation factors based on SGLegend analysis
        self.char_width_factor = 12  # Approximate width per character
        self.line_height_factor = 20  # Height per text line
    
    def calculate_content_width(self, content_widgets):
        """
        Calculate necessary width based on content widgets.
        
        Args:
            content_widgets (list): List of widgets contained in the game_space
            
        Returns:
            int: Calculated width in pixels
        """
        if not content_widgets:
            return self.min_width
            
        max_width = 0
        for widget in content_widgets:
            if hasattr(widget, 'geometry'):
                widget_width = widget.geometry().size().width()
                max_width = max(max_width, widget_width)
            elif hasattr(widget, 'text'):
                # Calculation based on text length
                text_width = len(widget.text) * self.char_width_factor
                max_width = max(max_width, text_width)
        
        return max_width + self.right_margin + self.border_padding
    
    def calculate_content_height(self, content_items):
        """
        Calculate necessary height based on the number of content items.
        
        Args:
            content_items (list): List of content items
            
        Returns:
            int: Calculated height in pixels
        """
        if not content_items:
            return self.min_height
            
        # Calculation based on number of items and spacing
        num_items = len(content_items)
        total_height = num_items * self.line_height_factor
        gaps_height = (num_items - 1) * self.vertical_gap_between_labels
        
        return total_height + gaps_height + self.border_padding
    
    def calculate_text_width(self, text_content):
        """
        Calculate necessary width for text content.
        
        Args:
            text_content (str): The text content
            
        Returns:
            int: Calculated width in pixels
        """
        if not text_content:
            return self.min_width
            
        # Calculation based on the longest text line
        lines = text_content.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else 0
        
        return max_line_length * self.char_width_factor + self.right_margin + self.border_padding
    
    def calculate_text_height(self, text_content, font=None):
        """
        Calculate necessary height for text content using QFontMetrics.
        
        Args:
            text_content (str): The text content
            font (QFont, optional): Font to use for calculation. If None, uses default font.
            
        Returns:
            int: Calculated height in pixels
        """
        if not text_content:
            return self.min_height
        
        # Use default font if none provided
        if font is None:
            font = QFont("Verdana", 10)  # Default SGE font
        
        # Create QFontMetrics to calculate real dimensions
        metrics = QFontMetrics(font)
        
        # Calculate real height based on number of lines
        lines = text_content.split('\n')
        num_lines = len(lines)
        
        # Use real line height from the font with additional margin for safety
        line_height = metrics.height()
        
        # Add extra margin to prevent text clipping (empirical factor)
        line_height_with_margin = line_height + 2
        
        # Calculate total height with border padding and extra safety margin
        total_height = num_lines * line_height_with_margin + self.border_padding + 10
        
        return max(total_height, self.min_height)
    
    def adjust_game_space_to_content(self, game_space, content_widgets=None, content_items=None, text_content=None, font=None):
        """
        Adjust game_space size to its content.
        
        Args:
            game_space: The game_space instance to adjust
            content_widgets (list, optional): Content widgets
            content_items (list, optional): Content items
            text_content (str, optional): Text content
            font (QFont, optional): Font to use for text height calculation
        """
        width = self.min_width
        height = self.min_height
        
        # Calculate width
        if content_widgets:
            width = max(width, self.calculate_content_width(content_widgets))
        elif text_content:
            width = max(width, self.calculate_text_width(text_content))
        
        # Calculate height
        if content_items:
            height = max(height, self.calculate_content_height(content_items))
        elif text_content:
            height = max(height, self.calculate_text_height(text_content, font))
        
        # Apply calculated size
        game_space.setMinimumSize(width, height)
        game_space.resize(width, height)
    
    def set_right_margin(self, margin):
        """
        Set right margin.
        
        Args:
            margin (int): New margin in pixels
        """
        self.right_margin = margin
    
    def set_vertical_gap(self, gap):
        """
        Set vertical spacing between labels.
        
        Args:
            gap (int): New spacing in pixels
        """
        self.vertical_gap_between_labels = gap
    
    def set_border_padding(self, padding):
        """
        Set border padding.
        
        Args:
            padding (int): New padding in pixels
        """
        self.border_padding = padding
    
    def set_minimum_size(self, min_width, min_height):
        """
        Set minimum sizes.
        
        Args:
            min_width (int): Minimum width
            min_height (int): Minimum height
        """
        self.min_width = min_width
        self.min_height = min_height
