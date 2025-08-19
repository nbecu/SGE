from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from collections import defaultdict
import random
from mainClasses.AttributeAndValueFunctionalities import *
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QMessageBox, QDialog, QLabel, QVBoxLayout
from mainClasses.SGEventHandlerGuide import *

# Class who is in charged of entities : cells and agents
class SGEntity(QtWidgets.QWidget, SGEventHandlerGuide, AttributeAndValueFunctionalities):
    def __init__(self,parent,classDef,size,attributesAndValues):
        super().__init__(parent)
        self.classDef=classDef
        self.id=self.classDef.nextId()
        self.privateID = self.classDef.entityName+str(self.id)
        self.model=self.classDef.model
        self.shape= self.classDef.shape
        self.size=size
        self.borderColor=self.classDef.defaultBorderColor
        self.isDisplay=True
        #Define variables to handle the history 
        self.history={}
        self.history["value"]=defaultdict(list)
        # self.list_history = []
        self.watchers={}
        #Set the attributes
        self.initAttributesAndValuesWith(attributesAndValues)
        self.owner="admin"
        # define highlighting
        self.highlightEffect = None
        self.isHighlighted = False
        # set the contextual and gameAction controller
        self.init_contextMenu()

    
    def initAttributesAndValuesWith(self, thisAgentAttributesAndValues):
        self.dictAttributes={}
        if thisAgentAttributesAndValues is None : thisAgentAttributesAndValues={}
        
        for aAtt, aDefaultValue in self.classDef.attributesDefaultValues.items():
            if not aAtt in thisAgentAttributesAndValues.keys():
                thisAgentAttributesAndValues[aAtt]=aDefaultValue
        for aAtt, valueToSet in thisAgentAttributesAndValues.items():
            if callable(valueToSet):
                aValue= valueToSet()
                self.setValue(aAtt,aValue)
            else:
                self.setValue(aAtt,valueToSet)

    def getRandomAttributValue(self,aAgentSpecies,aAtt):
        if aAgentSpecies.dictAttributes is not None:
            values = list(aAgentSpecies.dictAttributes[aAtt])
            number=len(values)
            aRandomValue=random.randint(0,number-1)          
        return aRandomValue


    def readColorFromPovDef(self,aPovDef,aDefaultColor):
        if aPovDef is None: return aDefaultColor
        aAtt=list(aPovDef.keys())[0]
        aDictOfValueAndColor=list(aPovDef.values())[0]
        aColor = aDictOfValueAndColor.get(self.value(aAtt))
        return aColor if aColor is not None else aDefaultColor

    def readColorAndWidthFromBorderPovDef(self,aBorderPovDef,aDefaultColor,aDefaultWidth):
        if aBorderPovDef is None: return {'color':aDefaultColor,'width':aDefaultWidth}
        aAtt=list(aBorderPovDef.keys())[0]
        aDictOfValueAndColorWidth=list(aBorderPovDef.values())[0]
        dictColorAndWidth = aDictOfValueAndColorWidth.get(self.value(aAtt))
        if dictColorAndWidth is None:  # Vérification si la valeur n'existe pas
            raise ValueError(f'BorderPov cannot work because {self.privateID} has no value for attribute "{aAtt}"')
        if not isinstance(dictColorAndWidth,dict): raise ValueError('wrong format')
        return dictColorAndWidth

    def getColor(self):
        if self.isDisplay==False: return Qt.transparent
        aChoosenPov = self.model.getCheckedSymbologyOfEntity(self.classDef.entityName)
        aPovDef = self.classDef.povShapeColor.get(aChoosenPov)
        aDefaultColor= self.classDef.defaultShapeColor
        return self.readColorFromPovDef(aPovDef,aDefaultColor)

    def getBorderColorAndWidth(self):
        if self.isDisplay==False: return Qt.transparent
        aChoosenPov = self.model.getCheckedSymbologyOfEntity(self.classDef.entityName, borderSymbology=True)
        aBorderPovDef = self.classDef.povBorderColorAndWidth.get(aChoosenPov)
        aDefaultColor= self.classDef.defaultBorderColor
        aDefaultWidth=self.classDef.defaultBorderWidth
        return self.readColorAndWidthFromBorderPovDef(aBorderPovDef,aDefaultColor,aDefaultWidth)
    
    def getImage(self):
        if self.isDisplay==False: return None
        aChoosenPov = self.model.getCheckedSymbologyOfEntity(self.classDef.entityName)
        aPovDef = self.classDef.povShapeColor.get(aChoosenPov)
        if aPovDef is None: return None
        aAtt=list(aPovDef.keys())[0]
        aDictOfValueAndImage=list(aPovDef.values())[0]
        aImage = aDictOfValueAndImage.get(self.value(aAtt))     

        if aImage is not None and isinstance(aImage,QPixmap):
            return aImage 
        else:
            return None
    
    def rescaleImage(self, image):
        
        imageWidth = image.width()
        imageHeight = image.height()

        if imageWidth ==0 or imageHeight == 0 : raise ValueError('Image size is not valid')
        # entityWidth = self.width() #could use self.size, instead
        # entityHeight = self.height()  
        entityWidth = self.size
        entityHeight = self.size

        if (imageHeight / imageWidth) < (entityHeight / entityWidth):
            scaled_image = image.scaledToHeight(entityHeight, Qt.SmoothTransformation)
        else:
            scaled_image = image.scaledToWidth(entityWidth, Qt.SmoothTransformation)
        # Calculer le rectangle cible pour le dessin
        x_offset = (entityWidth - scaled_image.width()) // 2
        y_offset = (entityHeight - scaled_image.height()) // 2
        target_rect = QRect(x_offset, y_offset, scaled_image.width(), scaled_image.height())

        return target_rect, scaled_image
   
    # def toggleHighlight(self):
    #     if self.isHighlighted:
    #         self.setGraphicsEffect(None)
    #     else:
    #         self.highlightEffect = QtWidgets.QGraphicsColorizeEffect()
    #         self.highlightEffect.setColor(QColor("yellow"))
    #         self.setGraphicsEffect(self.highlightEffect)
        
    #     self.isHighlighted = not self.isHighlighted

    # Handle the contextual menu and GameAction controller
    def init_contextMenu(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_contextMenu)
    
    def show_contextMenu(self, point):
        menu = QMenu(self)

        for anItem in self.classDef.attributesToDisplayInContextualMenu:
            aAtt = anItem['att']
            aLabel = anItem['label']
            aValue = self.value(aAtt)
            text = aLabel  + "="+str(aValue)
            option = QAction(text, self)
            menu.addAction(option)

        player=self.model.getCurrentPlayer()
        if not player == "Admin":        
            actions = player.getAllGameActionsOn(self)
            for aAction in actions:
                if aAction.setControllerContextualMenu:
                        if aAction.checkAuthorization(self):
                            aMenuAction=QAction(aAction.nameToDisplay,self)
                            aMenuAction.setCheckable(False)
                            aMenuAction.triggered.connect(lambda _, a=aAction: a.perform_with(self))
                            menu.addAction(aMenuAction)


        if not menu.isEmpty() and self.rect().contains(point):
            menu.exec_(self.mapToGlobal(point))

    
    def getObjectIdentiferForJsonDumps(self):
        dict ={}
        dict['entityName']=self.classDef.entityName
        dict['id']=self.id
        return dict
    
    def addWatcher(self,aIndicator):
        aAtt = aIndicator.attribute
        if aAtt not in self.watchers.keys():
            self.watchers[aAtt]=[]
        self.watchers[aAtt].append(aIndicator)

    def updateWatchersOnAttribute(self,aAtt):
        for watcher in self.watchers.get(aAtt,[]):
            watcher.checkAndUpdate()

    def getListOfStepsData(self,startStep=None,endStep=None):
        aList=self.getListOfUntagedStepsData(startStep,endStep)
        return [{**{'entityType': self.classDef.entityType(),'entityName': self.classDef.entityName,'id': self.id},**aStepData} for aStepData in aList]

    
    def isDeleted(self):
        return not self.isDisplay


    #To perform action --> Check if this method is used or not
    def doAction(self, aLambdaFunction):
        aLambdaFunction(self)


    def entDef(self):
        """
        Returns the 'entity definition' class of the entity
        """        
        return self.classDef
    
