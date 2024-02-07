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


    def getAllDataSinceInitialization(self):
        dictOfData ={}
        historyData = []
        for aEntity in self.model.getAllEntities():
            h = aEntity.getHistoryDataJSON()
            historyData.append(h)
            dictOfData[aEntity.getObjectIdentiferForJsonDumps] = aEntity.history["value"]
            """print("id: {}, entityName: {}, entityDef: {}, value: {}".
                  format(h['id'], h['entityName'], h['entityDef'], h['value']))"""
            # ToDo: Here I fetch the raw format of the history["value"] of the entity, but perhaps it would need to be reformated
        #print(historyData)
        return historyData

    def collectCurrentStepData(self):
        """
        Collect data from the current step, just before the simulation moves on to the next step
        'Moving to the next step' means either 'Moving to the next phase of the round', or (if its the last phase of the round), 'Moving to the next round'
        """
        currentRound =self.model.timeManager.currentRound
        currentPhase = self.model.timeManager.currentPhase
        for aEntity in self.model.getAllEntities():
            entName = aEntity.classDef.entityName
            entId = aEntity.id
            self.dictOfData.setdefault(entName,{})
            self.dictOfData[entName].setdefault(entId,{})

            """
            aEntity.history["value"] contains a list of the history of attribute value updates.
            Depending on the progress of the simulation, the last update of an attribute may have been made during the current step, or at a previous step in time.
            The instructions below check when the last update was made, in order to either collect the data from aEntity.history["value"], or to use the last data saved in self.dictOfData.
            """
            for aAttribute, historyList in aEntity.history["value"].items():
                self.dictOfData[entName][entId].setdefault(aAttribute,[])
                #h = historyList[-1] #  format (h['round'], h['phase'], h['value']))
                h = historyList
                #print("h : ", historyList)
                if (h[0] !=  currentRound) or ((h[0] ==  currentRound) and (h[1] !=  currentPhase)):
                    valueToRecordAtThisStep = self.dictOfData[entName][entId][aAttribute][-1]
                    #print("self.dictOfData[entName][entId][aAttribute][-1] : ", self.dictOfData[entName][entId][aAttribute][-1])
                else:
                    valueToRecordAtThisStep = h[2]
                    #print("h 2 : ", h[2])


                self.dictOfData[entName][entId][aAttribute].append(valueToRecordAtThisStep)
        #print(self.dictOfData)

    """
    def collectLastStepData(self):
    currentRound, currentPhase = self.model.timeManager.currentRound, self.model.timeManager.currentPhase
    self.dictOfData.update({entName: {entId: {aAttribute: [self.dictOfData[entName][entId][aAttribute][-1] if (h := historyList[-1])[0] == currentRound and h[1] == currentPhase else h[2] for aAttribute, historyList in aEntity.history["value"].items()] for entId in [aEntity.id]} for entName, aEntity in ((aEntity.classDef.entityName, aEntity) for aEntity in self.model.getAllEntities())})
    print(self.dictOfData)


    def collectLastStepData(self):
        currentRound, currentPhase = self.model.timeManager.currentRound, self.model.timeManager.currentPhase
    
        for entity in self.model.getAllEntities():
            ent_name, ent_id = entity.classDef.entityName, entity.id
            data = self.dictOfData.setdefault(ent_name, {}).setdefault(ent_id, {})
    
            for attribute, history_list in entity.history["value"].items():
                data.setdefault(attribute, []).append(
                    data[attribute][-1] if history_list[-1][0] != currentRound or (history_list[-1][0] == currentRound and history_list[-1][1] != currentPhase)
                    else history_list[-1][2]
                )
    
        print(self.dictOfData)
    """