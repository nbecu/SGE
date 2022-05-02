
from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *


   
#Class who is responsible of the declaration a cell
class SGCell(QtWidgets.QWidget):
    def __init__(self,x, y,format="square",size=32,color="blue",aPov="default", parent=None):
        super().__init__()
        self.layout = QtWidgets.QGridLayout() 
        self.setLayout(self.layout) 
        #Definition of variables
        self.x = x
        self.y = y
        self.format=format
        self.size = size
        self.povs=dict()
        
        
    def changeThePovValue(self,aNameOfPov,aValue):
        self.povs[aNameOfPov]=aValue

        
    def getColorOfThePovValue(self,aNameOfPov):
        return self.povs[aNameOfPov]
#-----------------------------------------------------------------------------------------
#Definiton of the methods who the modeler will use
    

        
    
        
    