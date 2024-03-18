from PyQt5.QtGui import *
from PyQt5.QtCore import *

#Class that manage the horizontal layout
class SGHorizontalLayout():
    def __init__(self):
        self.count=0
        self.GameSpaces=[]
    
    #Return the number of element
    def getNumberOfElement(self):
        return self.count
    
    #Return the number of an element
    def getNumberOfAnElement(self,aGameSpace):
        count=0
        for anElement in self.GameSpaces:
            if anElement.id==aGameSpace.id:
                return count
            count=count+1
    
    #Add a game space to the layout and return the basic position
    def addGameSpace(self,aGameSpace):
        self.count=self.count+1
        self.GameSpaces.append(aGameSpace)
        size=self.calculateSize(aGameSpace)
        return size
    
    #Calculate the space needed for a GameSpaces involving the others
    def calculateSize(self,aGameSpace):
        size=20     #30 instead of 20 to leave space at top because of menuBar
        for i in range(self.count):
            if self.GameSpaces[i].id == aGameSpace.id:
                break;
            else:
                size=size+self.GameSpaces[i].getSizeXGlobal()
        return (size,40)
    
    #Ordered all gameSpaces and reAllocate the space of the model
    def ordered(self):
        ordered= []
        for i in range(self.count):
            for j in range(self.count) :
                if i == self.GameSpaces[j].posXInLayout :
                    ordered.append(self.GameSpaces[j])
        self.GameSpaces=ordered
        return self.reAllocateSpace()  
    
    #Re allocate the space of the model
    def reAllocateSpace(self):
        for i in range(self.count) :
            self.GameSpaces[i].startXBase = self.calculateSize(self.GameSpaces[i])[0]
            
    #To have the maximum value of the item displayed into the layout
    def getMax(self):
        maxX=0
        maxY=0
        for anElement in self.GameSpaces:
            maxY = maxY+anElement.getSizeYGlobal()
            if maxX< anElement.getSizeXGlobal() :
                maxX=anElement.getSizeXGlobal()
        return (maxX,maxY)
            
    