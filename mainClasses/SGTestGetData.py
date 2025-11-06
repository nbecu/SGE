import sys
from pathlib import Path

from mainClasses.SGModel import*
from mainClasses.SGEntity import *
from mainClasses.SGEntityType import*
from mainClasses.SGAgent import*
from mainClasses.SGCell import*
from mainClasses.SGModelAction import*
from mainClasses.SGPlayer import*
from mainClasses.SGSimulationVariable import*
from mainClasses.SGTimeManager import*


""" ---------------------------------------------------------------------------
This class is currently under construction.
Do not rely on its current implementation.
"""
class SGTestGetData():
    def __init__(self, model):
        self.model = model


    def getAllDataSinceInitialization(self):
        dictOfData ={}
        historyData = []
        for aEntity in self.model.getAllEntities():
            h = aEntity.getHistoryDataJSON()
            historyData.append(h)
            dictOfData[aEntity.getObjectIdentiferForJsonDumps] = aEntity.history["value"]
            """print("id: {}, name: {}, entityDef: {}, value: {}".
                  format(h['id'], h['name'], h['entityDef'], h['value']))"""

            # ToDo: Here I fetch the raw format of the history["value"] of the entity, but perhaps it would need to be reformated
        print(historyData)


        return historyData
        # self.modelgetAllAgents
        # self.model.getAllCells  --> These two lines are equivalent to self.modelgetAllEntities

        # In addition to data carried by the entities, there are are also data carried by :
        #      - SGEntityType, SimVariable and SGPlayer --> Those data are in the form of attribute and values
        #      - GameActions  --> Those data are the number of actions performed or left at each round