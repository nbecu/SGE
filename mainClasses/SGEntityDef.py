from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGCell import SGCell
from mainClasses.SGGrid import SGGrid
from mainClasses.SGAgent import SGAgent
import random

# Class who is in charged of the definition of an entity type (like entities and agents)
# EntityDef has two subclasses entityDef and AgentDef which hold the definition parameters of the entities and agents 
# entityDef and AgentDef also hold the list of entities of the simulation 
class SGEntityDef():
    def __init__(self, sgModel, entityName,shape,defaultsize,attributesPossibleValues, defaultShapeColor):
        self.model= sgModel
        self.entityName=entityName
        self.attributesPossibleValues= attributesPossibleValues if attributesPossibleValues is not None else {}
        self.attributesDefaultValues={}
        self.shape=shape
        self.defaultsize=defaultsize
        self.defaultShapeColor=defaultShapeColor
        self.defaultBorderColor=Qt.black
        self.defaultBorderWidth=1
        self.povShapeColor={}
        self.povBorderColorAndWidth={}
        self.shapeColorClassif={} # Classif devra remplacer les Pov à terme
        self.borderColorClassif={}# Classif devra remplacer les Pov à terme
        self.watchers={}
        self.IDincr = 0
        self.entities=[]

    def nextId(self):
        self.IDincr +=1
        return self.IDincr
    
    def entityType(self):
        if isinstance(self,SGCellDef): return 'Cell'
        elif isinstance(self,SGAgentDef): return 'Agent'
        else: raise ValueError('Wrong or new entity type')

    #a mettre coté instance
        # isDisplay

    ###Definition of the developer methods
    def addWatcher(self,aIndicator):
        if aIndicator.attribut is None:
            aAtt = 'nb'
        else: aAtt = aIndicator.attribut
        if aAtt not in self.watchers.keys():
            self.watchers[aAtt]=[]
        self.watchers[aAtt].append(aIndicator)

        1
    # def setCellWatchers(self, attribut, indicator):
    #     grids = self.model.getGrids()
    #     for grid in grids:
    #         cellCollection = self.model.cellCollection[grid.id]
    #         if attribut not in cellCollection["watchers"].keys():
    #             cellCollection["watchers"][attribut] = []
    #         cellCollection["watchers"][attribut].append(indicator)
        
    # def setAgentWatchers(self,indicator):
    #     if indicator.attribut is None:
    #         aAtt = 'nb'
    #     else:
    #         aAtt = indicator.attribut
    #     if indicator.entity == 'agents':
    #         if 'agents' not in self.model.agentSpecies.keys():
    #             self.model.agentSpecies['agents']={'watchers':{}}
    #         watchersDict=self.model.agentSpecies['agents']['watchers']
    #     else:
    #          watchersDict=self.model.agentSpecies[indicator.entity]['watchers']

    #     if aAtt not in watchersDict.keys():
    #         watchersDict[aAtt]=[]
    #     watchersDict[aAtt].append(indicator)

    
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
        # self.model.addPovinMenuBar(nameofPOV)
        self.model.addClassDefSymbologyinMenuBar(self,nameOfPov)
        if len(self.povShapeColor)==1:
            self.setInitialPov(nameOfPov)

    def setInitialPov(self,nameOfPov):
        self.model.checkSymbologyinMenuBar(self,nameOfPov)

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


# to get all entities with a certain value
    def getEntities_withValue(self, att, val):
        return list(filter(lambda ent: ent.value(att)==val, self.entities))

