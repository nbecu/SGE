from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *




            
class SGGridLayout():
    def __init__(self,x,y):
        self.count=0
        self.x=x
        self.y=y
        #Init of the grid
        self.listOfGameSpace=[]
        for i in range(self.y):
            self.listOfGameSpace.append([])
        
    
    #Return the number of element
    def getNumberOfElement(self):
        return self.count
    
    #Add a game space to the layout and return the basic position
    def addGameSpace(self,aGameSpace):
        self.count=self.count+1
        aListe = self.listOfGameSpace[((self.count-1)%self.y)]
        if len(aListe)<self.x and self.foundInLayout(aGameSpace) is None:
            aListe.append(aGameSpace)
        size=size=self.calculateSize(aGameSpace)
        return size
    
    #Calculate the space needed for a GameSpaces involving the others
    def calculateSize(self,aGameSpace):
        sizeX=20
        sizeY=40
        found= self.foundInLayout(aGameSpace)
        colonneTrouve=found[0]
        ligneTrouve=found[1]
        #We shearch the size of the column so in Y
        for i in range(self.y):
            if i<ligneTrouve :
                sizeY=sizeY+self.listOfGameSpace[colonneTrouve][i].getSizeYGlobal()
        #We shearch the size of the row so in X
        
        for i in range(self.x):
            if i<colonneTrouve :
                sizeX=sizeX+self.listOfGameSpace[i][ligneTrouve].getSizeXGlobal()
        return (sizeX,sizeY)
    
    #Found in layout a gameSpace
    def foundInLayout(self,aGameSpace):
        count=0
        for aListe in self.listOfGameSpace:
            if aGameSpace in aListe:
                countX=0
                for element in aListe:
                    if element.id==aGameSpace.id :
                        return (count,countX)
                    countX=countX+1
            count=count+1
        return None
    
    #Ordered all gameSpaces and reAllocate the space of the model
    def ordered(self):
        print(self.listOfGameSpace)
        ordered=[]
        for i in range(self.y):
            ordered.append([])
        
        
        for aList in self.listOfGameSpace :
            for anElement in aList :
                count=0
                for aGameSpace in ordered[anElement.posYInLayout] :
                    if aGameSpace.posXInLayout<anElement.posXInLayout:
                        count=count+1
                    
                ordered[anElement.posYInLayout].insert(count,anElement)
                    
                    
        self.listOfGameSpace=ordered
        print(self.listOfGameSpace)
        self.reAllocateSpace()  
    
    #Re allocate the space of the model
    def reAllocateSpace(self):
        """for i in range(self.count) :
            self.listOfGameSpace[i].startYBase = self.calculateSize(self.listOfGameSpace[i])[1] +20*i +20"""
        for aList in self.listOfGameSpace :
            for anElement in aList :
                size=self.calculateSize(anElement)
                anElement.startXBase=size[0]
                anElement.startYBase=size[1]
            
            
        
        
        