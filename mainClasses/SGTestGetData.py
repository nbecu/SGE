import sys
from pathlib import Path

from mainClasses.SGModel import*
from mainClasses.SGEntity import*
from mainClasses.SGEntityDef import*
from mainClasses.SGAgent import*
from mainClasses.SGCell import*
from mainClasses.SGModelAction import*
from mainClasses.SGPlayer import*
from mainClasses.SGSimulationVariable import*
from mainClasses.SGTimeManager import*



class SGTestGetData():
    def __init__(self, model):
        self.model = model

    def getAllDataSinceInitialization(self):
        dictOfData ={}
        for aEntity in self.model.getAllEntities():
            dictOfData[aEntity.getObjectIdentiferForJsonDumps] = aEntity.history["value"]
                    # ToDo: Here I fetch the raw format of the history["value"] of the entity, but perhaps it would need to be reformated
        print(dictOfData)
        return dictOfData
        # self.modelgetAllAgents
        # self.model.getAllCells  --> These two lines are equivalent to self.modelgetAllEntities

        # In addition to data carried by the entities, there are are also data carried by :
        #      - SGEntityDef, SimVariable and SGPlayer --> Those data are in the form of attribute and values
        #      - GameActions  --> Those data are the number of actions performed or left at each round