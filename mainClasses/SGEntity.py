from tkinter.ttk import Separator
from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.gameAction.SGGameActions import SGGameActions
from sqlalchemy import true
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsView, QGraphicsScene
import random
import re

# Class who is in charged of entities : cells and agents
class SGEntity(QtWidgets.QWidget):
    def __init__(self,parent,name,format,defaultsize,dictOfAttributs,id,me,uniqueColor=Qt.white,methodOfPlacement="random"):
        super().__init__(parent)