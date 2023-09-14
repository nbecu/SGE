from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from PyQt5.QtWidgets import  QAction, QGraphicsRectItem, QGraphicsView, QGraphicsScene
import random
from mainClasses.gameAction.SGGameActions import SGGameActions
from mainClasses.SGGameSpace import SGGameSpace

class SGnewAgent(SGGameSpace):
    instances=[]

    def __init__(self, parent, id, shape, defaultsize, dictOfAttributs, me, uniqueColor=Qt.white, methodOfPlacement="random"):
        super().__init__(parent, 0, 60, 0, 0, true, uniqueColor)

        self.me=me
        self.model=parent