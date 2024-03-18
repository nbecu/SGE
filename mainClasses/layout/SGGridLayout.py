from PyQt5.QtGui import *
from PyQt5.QtCore import *


#Class that manage the grid layout
class SGGridLayout():
    def __init__(self,x,y):
        self.count=0
        self.x=x
        self.y=y
        #Init of the grid
        self.GameSpaces=[]
        for i in range(self.y):
            self.GameSpaces.append([])
        
    
    #Return the number of element
    def getNumberOfElement(self):
        return self.count
    
    #Add a game space to the layout and return the basic position
    def addGameSpace(self,aGameSpace):
        self.count=self.count+1
        aListe = self.GameSpaces[((self.count-1)%self.y)]
        aGameSpace.posYInLayout=((self.count-1)%self.y)
        if len(aListe)<self.x and self.foundInLayout(aGameSpace) is None:
            aGameSpace.posXInLayout=len(aListe)
            aListe.append(aGameSpace)
        size=size=self.calculateSize(aGameSpace)
        return size
    
    #Calculate the space needed for a GameSpaces involving the others
    def calculateSize(self,aGameSpace):
        sizeX=20
        sizeY=30    #30 instead of 20 to leave space at top because of menuBar
        found= self.foundInLayout(aGameSpace)
        colonneTrouve=found[0]
        ligneTrouve=found[1]
        #We shearch the size of the column so in Y
        for i in range(self.y):
            if i<ligneTrouve :
                sizeY=sizeY+self.GameSpaces[colonneTrouve][i].getSizeYGlobal()
        #We shearch the size of the row so in X
        for i in range(self.x):
            if i<colonneTrouve :
                sizeX=sizeX+self.GameSpaces[i][ligneTrouve].getSizeXGlobal()
        return (sizeX,sizeY)
    
    #Found in layout a gameSpace
    def foundInLayout(self,aGameSpace):
        count=0
        for aListe in self.GameSpaces:
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
        ordered=[]
        for i in range(self.y):
            ordered.append([])
        
        
        for aList in self.GameSpaces :
            for anElement in aList :
                count=0
                for aGameSpace in ordered[anElement.posYInLayout] :
                    if aGameSpace.posXInLayout<anElement.posXInLayout:
                        count=count+1
                    
                ordered[anElement.posYInLayout].insert(count,anElement)
                    
                    
        self.GameSpaces=ordered
        self.reAllocateSpace()  
    
    #Re allocate the space of the model
    def reAllocateSpace(self):
        for aList in self.GameSpaces :
            for anElement in aList :
                size=self.calculateSize(anElement)
                anElement.startXBase=size[0]
                anElement.startYBase=size[1]
                
                
    #To have the maximum value of the item displayed into the layout           
    def getMax(self):
        maxX=0
        maxY=0
        for aColumn in self.GameSpaces:
            tempMaxY=0
            for anElement in aColumn:
                tempMaxY = tempMaxY+anElement.getSizeYGlobal()
            if maxY<tempMaxY :
                    maxY=tempMaxY
                    
        for i in range(self.x):
            tempMaxX=0
            for j in range(self.y):
                if len(self.GameSpaces[j])>i :
                    tempMaxX=tempMaxX+self.GameSpaces[j][i].getSizeXGlobal()
            if maxX<tempMaxX:
                maxX=tempMaxX
            
        return (maxX,maxY)
            
            
        
        
        