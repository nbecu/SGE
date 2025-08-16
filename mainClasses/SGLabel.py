from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
# from PyQt5.QtWidgets import QStyleFactory
# from mainClasses.SGGameSpace import SGGameSpace


class SGLabel(QtWidgets.QWidget):
    def __init__(self, parent, text, textStyle_specs="", borderStyle_specs="", backgroundColor_specs="",  alignement= "Left", fixedWidth=None, fixedHeight=None):
        super().__init__(parent)
        self.model = parent
        self.moveable = True
        self.isDisplay = True
        
        label = QtWidgets.QLabel(text, self)
        
        if fixedWidth is not None:
            label.setFixedWidth(fixedWidth)
            label.setWordWrap(True)  # Allow line wrapping if the text is too long

        if fixedHeight is not None:
            label.setFixedHeight(fixedHeight)
        
        label.setAlignment(getattr(Qt, "Align"+alignement)) 

        
        # Build the complete stylesheet
        complete_style = f"{backgroundColor_specs}{textStyle_specs}{borderStyle_specs}"
        label.setStyleSheet(complete_style)
        # label.setFont(QFont('Arial', 18)) -> Other way to set the Font
        
        # ajust the size of the label according to its style font and border. Then redefine the size of the widget according to the size of the geometry of the label 
        label.adjustSize()   
        self.setMinimumSize(label.geometry().size())
 
  



  

# class SGLabel2(SGLabel):
#     def __init__(self, parent, text, font=None, size=None, color=None, text_decoration="none", font_weight="normal", font_style="normal", alignement= "Left", border_style="solid", border_size=0, border_color=None, background_color=None, fixedWidth=None, fixedHeight=None):
#          # Create the text style
#         textStyle_specs = f"font-family: {font}; font-size: {size}px; color: {color}; text-decoration: {text_decoration}; font-weight: {font_weight}; font-style: {font_style};"
#         # Create the border style
#         borderStyle_specs = f"border: {border_size}px {border_style} {border_color};"     
#         # Create the background style
#         backgroundColor_specs = f"background-color: {background_color};"
        
    
#         super().__init__(parent, text, textStyle_specs, borderStyle_specs, backgroundColor_specs, alignement, fixedWidth, fixedHeight)


# class SGLabel3(QtWidgets.QLabel):
#     def __init__(self, parent, text, font=None, size=None, color=None, text_decoration="none", font_weight="normal", font_style="normal", alignement= "Left", border_style=None, border_size=None, border_color=None, background_color=None, fixedWidth=None, fixedHeight=None):

#         # in case one parameter of border is defined, sets a default value for the other border parameters that are None
#         hasABorder = any(value is not None for value in [border_size, border_color, border_style])
#         if hasABorder:
#             if border_size is None: border_size = 1
#             if border_color is None: border_color = "black"
#             if border_style is None: border_style = "solid"

#          # Create the text style
#         textStyle_specs = f"font-family: {font}; font-size: {size}px; color: {color}; text-decoration: {text_decoration}; font-weight: {font_weight}; font-style: {font_style};"
#         # Create the border style
#         borderStyle_specs = f"border: {border_size}px {border_style} {border_color};"     
#         # Create the background style
#         backgroundColor_specs = f"background-color: {background_color};"
        
    
#         # super().__init__(parent, text, text_specs, border_specs, background_specs, alignement, fixedWidth, fixedHeight)
#         super().__init__()
#         self.setText(text)
#         if fixedWidth is not None:
#             self.setFixedWidth(fixedWidth)
#             self.setWordWrap(True)  # Allow line wrapping if the text is too long

#         if fixedHeight is not None:
#             self.setFixedHeight(fixedHeight)
        
#         self.setAlignment(getattr(Qt, "Align"+alignement)) 

        
#         # Build the complete stylesheet
#         complete_style = f"{backgroundColor_specs}{textStyle_specs}{borderStyle_specs}"
#         self.setStyleSheet(complete_style)
#         # label.setFont(QFont('Arial', 18)) -> Other way to set the Font
        
#         # ajust the size of the label according to its style font and border. Then redefine the size of the widget according to the size of the geometry of the label 
#         self.adjustSize()   
#         self.setFixedSize(self.geometry().size())

        
        
#         self.setParent(parent)
 