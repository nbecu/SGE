from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGCell import SGCell
from mainClasses.SGAgent import SGAgent
from mainClasses.AttributeAndValueFunctionalities import *
import numpy as np
from collections import Counter
import random

# Définition de SGEntityDef
class SGEntityDef(AttributeAndValueFunctionalities):
    def __init__(self, sgModel, entityName, shape, defaultsize, entDefAttributesAndValues, defaultShapeColor):
        self.model = sgModel
        self.entityName = entityName
        self.dictAttributes = entDefAttributesAndValues if entDefAttributesAndValues is not None else {}
        self.attributesDefaultValues = {}
        self.shape = shape
        self.defaultsize = defaultsize
        self.defaultShapeColor = defaultShapeColor
        self.defaultBorderColor = Qt.black
        self.defaultBorderWidth = 1
        self.povShapeColor = {}
        self.povBorderColorAndWidth = {}
        self.shapeColorClassif = {}  # Classif will replace pov
        self.borderColorClassif = {}  # Classif will replace pov
        self.watchers = {}
        self.IDincr = 0
        self.entities = []
        self.initAttributes(entDefAttributesAndValues)
        self.listOfStepStats = []
        self.attributesToDisplayInContextualMenu = []
        self.updateMenu = False
        self.attributesToDisplayInUpdateMenu = []

    def nextId(self):
        self.IDincr +=1
        return self.IDincr
    
    def entityType(self):
        if isinstance(self,SGCellDef): return 'Cell'
        elif isinstance(self,SGAgentDef): return 'Agent'
        else: raise ValueError('Wrong or new entity type')

    ###Definition of the developer methods
    def addWatcher(self,aIndicator):
        if aIndicator.attribute is None:
            aAtt = 'nb'
        else: aAtt = aIndicator.attribute
        if aAtt not in self.watchers.keys():
            self.watchers[aAtt]=[]
        self.watchers[aAtt].append(aIndicator)

    def updateWatchersOnAttribute(self,aAtt):
        for watcher in self.watchers.get(aAtt,[]):
            watcher.checkAndUpdate()

    def updateWatchersOnAllAttributes(self):
        for aAtt, listOfWatchers in self.watchers.items():
            if aAtt == 'nb': continue
            for watcher in listOfWatchers:
                watcher.checkAndUpdate()

    def updateWatchersOnPop(self):
        self.updateWatchersOnAttribute('nb')
    
    def updateAllWatchers(self):
        for listOfWatchers in self.watchers.values():
            for watcher in listOfWatchers:
                watcher.checkAndUpdate()
                    
    def  getColorOrColorandWidthOfFirstOccurenceOfAttAndValue(self, att, value):
        # Check first the shape colorDict 
        for aDictWith_Att_ColorDict in list(self.povShapeColor.values()):
            aAtt=list(aDictWith_Att_ColorDict.keys())[0]
            aColorDict=aDictWith_Att_ColorDict[aAtt]
            if aAtt == att:
                aColor = aColorDict.get(value)
                if aColor is not None: return aColor
        #Then check if there is a correspondance in the border colorDict
        for aDictWith_Att_ColorDict in list(self.povBorderColorAndWidth.values()):
            aAtt=list(aDictWith_Att_ColorDict.keys())[0]
            aDictOfDictsOfColorAndWidth=aDictWith_Att_ColorDict[aAtt]
            if aAtt == att:
                dictOfColorAndWidth = aDictOfDictsOfColorAndWidth.get(value)
                return dictOfColorAndWidth
        # If no matches are found, retunr the default color
        return self.defaultShapeColor

    ###Definiton of the methods who the modeler will use
    def setDefaultValue(self, aAtt, aDefaultValue):
        self.attributesDefaultValues[aAtt] = aDefaultValue
    
    def setDefaultValues(self, aDictOfAttributesAndValues):
        for att, defValue in aDictOfAttributesAndValues.items():
            self.attributesDefaultValues[att] = defValue



    #To set up a POV
    def newPov(self,nameOfPov,concernedAtt,dictOfColor):
        """
        Declare a new Point of View for the Species.

        Args:
            self (Species object): aSpecies
            nameOfPov (str): name of POV, will appear in the interface
            concernedAtt (str): name of the attribut concerned by the declaration
            DictofColors (dict): a dictionary with all the attribut values, and for each one a Qt.Color (https://doc.qt.io/archives/3.3/qcolor.html)
            
        """
        self.povShapeColor[nameOfPov]={str(concernedAtt):dictOfColor}
        self.model.addClassDefSymbologyinMenuBar(self,nameOfPov)
        if len(self.povShapeColor)==1:
            self.displayPov(nameOfPov)

    def displayPov(self,nameOfPov):
        """
        Displays the symbology for the specified Point of View.
        Args:
            nameOfPov (str): The name of the Point of View to display.
        """
        self.model.checkSymbologyinMenuBar(self,nameOfPov)

    def displayBorderPov(self,nameOfBorderPov):
        """
        Displays the border symbology for the specified Point of View.
        Args:
            nameOfBorderPov (str): The name of the border Point of View to display.
        """
        self.model.checkSymbologyinMenuBar(self,nameOfBorderPov,borderSymbology=True)

    def newBorderPov(self, nameOfPov, concernedAtt, dictOfColor, borderWidth=3):
        """
        Declare a new Point of View (only for border color).
        Args:
            nameOfPov (str): name of POV, will appear in the interface
            aAtt (str): name of the attribut
            DictofColors (dict): a dictionary with all the attribut values, and for each one a Qt.Color (https://doc.qt.io/archives/3.3/qcolor.html)        """
        dictOfColorAndWidth = self.addWidthInPovDictOfColors(borderWidth,dictOfColor)
        self.povBorderColorAndWidth[nameOfPov]={str(concernedAtt):dictOfColorAndWidth}
        self.model.addClassDefSymbologyinMenuBar(self,nameOfPov,isBorder=True)

    def newBorderPovColorAndWidth(self, nameOfPov, concernedAtt, dictOfColorAndWidth):
        """
        Declare a new Point of View (only for border color).
        Args:
            nameOfPov (str): name of POV, will appear in the interface
            aAtt (str): name of the attribut
            DictofColorsAndWidth (dict): a dictionary with all the attribut values, and for each one a Qt.Color (https://doc.qt.io/archives/3.3/qcolor.html)
        """
        dictOfColorAndWidth = self.reformatDictOfColorAndWidth(dictOfColorAndWidth)
        self.povBorderColorAndWidth[nameOfPov]={str(concernedAtt):dictOfColorAndWidth}
        self.model.addClassDefSymbologyinMenuBar(self,nameOfPov,isBorder=True)


    def addWidthInPovDictOfColors(self,borderWidth,dictOfColor):
        dictOfColorAndWidth ={}
        for aKey, aColor in dictOfColor.items():
            dictOfColorAndWidth[aKey] = {'color':aColor,'width':borderWidth}
        return dictOfColorAndWidth
    
    def reformatDictOfColorAndWidth(self,dictOfColorAndWidth):
        reformatedDict ={}
        for aKey, aListOfColorAndWidth in dictOfColorAndWidth.items():
            reformatedDict[aKey] = {'color':aListOfColorAndWidth[0],'width':aListOfColorAndWidth[1]}
        return reformatedDict
    

    def calculateAndRecordCurrentStepStats(self):        
        currentRound =self.model.roundNumber()
        currentPhase = self.model.phaseNumber()
        quantiAttributesStats ={}
        qualiAttributesStats ={}
        if self.entities: 
            listQuantiAttributes = []
            listQualiAttributes = []
            for aAtt,aVal in self.entities[0].dictAttributes.items():  
                if type(aVal) in [int,float]:
                    listQuantiAttributes.append(aAtt)
                elif type(aVal) == str:
                    listQualiAttributes.append(aAtt) 
                # else:
                #     raise TypeError("Only int float and str are allowed")
            for aAtt in listQuantiAttributes:
                listOfValues = [aEnt.value(aAtt) for aEnt in self.entities]
                quantiAttributesStats[aAtt] = {
                    'sum': np.sum(listOfValues),
                    'mean': np.mean(listOfValues),
                    'min': np.min(listOfValues),
                    'max': np.max(listOfValues),
                    'stdev': np.std(listOfValues),
                    'histo':np.histogram(listOfValues, bins='auto')
                    }
            for aAtt in listQualiAttributes:
                listOfValues = [aEnt.value(aAtt) for aEnt in self.entities]
                qualiAttributesStats[aAtt]=Counter(listOfValues)
                type(dict(Counter(listOfValues)))

        aData = {
                'entityType': self.entityType(),
                'entityName': self.entityName,
                'round': currentRound,
                'phase': currentPhase,
                'population': len(self.entities),
                'entDefAttributes': dict(filter(lambda i: type(i[1]) in[int,float],self.dictAttributes.items())),
                'quantiAttributes': quantiAttributesStats,
                'qualiAttributes': qualiAttributesStats
                    }    
        self.listOfStepStats.append(aData)



