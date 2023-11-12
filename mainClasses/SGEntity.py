from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import random
from mainClasses.gameAction.SGGameActions import SGGameActions

# Class who is in charged of entities : cells and agents
class SGEntity(QtWidgets.QWidget):
    def __init__(self,parent,classDef,size,shapeColor,attributesAndValues):
        super().__init__(parent)
        self.classDef=classDef
        self.id=self.classDef.nextId()
        self.privateID = self.classDef.entityName+str(self.id)
        self.model=self.classDef.model
        self.shape= self.classDef.shape
        self.size=size
        self.color=shapeColor
        self.borderColor=self.classDef.defaultBorderColor
        self.isDisplay=True
        #Define variables to handle the history 
        self.history={}
        self.history["value"]=[]
        #Set the attributes
        self.initAttributesAndValuesWith(attributesAndValues)
        self.owner="admin"

    
    def initAttributesAndValuesWith(self, thisAgentAttributesAndValues):
        self.dictAttributes={}
        if thisAgentAttributesAndValues is None : thisAgentAttributesAndValues={}
        for aAtt in self.classDef.attributesPossibleValues.keys():
            if aAtt in thisAgentAttributesAndValues.keys():
                valueToSet = thisAgentAttributesAndValues[aAtt]
            elif aAtt in self.classDef.attributesDefaultValues.keys():
                valueToSet = self.classDef.attributesDefaultValues[aAtt]
            else: valueToSet = None
            if callable(valueToSet):
                self.setValue(aAtt,valueToSet())
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

    def getColor(self):
        if self.isDisplay==False: return Qt.transparent
        # replace the search of model name of pov by getCheckedSymbologyNameOfEntity (which look for the symbolgy which is checked for this item in the menu)
        aChoosenPov = self.model.getCheckedSymbologyOfEntity(self.classDef.entityName)
        aPovDef = self.classDef.povShapeColor.get(aChoosenPov) #self.model.nameOfPov
        aDefaultColor= self.classDef.defaultShapeColor
        return self.readColorFromPovDef(aPovDef,aDefaultColor)
      
    
    def getBorderColor(self):
        if self.isDisplay==False: return Qt.transparent
        aPovDef = self.classDef.povBorderColor.get(self.model.nameOfPov)
        aDefaultColor= self.classDef.defaultBorderColor
        return self.readColorFromPovDef(aPovDef,aDefaultColor)

    
    def getBorderWidth(self):
        # if self.me == 'agent':
        #     return int(1)
        # if self.me == 'cell':
        #     grid=self.grid
        #     if self.model.cellCollection[grid.id]["BorderPOV"] is not None and self.grid.model.nameOfPov in self.model.cellCollection[grid.id]["BorderPOV"].keys():
        #             return int(self.model.cellCollection[grid.id]["BorderPOV"]["BorderWidth"])
            return int(1)
    
    #To get the pov
    def getPov(self):
        return self.model.nameOfPov

    def getRandomXY(self):
        x = 0
        maxSize=self.cell.size
        x = random.randint(1,maxSize-1)
        return x

    def mousePressEvent(self, event):
       if event.button() == Qt.LeftButton:
            #Something is selected
            aLegendItem = self.model.getSelectedLegendItem()
            if aLegendItem is None : return #Exit the method

            authorisation=SGGameActions.getActionPermission(self)
        
            #The delete Action
            if aLegendItem.type == 'delete' : #or self.grid.model.selected[2].split()[0]== "Remove" :
                if authorisation : 
                    #We now check the feedBack of the actions if it have some
                    """if theAction is not None:
                        self.feedBack(theAction)"""
                    if len(self.agents) !=0:
                        self.deleteAllAgents()
                    self.classDef.deleteEntity(self)

                    if self.model.mqttMajType == "Instantaneous":
                        SGGameActions.sendMqttMessage(self)
                    self.show()
                    self.repaint()    

            #The Replace cell and change value Action
            elif aLegendItem.isValueOnCell():
                if  authorisation :
                    #We now check the feedBack of the actions if it have some
                    if not aLegendItem.legend.isAdminLegend():
                        self.owner=self.grid.model.currentPlayer
                    if self.isDeleted() : self.classDef.reviveThisCell(self) 
                    self.setValue(aLegendItem.nameOfAttribut,aLegendItem.valueOfAttribut)     
                    # self.update() A PRIORI ON PEUT S'EN PASSER   //  C'est peut etre meme cela qui fait tourner un refresh en boucle

            #The  change value on agent
            elif aLegendItem.isValueOnAgent() :
                if  authorisation :
                    self.setValue(aLegendItem.nameOfAttribut,aLegendItem.valueOfAttribut)     
                    # self.update() A PRIORI ON PEUT S'EN PASSER   //  C'est peut etre meme cela qui fait tourner un refresh en boucle                    

            #For agent placement         
            else :
                if  authorisation :
                    aDictWithValue={self.grid.model.selected[4]:self.grid.model.selected[3]}
                    if self.grid.model.selected[4] =="empty" or self.grid.model.selected[3]=='empty':
                        Species=self.grid.model.selected[2]
                    elif self.grid.model.selected[4] ==None or self.grid.model.selected[3]==None:
                        Species=self.grid.model.selected[2]
                    elif ":" in self.grid.model.selected[2] :
                        selected=self.grid.model.selected[2]
                        chain=selected.split(' : ')
                        Species = chain[0]
                    else:
                        Species=re.search(r'\b(\w+)\s*:', self.grid.model.selected[5]).group(1)
                    if self.isDisplay==True :
                        #We now check the feedBack of the actions if it have some
                        """if theAction is not None:
                            self.feedBack(theAction)"""
                        theSpecies = self.model.getAgentSpecie(Species)
                        aAgent=self.newAgentHere(theSpecies,aDictWithValue)
                        self.updateIncomingAgent(aAgent)
                        for method in self.model.agentSpecies[Species]["watchers"]:
                            for watcher in self.model.agentSpecies[Species]["watchers"][method]:
                                updatePermit=watcher.getUpdatePermission()
                                if updatePermit:
                                    watcher.updateText()
                        for method in self.model.agentSpecies['agents']["watchers"]:
                            for watcher in self.model.agentSpecies['agents']["watchers"][method]:
                                updatePermit=watcher.getUpdatePermission()
                                if updatePermit:
                                    watcher.updateText()
                        if self.model.mqttMajType == "Instantaneous":
                            SGGameActions.sendMqttMessage(self)
                        self.update()
                        self.grid.model.update()

    def updateMqtt(self):
        if self.model.mqttMajType == "Instantaneous":
            SGGameActions.sendMqttMessage(self)

    def saveHistoryValue(self):
        if len(self.history["value"])==0:
            self.history["value"].append([0,0,self.dictAttributes]) #correspond à round 0 phase 0
        self.history["value"].append([self.model.timeManager.currentRound,self.model.timeManager.currentPhase,self.dictAttributes])


    #To handle the attributs and values
    def setValue(self,aAttribut,aValue):
        """
        Sets the value of an attribut
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be set
        """
        if self.model.round()!=0 and not aAttribut in self.dictAttributes: raise ValueError("Not such an attribute")
        if aAttribut in self.dictAttributes and self.dictAttributes[aAttribut]==aValue: return False #The attribute has already this value
        self.saveHistoryValue()    
        self.dictAttributes[aAttribut]=aValue

        self.classDef.updateWatchersOnAttribute(aAttribut)
        self.updateMqtt()
        return True

    def value(self,att):
        """
        Return the value of a cell Attribut
        Args:
            att (str): Name of the attribute
        """
        return self.dictAttributes[att]
    
    def incValue(self,aAttribut,aValue=1,max=None):
        """
        Increase the value of an attribut with an additional value
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be added to the current value of the attribute
        """       
        self.dictAttributes[aAttribut]= (self.value(aAttribut)+aValue if max is None else min(self.value(aAttribut)+aValue,max))

    def decValue(self,aAttribut,aValue=1,min=None):
        """
        Decrease the value of an attribut with an additional value
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be subtracted to the current value of the attribute
        """       
        self.dictAttributes[aAttribut]= (self.value(aAttribut)-aValue if min is None else max(self.value(aAttribut)-aValue,min))
