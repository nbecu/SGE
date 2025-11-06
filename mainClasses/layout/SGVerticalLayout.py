from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.layout.SGAbstractLayout import SGAbstractLayout


#Class that manage the vertical layout
class SGVerticalLayout(SGAbstractLayout):
    
    #Calculate the space needed for a GameSpaces involving the others
    def calculateSize(self,aGameSpace):
        size=0
        for i in range(self.count):
            if self.GameSpaces[i].id == aGameSpace.id:
                break;
            else:
                size=size+self.GameSpaces[i].getSizeYGlobal()
        return (self.leftMargin , size + self.topMargin)
 
    
    #Re allocate the space of the model
    def reAllocateSpace(self):
        for i in range(self.count) :
            self.GameSpaces[i].setStartYBase (self.calculateSize(self.GameSpaces[i])[1])
     
    #To have the maximum value of the item displayed into the layout
    def getMax(self):
        maxX=0
        maxY=0
        for anElement in self.GameSpaces:
            maxX = maxX+anElement.getSizeXGlobal()
            if maxY< anElement.getSizeYGlobal() :
                maxY=anElement.getSizeYGlobal()
        return (maxX,maxY)
    
    def applyLayout(self, gameSpaces):
        """
        Apply vertical layout to gameSpaces
        """
        self.ordered()
        aGap = self.gapBetweenGameSpaces
        for aGameSpace in (element for element in gameSpaces if not element.isPositionDefineByModeler()):
            aGameSpace.move(aGameSpace.startXBase,
                           aGameSpace.startYBase + (aGap * (self.getNumberOfAnElement(aGameSpace) - 1)))
              
        
                    