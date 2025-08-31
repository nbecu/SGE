from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true

from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGLegendItem import SGLegendItem


#Class who is responsible of the Legend creation 
class SGLegend(SGGameSpace):
    def __init__(self, parent,backgroundColor=Qt.transparent):
        super().__init__(parent,0,60,0,0,true,backgroundColor)
        self.isLegend=True
        self.isControlPanel=False
        # self.heightOfLabels= 25 #added for CarbonPolis
        self.heightOfLabels= 20 #added for CarbonPolis

    def initialize(self, model, legendName,listOfSymbologies,alwaysDisplayDefaultAgentSymbology=False,borderColor=Qt.black):
        self.id=legendName #todo should be removed as it is managed by the superclass
        self.model=model
        self.alwaysDisplayDefaultAgentSymbology=alwaysDisplayDefaultAgentSymbology
        self.legendItems={}
        self.borderColor=borderColor
        self.updateWithSymbologies(listOfSymbologies)
        return self
    
    
    def clearAllLegendItems(self):
        for aItem in self.legendItems:
            aItem.deleteLater()
        self.legendItems=[]
        
    def updateWithSymbologies(self,listOfSymbologies):
        self.clearAllLegendItems()
        self.listOfSymbologies=listOfSymbologies
        self.posYOfItems = 0
        anItem=SGLegendItem(self,'Title1',self.id)
        self.legendItems.append(anItem)
        for entDef, aDictOfSymbology in self.listOfSymbologies.items():
            anItem=SGLegendItem(self,'Title2',entDef.entityName)
            self.legendItems.append(anItem)
            # aDictOfSymbology is a dict with keys 'shape' and 'border'
            aShapeSymbology = aDictOfSymbology['shape']
            aBorderSymbology = aDictOfSymbology['border']
            if aShapeSymbology is None and aBorderSymbology is None:         
                # Case 1: Default symbology - no POV defined, use entity's default shape color
                # This case corresponds to entities without any POV defined, showing default appearance
                anItem=SGLegendItem(self,'symbol','default',entDef,entDef.defaultShapeColor)
                self.legendItems.append(anItem)
                continue
            if aShapeSymbology is not None:
                # Case 2: Shape symbology - POV for shape color, creates items for each symbol name and color
                # This case corresponds to entities with shape-based POV (e.g., health status affecting color)
                if self.alwaysDisplayDefaultAgentSymbology and entDef.isAgentDef:
                    # Use default symbology for agents without attributes
                    anItem=SGLegendItem(self,'symbol','default',entDef,entDef.defaultShapeColor)
                    self.legendItems.append(anItem)    
                aAtt = list(entDef.povShapeColor[aShapeSymbology].keys())[0]
                dictSymbolNameAndColor= list(entDef.povShapeColor[aShapeSymbology].values())[0]
                for aSymbolName, aColor in dictSymbolNameAndColor.items():
                    anItem=SGLegendItem(self,'symbol',aSymbolName,entDef,aColor,aAtt,aSymbolName)
                    self.legendItems.append(anItem)
            if aBorderSymbology is not None:
                # Case 3: Border symbology - POV for border color and width, creates items for each symbol name
                # This case corresponds to entities with border-based POV (e.g., ownership or status borders)
                aPovBorderDef = entDef.povBorderColorAndWidth.get(aBorderSymbology)
                aAtt = list(aPovBorderDef.keys())[0]
                dictSymbolNameAndColorAndWidth= list(aPovBorderDef.values())[0]
                for aSymbolName, aDictColorAndWidth in dictSymbolNameAndColorAndWidth.items():
                    anItem=SGLegendItem(self,'symbol',aSymbolName,entDef,nameOfAttribut=aAtt,valueOfAttribut=aSymbolName,isBorderItem=True,borderColorAndWidth=aDictColorAndWidth)
                    self.legendItems.append(anItem)

        for anItem in self.legendItems:
            anItem.adjustSize()  #NEW
            anItem.show()
        self.adjustSize()
        # self.setMinimumSize(self.getSizeXGlobal(),10)
        self.setMinimumSize(self.getSizeX_fromAllWidgets(),10)

    def showLegendItem(self, typeOfPov, aAttribut, aValue, color, aKeyOfGamespace, added_items, added_colors):
        item_key=aAttribut +' '+ str(aValue)
        if item_key not in added_items and color not in added_colors and color != Qt.transparent:
            self.y=self.y+1
            anItem=SGLegendItem(self,self.model.getGameSpaceByName(aKeyOfGamespace).format,self.y,aAttribut+" "+str(aValue),color,aValue,aAttribut)
            if typeOfPov == "BorderPOV" :
                anItem.border = True
            self.legendItems[aKeyOfGamespace].append(anItem)
            anItem.show()
            added_items.add(item_key)
            added_colors.append(color)


    #Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        listOfLengths = [len(item.text) for item in self.legendItems]
        listOfLengths.append(len(self.id))
        if len(listOfLengths)==0:
            return 250
        lMax= sorted(listOfLengths,reverse=True)[0]
        return lMax*12+10
    
    def getSizeX_fromAllWidgets(self):
        if self.legendItems:  # Vérifier si la liste n'est pas vide
            max_size_item = max(self.legendItems, key=lambda item: item.geometry().size().width())
            max_width = max_size_item.geometry().size().width()
        else:
            max_width = 30  # Ou une autre valeur par défaut
        return max_width + 10
    
    def getSizeYGlobal(self):
        return (self.heightOfLabels)*(len(self.legendItems)+1)
    
    #Funtion to handle the zoom
    def zoomIn(self):
        """IN PROGRESS"""
        return True
    
    def zoomOut(self):
        """IN PROGRESS"""
        return True 
        
    #Drawing the Legend
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.gs_aspect.getBackgroundColorValue(), Qt.SolidPattern))
        painter.setPen(QPen(self.borderColor,1))
        #Draw the corner of the Legend
        # self.setMinimumSize(self.getSizeXGlobal()+3, self.getSizeYGlobal()+3)
        # painter.drawRect(0,0,self.getSizeXGlobal(), self.getSizeYGlobal())     
        self.setMinimumSize(self.getSizeX_fromAllWidgets(), self.getSizeYGlobal()+3)
        painter.drawRect(0,0,self.getSizeX_fromAllWidgets()-1, self.getSizeYGlobal())

        painter.end()

    

    #obsolete function
    # def checkSpecie(self,item_key,items):
    #     for legendItem in items:
    #         if item_key in legendItem.text:
    #             return False
    #     return True
