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


class SGDataRecorder():
    def __init__(self, model):
        self.model = model
        self.stepsData_ofEntities = []
        self.stepsData_ofSimVariables = []
        self.stepsData_ofPlayers = []
        self.nbPhases = len(self.model.timeManager.phases) -1 #ToDo : le +1  devra etre enlevé lorsqu'on fera le merge avec la branche "version 5""
        

    def calculateStepStats(self):
        for aEntDef in self.model.getEntitiesDef():  
              aEntDef.calculateAndRecordCurrentStepStats()
    
    def getStats_ofEntities(self):
        aList=[]
        for aEntDef in self.model.getEntitiesDef():  
              aList.extend(aEntDef.listOfStepStats)
        return aList

    def getStepsData_ofEntities(self):
        if not [e for e in self.model.getAllEntities.values() if e.dictAttributes ] : return []
        if not self.stepsData_ofEntities:
            #in case the records are empty, than the getListOfStepsData() should start from the initial date which is [0,0]
            lastRecordedDate=[0,0] 
        else:
            lastRecordedDate = [self.stepsData_ofEntities[-1]['round'], self.stepsData_ofEntities[-1]['phase']]
            # remove the last recorded date from the records (because the values may have been changed during the concerned step )
            self.stepsData_ofEntities = [aStepData  for aStepData in self.stepsData_ofEntities if [aStepData['round'],aStepData['phase']]==lastRecordedDate]
        for aEntity in self.model.getAllEntities():
            stepsData = aEntity.getListOfStepsData(lastRecordedDate)
            self.stepsData_ofEntities.extend(stepsData)
        return self.stepsData_ofEntities

    def getStepsData_ofSimVariables(self):
        aList=[]
        for aSimVar in self.model.simulationVariables:
            aList.extend(aSimVar.getListOfStepsData())
        return aList
    
    def getStepsData_ofPlayers(self):
        if not [p for p in self.model.players.values() if p.dictAttributes ] : return []
        if not self.stepsData_ofPlayers:
            #in case the records are empty, than the getListOfStepsData() should start from the initial date which is [0,0]
             lastRecordedDate=[0,0] 
        else:
            lastRecordedDate = [self.stepsData_ofPlayers[-1]['round'], self.stepsData_ofPlayers[-1]['phase']]
            # remove the last recorded date from the records (because the values may have been changed during the concerned step )
            self.stepsData_ofPlayers = [aStepData  for aStepData in self.stepsData_ofPlayers if [aStepData['round'],aStepData['phase']]==lastRecordedDate]
        
        for aPlayer in self.model.players.values():  
              self.stepsData_ofPlayers.extend(aPlayer.getListOfStepsData(lastRecordedDate))
        return self.stepsData_ofPlayers
    


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

    def getDictAttributesOfAEntityAtSpecifiedRoundAndPhase(self,entityName,entityId,aRound,aPhase):
        #keys of a stepData are -> 'entityType','entityName','id','round','phase','dictAttributes'
        res=  next((aStepData for aStepData in self.stepsData_ofEntities if entityName==aStepData['entityName'] and entityId==aStepData['id'] and aRound==aStepData['round'] and aPhase==aStepData['phase']), None) 
        return res if None else res['dictAttributes']

    def getAttributeValueOfAEntityAtRoundAndPhase(self,entityName,entityId,aRound,aPhase,aAttribute):
        res=  self.getDictAttributesOfAEntityAtSpecifiedRoundAndPhase(entityName,entityId,aRound,aPhase)
        return res if None else res[aAttribute]
    
    def getAttributeValueOfAEntityAtSpecifiedStep(self,entityName,entityId,aStep,aAttribute):
        aDate = self.convertStep_inRoundAndPhase(aStep)
        return self.getValueOfAEntityAndAttributeAtSpecifiedRoundAndPhase(entityName,entityId,aDate['round'],aDate['phase'],aAttribute)

    
        
