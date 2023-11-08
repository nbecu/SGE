from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null
import numpy as np
from mainClasses.SGCell import SGCell
from mainClasses.SGAgent import SGAgent


   
#Class who is responsible of indicator creation 
class SGSimulationVariables():
    def __init__(self,parent,initValue,name,color,isDisplay=True):
        #Basic initialize
        self.model=parent
        self.value=initValue
        self.name=name
        self.color=color
        self.isDisplay=isDisplay
        

    def updateValue(self,newValue):
        self.value=newValue