# ********************************************************    

# to get the entity matching a Id or at a specified coordinates
    def getEntity(self, x, y=None):
        """
        Return an entity identified by its id or its coordinates on a grid
        arg:
            id (int): id of the entity
        Alternativly, can return an entity identified by its if or coordinates on a grid 
             x (int): column number
            y (int):  row number
        """
        if isinstance(y, int):
            if x < 0 or y < 0 : return None
            aId= self.grid.cellIdFromCoords(x,y)
        else:
            aId=x
        return next(filter(lambda ent: ent.id==aId, self.entities),None)

# to get all entities. a condition on the entity can be used to select only some entities
    def getEntities(self, condition=None):

        if condition is None: return self.entities[:]
        return [ent for ent in self.entities if condition(ent)]

# to get all entities with a certain value
    def getEntities_withValue(self, att, val):
        return list(filter(lambda ent: ent.value(att)==val, self.entities))

# to get all entities not having a certain value
    def getEntities_withValueNot(self, att, val):
        return list(filter(lambda ent: ent.value(att)!=val, self.entities))

  # Return a random entity
    def getRandomEntity(self, condition=None, listOfEntitiesToPickFrom=None):
        """
        Return a random entity.
        """
        if listOfEntitiesToPickFrom == None:
            listOfEntitiesToPickFrom = self.entities
        if condition == None:
            listOfEntities = listOfEntitiesToPickFrom
        else:
            listOfEntities = [ent for ent in listOfEntitiesToPickFrom if condition(ent)]
        
        return random.choice(listOfEntities) if len(listOfEntities) > 0 else False

   # Return a random entity with a certain value
    def getRandomEntity_withValue(self, att, val, condition=None):
        """
        Return a random entity.
        """
        return self.getRandomEntity(condition=condition, listOfEntitiesToPickFrom=self.getEntities_withValue(att, val))


  # Return a random entity not having a certain value
    def getRandomEntity_withValueNot(self, att, val, condition=None):
        """
        Return a random entity.
        """
        return self.getRandomEntity(condition=condition, listOfEntitiesToPickFrom=self.getEntities_withValueNot(att, val))

    def getRandomEntities(self, aNumber, condition=None, listOfEntitiesToPickFrom=None):
        """
        Return a specified number of random entities.
        args:
            aNumber (int): a number of entities to be randomly selected
        """
        if listOfEntitiesToPickFrom == None:
            listOfEntitiesToPickFrom = self.entities
        if condition == None:
            listOfEntities = listOfEntitiesToPickFrom
        else:
            listOfEntities = [ent for ent in listOfEntitiesToPickFrom if condition(ent)]
        
        return random.sample(listOfEntities, min(aNumber,len(listOfEntities))) if len(listOfEntities) > 0 else []

    # Return random Entities with a certain value
    def getRandomEntities_withValue(self, aNumber, att, val, condition=None):
        """
        Return a specified number of random Entities.
        args:
            aNumber (int): a number of entities to be randomly selected
        """
        return self.getRandomEntities(aNumber, condition=condition, listOfEntitiesToPickFrom=self.getEntities_withValue(att, val))

    # Return random Entities not having a certain value
    def getRandomEntities_withValueNot(self, aNumber, att, val, condition=None):
        """
        Return a specified number of random Entities.
        args:
            aNumber (int): a number of entities to be randomly selected
        """
        return self.getRandomEntities(aNumber, condition=condition, listOfEntitiesToPickFrom=self.getEntities_withValueNot(att, val))


