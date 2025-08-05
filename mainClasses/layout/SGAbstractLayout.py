from PyQt5.QtGui import *
from PyQt5.QtCore import *
from abc import ABC, abstractmethod


#Class that defines the generic methods of a layout
class SGAbstractLayout():
    def __init__(self):
        self.count=0
        self.GameSpaces=[]
        self.topMargin = 23 #23 pixels to leave space at top because of menuBar
        self.leftMargin = 1 #1 pixel to leave a very thin margin at left
        self.gapBetweenGameSpaces = 20 #10 pixels to leave a margin between 2 gamespaces
    
    #Return the number of element
    def getNumberOfElement(self):
        return self.count
    
    #Return the number of an element
    def getNumberOfAnElement(self,aGameSpace):
        count=1
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
    @abstractmethod # This method must be overridden by subclasses
    def calculateSize(self, aGameSpace): 
        pass  
    
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
            
    