# to get all entities not having a certain value
    def getEntities_withValueNot(self, att, val):
        return list(filter(lambda ent: ent.value(att)!=val, self.entities))

  # Return a random entity
    def getRandom(self, condition=None, listOfEntitiesToPickFrom=None):
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
    def getRandom_withValue(self, att, val, condition=None):
        """
        Return a random entity.
        """
        return self.getRandom(condition=condition, listOfEntitiesToPickFrom=self.getEntities_withValue(att, val))


  # Return a random entity not having a certain value
    def getRandom_withValueNot(self, att, val, condition=None):
        """
        Return a random entity.
        """
        return self.getRandom(condition=condition, listOfEntitiesToPickFrom=self.getEntities_withValueNot(att, val))

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
    def setEntities(self, aAttribute, aValue):
        """
        Set the value of attribut value of all entities

        Args:
            aAttribute (str): Name of the attribute to set
            aValue (str): Value to set the attribute to
        """
        for ent in self.entities:
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
        self.getRandomEntity_withValue(
            conditionAtt, conditionVal, condition).setValue(aAttribut, aValue)

   # To apply a value to a random entity not having a certain value
    def setRandomEntity_withValueNot(self, aAttribut, aValue, conditionAtt, conditionVal, condition=None):
        """
       To apply a value to a random entity not having a certain value

        Args:
            aAttribut (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
        """
        self.getRandomEntity_withValueNot(
            conditionAtt, conditionVal, condition).setValue(aAttribut, aValue)

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
    # to get all entities who respect certain value
    def nb_withValue(self, att, value):
        return len(self.getEntities_withValue(att, value))
    
# ********************************************************    

class SGAgentDef(SGEntityDef):
    def __init__(self, sgModel, entityName,shape,defaultsize,attributesPossibleValues,defaultColor=Qt.black,locationInentity="random"):
        super().__init__(sgModel, entityName,shape,defaultsize,attributesPossibleValues,defaultColor)
        self.locationInentity=locationInentity

    def newAgentOnCell(self, aCell, attributesAndValues=None):
        """
        Create a new Agent in the associated species.
        Args:
            aCell : aCell located on a grid
            attributesAndValues : attributes and values of the new agent
        Return:
            a agent
        """
        # anAgentID = str(aAgentSpecies.memoryID)
        # self.updateIDmemory(aAgentSpecies)
        aAgent = SGAgent(aCell, self.defaultsize,attributesAndValues, self.defaultShapeColor,classDef=self)
        self.entities.append(aAgent)
        self.updateWatchersOnPop()
        self.updateWatchersOnAllAttributes()
        aAgent.updateMqtt()
        aAgent.show()
        return aAgent


    def newAgentAtCoords(self, cellDef_or_grid, xCoord=None, yCoord=None, attributesAndValues=None):
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
        return self.newAgentOnCell(locationCell, attributesAndValues)

    


    def newAgentAtRandom(self, cellDef_or_grid, attributesAndValues=None):
        """
        Create a new Agent in the associated species a place it on a random cell.
        Args:
            cellDef_or_grid (instance) : the cellDef or grid you want your agent in
        Return:
            a agent
            """
        return self.newAgentAtCoords(cellDef_or_grid, None, None, attributesAndValues)


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
        aAgent.updateMqtt()
        # aAgent.update()


class SGCellDef(SGEntityDef):
    def __init__(self,grid, shape,defaultsize,defaultColor=Qt.white,entityName='Cell'):
        attributesPossibleValues=None
        super().__init__(grid.model, entityName,shape,defaultsize,attributesPossibleValues,defaultColor)
        self.grid= grid
        self.deletedCells=[]

    def newCell (self, x, y):
        ent = SGCell(self, x, y)
        self.entities.append(ent)
        ent.show()

    def setCell(self, x, y, aAttribute, aValue):
        """
        set the value of attribute value for a specific cell
        Args:
            x (int): a column number
            y (int): a row number
            aAttribute (str): Name of the attribute to set.
            aValue (str): Value to set the attribute to
        """
        ent = self.getCell(x, y).setValue(aAttribute, aValue)
        return ent
    
    # Return the cell matching a Id or at specified coordinates
    def getCell(self, x, y=None):
        """
        Return a cell identified by its column number and row number.
        args:
            x (int): column number
            y (int): row number
        Alternativly can also return a cell identified by its id
        arg:
            id (int): id of the cell
        """
        if isinstance(y, int):
            if x < 0 or y < 0 : return None
            aId= self.cellIdFromCoords(x,y)
        else:
            aId=x
        return next(filter(lambda ent: ent.id==aId, self.entities),None)

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
        aCell.updateMqtt()
        aCell.update()

    def reviveThisCell(self, aCell):
        self.entities.append(aCell)
        aCell.isDisplay = True
        self.deletedCells.remove(aCell)
        self.updateWatchersOnPop()
        self.updateWatchersOnAllAttributes()
        aCell.updateMqtt()
        aCell.update()
        
