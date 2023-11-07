from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGEntity import SGEntity
from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell
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
        self.povShapeColor={}
        self.povBorderColor={}
        self.shapeColorClassif={} # Classif devra remplacer les Pov à terme
        self.borderColorClassif={}# Classif devra remplacer les Pov à terme
        self.watchers={}
        self.IDincr = 0
        self.entities=[]

    def nextId(self):
        self.IDincr =+1
        return self.IDincr
    

    #a mettre coté instance
        # isDisplay

    ###Definiton of the methods who the modeler will use
    def setDefaultValue(self, aAtt, aDefaultValue):
        self.attributesDefaultValues[aAtt] = aDefaultValue

    #To set up a POV
    def newPov(self,nameofPOV,concernedAtt,dictOfColor):
        """
        Declare a new Point of View for the Species.

        Args:
            self (Species object): aSpecies
            nameOfPov (str): name of POV, will appear in the interface
            concernedAtt (str): name of the attribut concerned by the declaration
            DictofColors (dict): a dictionary with all the attribut values, and for each one a Qt.Color (https://doc.qt.io/archives/3.3/qcolor.html)
            
        """
        self.povShapeColor[nameofPOV]={str(concernedAtt):dictOfColor}
        self.model.addPovinMenuBar(nameofPOV)
        # if self.model.agentSpecies[self.entityName]['me']=='collec':
        #     self.color[str(nameofPOV)]={str(concernedAtt):dictOfColor}
        #     self.model.addPovinMenuBar(nameofPOV)
        # else:
        #     print("Warning, a POV can be only define on a Species")

# ********************************************************    

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
            listOfEntities = [aEntity for ent in listOfEntitiesToPickFrom if condition(aEntity)]
        
        return random.sample(listOfEntities, aNumber) if len(listOfEntities) > 0 else False

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
        for ent in self.grid.getCells_withColumn(aColumnNumber):
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
        for ent in self.entities_withRow(aRowNumber):
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
    def setRandomEntities(self, aAttribute, aValue, numberOfentities, condition=None):
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

# ********************************************************    

class SGAgentDef(SGEntityDef):
    def __init__(self, sgModel, entityName,shape,defaultsize,attributesPossibleValues,defaultColor=Qt.black,locationInentity="random"):
        super().__init__(sgModel, entityName,shape,defaultsize,attributesPossibleValues,defaultColor)
        self.locationInentity=locationInentity

    def newAgentAtCoords(self, aGrid, xCoord=None, yCoord=None, attributesAndValues=None):
        """
        Create a new Agent in the associated species.

        Args:
            aGrid (instance) : the grid you want your agent in
            aAgentSpecies (instance) : the species of your agent
            ValueX (int) : Column position in grid (Default=Random)
            ValueY (int) : Row position in grid (Default=Random)

        Return:
            a new nest in the species dict for the agent
            a agent


        """
        # anAgentID = str(aAgentSpecies.memoryID)
        # self.updateIDmemory(aAgentSpecies)

        if xCoord == None: xCoord = random.randint(1, aGrid.columns)
        if yCoord == None: yCoord = random.randint(1, aGrid.rows)
        locationCell = self.model.getCellDef(aGrid).getCell(xCoord, yCoord)
        aAgent = SGAgent(aGrid,locationCell, self.defaultsize,attributesAndValues, self.defaultShapeColor,classDef=self)
        self.entities.append(aAgent)
        aAgent.show()
        return aAgent
    

class SGCellDef(SGEntityDef):
    def __init__(self,grid, shape,defaultsize,defaultColor=Qt.white,entityName='entity'):
        attributesPossibleValues=None
        super().__init__(grid.model, entityName,shape,defaultsize,attributesPossibleValues,defaultColor)
        self.grid= grid

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
    
    # Return the cell at specified coordinates
    def getCell(self, x, y):
        """
        Return a cell with column and row number.
        args:
            x (int): column number
            y (int): row number
        """
        aId= self.cellIdFromCoords(x,y)
        return list(filter(lambda ent: ent.id==aId, self.entities))[0]

    def cellIdFromCoords(self,x,y):
        return x+ (self .grid.columns * (y -1))