# To handle POV and placing on entity

    # To define a value for all entities
    def setEntities(self, aAttribute, aValue, condition=None):
        """
        Set the value of attribut value of all entities

        Args:
            aAttribute (str): Name of the attribute to set
            aValue (str): Value to set the attribute to
            condition (lambda function): a condition on the entity can be used to select only some entities
        """
        for ent in self.getEntities(condition):
            ent.setValue(aAttribute, aValue)

    # set the value of attribut to all entities in a specified column
    def setEntities_withColumn(self, aAttribute, aValue, aColumnNumber):
        """
        Set the value of attribut to all entities in a specified column

        Args:
            aAttribute (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
            aColumnNumber (int): a column number

        """
        for ent in self.getEntities_withColumn(aColumnNumber):
            ent.setValue(aAttribute, aValue)

    # set the value of attribut to all entities in a specified row
    def setEntities_withRow(self, aAttribute, aValue, aRowNumber):
        """
        Set the value of attribut to all entities in a specified row

        Args:
            aAttribute (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
            aRowNumber (int): a row number

        """
        for ent in self.getEntities_withRow(aRowNumber):
            ent.setValue(aAttribute, aValue)

    # To apply a value to a random entity
    def setRandomEntity(self, aAttribute, aValue, condition=None):
        """
        Apply a value to a random entity

        Args:
            aAttribute (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
        """
        self.getRandomEntity(condition=condition).setValue(aAttribute, aValue)

    # To apply a value to a random entity with a certain value
    def setRandomEntity_withValue(self, aAttribut, aValue, conditionAtt, conditionVal, condition=None):
        """
        To apply a value to a random entity with a certain value

        Args:
            aAttribut (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
        """
        self.getRandomEntity_withValue(conditionAtt, conditionVal, condition).setValue(aAttribut, aValue)

   # To apply a value to a random entity not having a certain value
    def setRandomEntity_withValueNot(self, aAttribut, aValue, conditionAtt, conditionVal, condition=None):
        """
       To apply a value to a random entity not having a certain value

        Args:
            aAttribut (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
        """
        self.getRandomEntity_withValueNot(conditionAtt, conditionVal, condition).setValue(aAttribut, aValue)

    # To apply a value to some random entity
    def setRandomEntities(self, aAttribute, aValue, numberOfentities=1, condition=None):
        """
        Applies the same attribut value for a random number of entities

        Args:
            aAttribute (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
            numberOfentities (int): number of entities
        """
        aList = self.getRandomEntities(numberOfentities, condition)
        if aList == []:
            return False
        for ent in aList:
            ent.setValue(aAttribute, aValue)

    # To apply a value to some random entities with a certain value
    def setRandomEntities_withValue(self, aAttribut, aValue, numberOfentities, conditionAtt, conditionVal, condition=None):
        """
        To apply a value to some random entities with a certain value

        Args:
            aAttribut (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
            numberOfentities (int): number of entities
        """
        for ent in self.getRandomEntities_withValue(numberOfentities, conditionAtt, conditionVal, condition):
            ent.setValue(aAttribut, aValue)

   # To apply a value to some random entities noty having a certain value
    def setRandomEntities_withValueNot(self, aAttribut, aValue, numberOfentities, conditionAtt, conditionVal, condition=None):
        """
        To apply a value to some random entities noty having a certain value

        Args:
            aAttribut (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
            numberOfentities (int): number of entities
        """
        for ent in self.getRandomEntities_withValueNot(numberOfentities, conditionAtt, conditionVal, condition):
            ent.setValue(aAttribut, aValue)
   
    # To delete all entities of a species
    def deleteAllEntities(self):
        """
        Delete all entities of the species.
        """
        for ent in self.entities[:]:
            self.deleteEntity(ent)

    # Indicators
    # to get the nb of entities
    def nbOfEntities(self):
        return len(self.getEntities())

    # to get the nb of entities who respect certain value
    def nb_withValue(self, att, value):
        return len(self.getEntities_withValue(att, value))
    
    # To handle entDefAttributesAndValues
    # setter
    def setValue(self,aAttribut,aValue):
        """
        Sets the value of an attribut
        Args:
            aAttribut (str): Name of the attribute
            aValue (str): Value to be set
        """

        if aAttribut in self.dictAttributes and self.dictAttributes[aAttribut]==aValue: return False #The attribute has already this value
        #self.saveHistoryValue()
        #print("name self : ", self.entities)
        self.dictAttributes[aAttribut]=aValue
        self.updateWatchersOnAttribute(aAttribut) #This is for watchers on this specific entity
        return True

    # To handle the info to be displayed in a contextual menu on entitis
    def setAttributeValueToDisplayInContextualMenu(self,aAttribut,aLabel=None):
        aDict={}
        aDict['att']=aAttribut
        aDict['label']= (aLabel if aLabel is not None else aAttribut)
        self.attributesToDisplayInContextualMenu.append(aDict)
    
    # # To handle the attrobutes concerned by the contextual update menu
    # def setAttributesConcernedByUpdateMenu(self,aAttribut,aLabel=None):
    #     self.updateMenu=True
    #     aDict={}
    #     aDict['att']=aAttribut
    #     aDict['label']= (aLabel if aLabel is not None else aAttribut)
    #     self.attributesToDisplayInUpdateMenu.append(aDict)
    
