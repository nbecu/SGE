from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import null

class SGVerticalLayout():
    def __init__(self):
        self.count=0
        self.listOfGameSpace=[]
    
    #Return the number of element
    def getNumberOfElement(self):
        return self.count
    
    #Return the number of an element
    def getNumberOfAnElement(self,aGameSpace):
        count=0
        for anElement in self.listOfGameSpace:
            if anElement.id==aGameSpace.id:
                return count
            count=count+1
    
    #Add a game space to the layout and return the basic position
    def addGameSpace(self,aGameSpace):
        self.count=self.count+1
        self.listOfGameSpace.append(aGameSpace)
        size=self.calculateSize(aGameSpace)
        return size
    
    #Calculate the space needed for a GameSpaces involving the others
    def calculateSize(self,aGameSpace):
        size=20
        for i in range(self.count):
            if self.listOfGameSpace[i].id == aGameSpace.id:
                break;
            else:
                size=size+self.listOfGameSpace[i].getSizeYGlobal()
        return (20,size)
    
    #Ordered all gameSpaces and reAllocate the space of the model
    def ordered(self):
        ordered= []
        for i in range(self.count):
            for j in range(self.count) :
                if i == self.listOfGameSpace[j].posYInLayout :
                    ordered.append(self.listOfGameSpace[j])
        self.listOfGameSpace=ordered
        self.reAllocateSpace()  
    
    #Re allocate the space of the model
    def reAllocateSpace(self):
        for i in range(self.count) :
            self.listOfGameSpace[i].startYBase = self.calculateSize(self.listOfGameSpace[i])[1]
            
        
                    