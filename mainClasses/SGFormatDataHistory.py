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



class SGFormatDataHistory():
    def __init__(self, model):
        self.model = model
        self.dictOfData = {}


    def collectLastStepData(self):
        currentRound =self.model.timeManager.currentRound
        currentPhase = self.model.timeManager.currentPhase 
        for aEntity in self.model.getAllEntities():
            entName = aEntity.classDef.entityName
            entId = aEntity.id
            self.dictOfData.setdefault(entName,{})
            self.dictOfData[entName].setdefault(entId,{})
            for aAttribute, historyList in aEntity.history["value"].items():
                self.dictOfData[entName][entId].setdefault(aAttribute,[])
                h = historyList[-1] #  format (h['round'], h['phase'], h['value']))
                if (h[0] !=  currentRound) or ((h[0] ==  currentRound) and (h[1] !=  currentPhase)):
                    valueToRecordAtThisStep = self.dictOfData[entName][entId][aAttribute][-1]
                else:
                    valueToRecordAtThisStep = h[2]
                self.dictOfData[entName][entId][aAttribute].append(valueToRecordAtThisStep)

        print(self.dictOfData)