# ********************************************************    

class SGAgentDef(SGEntityDef):
    def __init__(self, sgModel, entityName, shape, defaultsize, entDefAttributesAndValues, defaultColor=Qt.black, locationInEntity="random", defaultImage=None, popupImage=None):
        super().__init__(sgModel, entityName, shape, defaultsize, entDefAttributesAndValues, defaultColor)
        self.locationInEntity = locationInEntity
        self.defaultImage = defaultImage
        self.popupImage = popupImage

    def newAgentOnCell(self, aCell, attributesAndValues=None, image=None, popupImage=None):
        if image is None:
            image = self.defaultImage
        if popupImage is None:
            popupImage = self.popupImage
        aAgent = SGAgent(aCell, self.defaultsize, attributesAndValues, self.defaultShapeColor, classDef=self, defaultImage=image, popupImage=popupImage)
        self.entities.append(aAgent)
        self.updateWatchersOnPop()
        self.updateWatchersOnAllAttributes()
        aAgent.show()
        return aAgent


    def newAgentAtCoords(self, cellDef_or_grid, xCoord=None, yCoord=None, attributesAndValues=None,image=None,popupImage=None):
        """
        Create a new Agent in the associated species.

        Args:
            cellDef_or_grid (instance) : the cellDef or grid you want your agent in
            ValueX (int) : Column position in grid (Default=Random)
            ValueY (int) : Row position in grid (Default=Random)
        Return:
            a agent
        """
        aCellDef = self.model.getCellDef(cellDef_or_grid)
        aGrid = self.model.getGrid(cellDef_or_grid)
        if xCoord == None: xCoord = random.randint(1, aGrid.columns)
        if yCoord == None: yCoord = random.randint(1, aGrid.rows)
        locationCell = aCellDef.getCell(xCoord, yCoord)
        return self.newAgentOnCell(locationCell, attributesAndValues,image,popupImage)

    def newAgentAtRandom(self, cellDef_or_grid, attributesAndValues=None,condition=None):
        """
        Create a new Agent in the associated species a place it on a random cell.
        Args:
            cellDef_or_grid (instance) : the cellDef or grid you want your agent in
        Return:
            a agent
            """
        aCellDef = self.model.getCellDef(cellDef_or_grid)
        locationCell=aCellDef.getRandomEntity(condition=condition)
        return self.newAgentOnCell(locationCell, attributesAndValues)

    def newAgentsAtRandom(self, aNumber, cellDef_or_grid, attributesAndValues=None,condition=None):
        """
        Create a number of Agents in the associated species and place them on random cells.
        Args:
            aNumber(int) : number of agents to be created
            cellDef_or_grid (instance) : the cellDef or grid you want your agent in
        Return:
            a list of agents
            """
        aCellDef = self.model.getCellDef(cellDef_or_grid)
        locationCells=aCellDef.getRandomEntities(aNumber, condition=condition)
        alist =[]
        for aCell in locationCells:
            alist.append(self.newAgentOnCell(aCell, attributesAndValues))
        return alist
    
    def newAgentsOnCell(self, nbAgents, aCell, attributesAndValues=None):
        """
        Create a specific number of new Agents in the associated species.
        Args:
            nbAgents (int) : number of Agents 
            aCell : aCell located on a grid
            attributesAndValues : attributes and values of the new agent
        Return:
            agents
        """
        for n in range(nbAgents):
            self.newAgentOnCell(aCell,attributesAndValues)

    def newAgentsAtCoords(self, nbAgents, cellDef_or_grid, xCoord=None, yCoord=None, attributesAndValues=None):
        """
        Create a specific number of new Agents in the associated species.

        Args:
            nbAgents (int) : number of Agents 
            cellDef_or_grid (instance) : the cellDef or grid you want your agent in
            ValueX (int) : Column position in grid (Default=Random)
            ValueY (int) : Row position in grid (Default=Random)
        Return:
            agents
        """
        for n in range(nbAgents):
            self.newAgentAtCoords(cellDef_or_grid,xCoord,yCoord,attributesAndValues)


    # To randomly move all agents
    def moveRandomly(self, numberOfMovement=1):
        for aAgent in self.entities[:]: # Need to iterate on a copy of the entities list, because , due to the moveByRecreating, the entities list changes during the loop
            aAgent.moveAgent(numberOfMovement=numberOfMovement)


    def deleteEntity(self, aAgent):
        """
        Delete a given agent
        args:
            aAgent (instance): the agent to de deleted
        """
        aAgent.cell.updateDepartureAgent(aAgent)
        aAgent.deleteLater()
        self.entities.remove(aAgent)
        self.updateWatchersOnPop()
        self.updateWatchersOnAllAttributes()
        #aAgent.update()


