from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
# from PyQt5.QtWidgets import QStyleFactory
# from mainClasses.SGGameSpace import SGGameSpace


class SGLabel(QtWidgets.QWidget):
    def __init__(self, parent, text, position=(20,20), textStyle_specs="", borderStyle_specs="", backgroundColor_specs="",  alignement= "Left", fixedWidth=None, fixedHeight=None):
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

        self.move(position[0], position[1])
 
  
