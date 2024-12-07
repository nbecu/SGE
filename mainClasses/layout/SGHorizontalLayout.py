from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.layout.SGAbstractLayout import SGAbstractLayout


#Class that manage the horizontal layout
class SGHorizontalLayout(SGAbstractLayout):
 
    #Calculate the space needed for a GameSpaces involving the others
    def calculateSize(self,aGameSpace):
        size=0
        for i in range(self.count):
            if self.GameSpaces[i].id == aGameSpace.id:
                break;
            else:
                size=size+self.GameSpaces[i].getSizeXGlobal()
        return (size + self.leftMargin , self.topMargin)

    
    #Re allocate the space of the model
    def reAllocateSpace(self):
        for i in range(self.count) :
            self.GameSpaces[i].setStartXBase(self.calculateSize(self.GameSpaces[i])[0])
            
    #To have the maximum value of the item displayed into the layout
    def getMax(self):
        maxX=0
        maxY=0
        for anElement in self.GameSpaces:
            maxY = maxY+anElement.getSizeYGlobal()
            if maxX< anElement.getSizeXGlobal() :
                maxX=anElement.getSizeXGlobal()
        return (maxX,maxY)
            
    