# Définition de SGCellDef
class SGCellDef(SGEntityDef):
    def __init__(self, grid, shape, defaultsize, entDefAttributesAndValues, defaultColor=Qt.white, entityName='Cell', defaultCellImage=None):
        super().__init__(grid.model, entityName, shape, defaultsize, entDefAttributesAndValues, defaultColor)
        self.grid = grid
        self.deletedCells = []
        self.defaultImage = defaultCellImage

    def newCell(self, x, y):
        ent = SGCell(self, x, y, self.defaultImage)
        self.entities.append(ent)
        ent.show()

    def setCell(self, x, y, aAttribute, aValue):
        ent = self.getCell(x, y).setValue(aAttribute, aValue)
        return ent

    def getCell(self, x, y=None):
        if isinstance(y, int):
            if x < 0 or y < 0:
                return None
            aId = self.cellIdFromCoords(x, y)
        else:
            aId = x
        return next(filter(lambda ent: ent.id == aId, self.entities), None)

    def cellIdFromCoords(self, x, y):
        if x < 0 or y < 0:
            return None
        return x + (self.grid.columns * (y - 1))

    # Return the cell at specified coordinates
    def getEntity(self, x, y=None):
        return self.getCell(x, y)

    def getEntities_withRow(self, aRowNumber):
        return self.grid.getCells_withRow(aRowNumber)

    def getEntities_withColumn(self, aColumnNumber):
        return self.grid.getCells_withColumn(aColumnNumber)

    def cellIdFromCoords(self,x,y):
        if x < 0 or y < 0 : return None
        return x + (self.grid.columns * (y -1))

    def deleteEntity(self, aCell):
        """
        Delete a given cell
        args:
            aCell (instance): the cell to de deleted
        """
        if len(aCell.agents) !=0:
            aCell.deleteAllAgents()
        self.deletedCells.append(aCell)
        aCell.isDisplay = False
        self.entities.remove(aCell)
        self.updateWatchersOnPop()
        self.updateWatchersOnAllAttributes()
        aCell.update()

    def reviveThisCell(self, aCell):
        self.entities.append(aCell)
        aCell.isDisplay = True
        self.deletedCells.remove(aCell)
        self.updateWatchersOnPop()
        self.updateWatchersOnAllAttributes()
        aCell.update()
        
