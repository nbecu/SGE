from PyQt5.QtGui import *
from PyQt5.QtCore import *

#Class that manage the vertical layout
class SGVerticalLayout():
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
        size=30
        for i in range(self.count):
            if self.GameSpaces[i].id == aGameSpace.id:
                break;
            else:
                size=size+self.GameSpaces[i].getSizeYGlobal()
        return (20,size)
    
    #Ordered all gameSpaces and reAllocate the space of the model
    def ordered(self):
        ordered= []
        for i in range(self.count):
            for j in range(self.count) :
                if i == self.GameSpaces[j].posYInLayout :
                    ordered.append(self.GameSpaces[j])
        self.GameSpaces=ordered
        self.reAllocateSpace()  
    
    #Re allocate the space of the model
    def reAllocateSpace(self):
        for i in range(self.count) :
            self.GameSpaces[i].startYBase = self.calculateSize(self.GameSpaces[i])[1]
     
    #To have the maximum value of the item displayed into the layout
    def getMax(self):
        maxX=0
        maxY=0
        for anElement in self.GameSpaces:
            maxX = maxX+anElement.getSizeXGlobal()
            if maxY< anElement.getSizeYGlobal() :
                maxY=anElement.getSizeYGlobal()
        return (maxX,maxY)
              
        
                    