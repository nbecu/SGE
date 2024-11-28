from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
# from PyQt5.QtWidgets import QStyleFactory
# from mainClasses.SGGameSpace import SGGameSpace


class SGLabel(QtWidgets.QWidget):
    def __init__(self, parent, text, position=(20,20), textStyle_specs="", borderStyle_specs="", backgroundColor_specs=""):
        super().__init__(parent)
        self.model = parent
        self.moveable = True
        self.isDisplay = True
        
        label = QtWidgets.QLabel(text, self) 
        # self.labelBox.setWordWrap(True)  # Permettre le retour à la ligne si le texte est trop long

        label.setStyleSheet(backgroundColor_specs+textStyle_specs+borderStyle_specs)  
                # label.setFont(QFont('Arial', 18)) -> Other way to set the Font
        
        # ajust the size of the label according to its style font and border. Then redefine the size of the widget according to the size of the geometry of the label 
        label.adjustSize()   
        self.setMinimumSize(label.geometry().size())

        self.move(position[0], position[1])
 
  
