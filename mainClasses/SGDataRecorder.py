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
from collections import defaultdict


class SGDataRecorder():
    def __init__(self, model):
        self.model = model
        # self.dictOfData = {}
        # self.dictOfData = defaultdict(defaultdict(defaultdict(list)))
        self.dictOfData = defaultdict(lambda: defaultdict((lambda: defaultdict(list))))
                                 # entName, entId , aAttribute, list of value at each step
        self.listOfData_ofEntities = []



    def collectStepData(self):
        currentRound =self.model.timeManager.currentRound
        currentPhase = self.model.timeManager.currentPhase
        for aEntity in self.model.getAllEntities():
            aData = {
                'entityType': aEntity.classDef.entityType(),
                'entityName': aEntity.classDef.entityName,
                'id': aEntity.id,
                'round': currentRound,
                'phase': currentPhase,
                'attribut': aEntity.dictAttributes
                    }    
            self.listOfData_ofEntities.append(aData)


    def convertStep_inRoundAndPhase(self,aStep):
        nbPhases = len(self.model.timeManager.phases) -1 #ToDo : le +1  devra etre enlevé lorsqu'on fera le merge avec la branche "version 5""
        if aStep == 0: aPhase=0
        else:
            aPhase = (aStep % nbPhases)
            if aPhase == 0 : aPhase = nbPhases
        aRound = ((aStep-1) // nbPhases) +1
        return {'round':aRound , 'phase':aPhase}
    
    def convertRoundAndPhase_inStep(self,aRound, aPhase):
        nbPhases = len(self.model.timeManager.phases) -1 #ToDo : le +1  devra etre enlevé lorsqu'on fera le merge avec la branche "version 5""
        return aPhase+((aRound -1)*nbPhases)+1

    def getAttributeValueOfAEntityAtSpecifiedRoundAndPhase(self,entityName,entityId,aAttribute,aRound,aPhase):
        aList = self.dictOfData[entityName][entityId][aAttribute]
        res = next((ele for ele in aList  if (ele[0] == aRound and ele[1] == aPhase)), False)
        return res[2]

    def getAttributeValueOfAEntityAtSpecifiedStep(self,entityName,entityId,aAttribute,aStep):
        aTime = self.convertStep_inRoundAndPhase(aStep)
        return self.getValueOfAEntityAndAttributeAtSpecifiedRoundAndPhase(entityName,entityId,aAttribute,aTime['round'],aTime['phase'])


    def getDictAttributesOfAEntityAtSpecifiedRoundAndPhase(self,entityName,entityId,aRound,aPhase):
        nbPhases = len(self.model.timeManager.phases) -1 #ToDo : le +1  devra etre enlevé lorsqu'aon fera le merge avec la branche "version 5""
        aStep = aPhase+((aRound -1)*nbPhases)+1
        return self.getDictAttributesOfAEntityAtSpecifiedStep(self,entityName,entityId,aStep)
    

    def getNumberOfStepsRecorded(self):
        self.dictOfData.values()
        return len(list(list(list(self.dictOfData.values())[0].values())[0].values())[0])
        
