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

    # def collectStepData(self):
    # ########    Ancienne méthode lorsque la sauvegarde se faisait  sous forme d'un dict d'attributs dans lequel on sauvegarde une liste des valeurs des steps, à chaque attribut
    #     currentRound =self.model.timeManager.currentRound
    #     currentPhase = self.model.timeManager.currentPhase
    #     for aEntity in self.model.getAllEntities():
    #         entName = aEntity.classDef.entityName
    #         entId = aEntity.id
    #         # self.dictOfData.setdefault(entName,{})
    #         # self.dictOfData[entName].setdefault(entId,{})
    #         #print("ent : ", aEntity.history["value"])
    #         for aAttribute, historyList in aEntity.history["value"].items():
    #             # self.dictOfData[entName][entId].setdefault(aAttribute,[])
    #             h = historyList[-1]      #format (h['round'], h['phase'], h['value']))
    #             if (h[0] !=  currentRound) or ((h[0] ==  currentRound) and (h[1] !=  currentPhase)):
    #                 stepDataOfAttribute = [currentRound,currentPhase,self.dictOfData[entName][entId][aAttribute][-1][2]]
    #             else:
    #                 stepDataOfAttribute = h
    #             print("stepDataOfAttribute :", stepDataOfAttribute) 
    #             self.dictOfData[entName][entId][aAttribute].append(stepDataOfAttribute)


    def collectStepData(self):
        ########   Nouvelle méthode avec une sauvegarde sous forme d'une liste de data qui contient les specifications de la donnée ('entityDef', 'entityName','id','round','phase') et la donnée (les valeurs) sous la forme d'un  dictOfAttributes
        # format d'une donné souvegardé dans la liste
            # aData = {
            #             'entityDef': 'Cell' if entityName == 'Cell' else 'Agent',
            #             'entityName': entityName,
            #             'id': entId,
            #             'round': iRound,
            #             'phase': iPhase,
            #             'attribut': dictAtt
            #          }         
        currentRound =self.model.timeManager.currentRound
        currentPhase = self.model.timeManager.currentPhase
        for aEntity in self.model.getAllEntities():
            aData = {
                'entityType': aEntity.classDef.entityType,
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
    
    def getDictAttributesOfAEntityAtSpecifiedStep(self,entityName,entityId,aStep):
        aData = self.dictOfData[entityName][entityId]
        atts  = list(aData.keys())
        dict ={}
        ########    ERREUR ICI CAR certaines entites peuvent avoir moins de valeurs que de nbb de steps car elles ont été créé p pendant lla simu ou ont et Del avant la fin de la simu
        # du coup au niveau du data recorced il faut sauver le round et la phase
        #  du coup c'est peut plus simple dans dataREcorder de faire une sauvegarde sous forme d'une liste des steps pour lesquels on sauvegarde un  dictOfAttributes à chaque step (plutôt d'un dict d'attributs dans lequel on sauvegarde une liste des valeurs des stapes, à chaque attribut)
        for aAtt in atts:
            dict[aAtt]= aData[aAtt][aStep]
        return dict

    def getNumberOfStepsRecorded(self):
        self.dictOfData.values()
        return len(list(list(list(self.dictOfData.values())[0].values())[0].values())[0])
        

    def getDataForDiagramInterface(self):
        #this method reformats self.dictOfData to the format that is used by the DiagramInterface
        nbPhases = len(self.model.timeManager.phases) -1 #ToDo : le +1  devra etre enlevé lorsqu'aon fera le merge avec la branche "version 5""
        nbRounds = self.model.round()
        nbSteps = self.getNumberOfStepsRecorded()
        #DiagramInterface need a list of the 'history' of all entities
        historyData = []
        for entityName,dictOfEntities in self.dictOfData.items():
            for entId in dictOfEntities.keys():
                for i in range(nbSteps-1):
                    if i == 0: iPhase=0
                    else:
                        iPhase = (i % nbPhases)
                        if iPhase == 0 : iPhase = nbPhases
                    iRound = ((i-1) // nbPhases) +1
                    dictAtt = self.getDictAttributesOfAEntityAtSpecifiedStep(entityName,entId,i)
                    h = {
                        'id': entId,
                        'currentPlayer': 'None',
                        'entityDef': 'Cell' if entityName == 'Cell' else 'Agent',
                        'entityName': entityName,
                        'simVariable': {},
                        'round': iRound,
                        'phase': iPhase,
                        'attribut': dictAtt
                        }
                    historyData.append(h)  
                
                # aDictAttributes = {}
                # for aAttribute,listOfValues in self.dictOfAttributes.items:
                #     aDictAttributes
                #     for i, aValue in enumerate(listOfValues):
                #         iPhase = i
                #         iRound = i
                #         historyData[-1]['id'] == entId
                #         h = {
                #             'id': entId,
                #             'currentPlayer': 'None',
                #             'entityDef': 'Cell' if entityName == 'Cell' else 'Agent',
                #             'entityName': entityName,
                #             'simVariable': {},
                #             'round': iRound,
                #             'phase': iPhase,
                #             'attribut' :{}
                #             }
                #         h['attribut'][aAttribute]=aValue
                #     historyData.append(h)  
                        
            #  format de entity.getHistoryDataJSON()) de entity 
    #  {
    #         'id': self.id,
    #         'currentPlayer': self.model.currentPlayer,
    #         'entityDef': self.classDef.entityName if self.classDef.entityName == 'Cell' else 'Agent',
    #         'entityName': self.classDef.entityName,
    #         'simVariable': simvariable_dict,
    #         'round': self.model.timeManager.currentRound,
    #         'phase': self.model.timeManager.currentPhase,
    #         'attribut': self.dictAttributes
    #     }
             
        return historyData

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


    # def getAllDataSinceInitialization(self):
    #     dictOfData ={}
    #     historyData = []
    #     for aEntity in self.model.getAllEntities():
    #         h = aEntity.getHistoryDataJSON()
    #         historyData.append(h)
    #         #dictOfData[aEntity.getObjectIdentiferForJsonDumps] = aEntity.history["value"]
    #         """print("id: {}, entityName: {}, entityDef: {}, value: {}".
    #               format(h['id'], h['entityName'], h['entityDef'], h['value']))"""
    #         # ToDo: Here I fetch the raw format of the history["value"] of the entity, but perhaps it would need to be reformated
    #     #print("historyData : ", len(historyData))
    #     return historyData

    # def collectCurrentStepData(self):
    #     #self.getAllDataSinceInitialization()
    #     """
    #     Collect data from the current step, just before the simulation moves on to the next step
    #     'Moving to the next step' means either 'Moving to the next phase of the round', or (if its the last phase of the round), 'Moving to the next round'
    #     """
    #     currentRound =self.model.timeManager.currentRound
    #     currentPhase = self.model.timeManager.currentPhase
    #     for aEntity in self.model.getAllEntities():
    #         entName = aEntity.classDef.entityName
    #         entId = aEntity.id
    #         self.dictOfData.setdefault(entName,{})
    #         self.dictOfData[entName].setdefault(entId,{})
    #     #     history = aEntity.getHistoryDataJSON()
    #     #     #print("len list_history : ", len(aEntity.list_history))


    #         """
    #         aEntity.history["value"] contains a list of the history of attribute value updates.
    #         Depending on the progress of the simulation, the last update of an attribute may have been made during the current step, or at a previous step in time.
    #         The instructions below check when the last update was made, in order to either collect the data from aEntity.history["value"], or to use the last data saved in self.dictOfData.
    #         """
    #         for aAttribute, historyList in aEntity.history["value"].items():
    #             self.dictOfData[entName][entId].setdefault(aAttribute,[])
    #             h = historyList[-1] #  format (h['round'], h['phase'], h['value']))
    #             # h = historyList
    #             #print("h : ", historyList)
    #             if (h[0] !=  currentRound) or ((h[0] ==  currentRound) and (h[1] !=  currentPhase)):
    #                 valueToRecordAtThisStep = self.dictOfData[entName][entId][aAttribute][-1]
    #                 #print("self.dictOfData[entName][entId][aAttribute][-1] : ", self.dictOfData[entName][entId][aAttribute][-1])
    #             else:
    #                 valueToRecordAtThisStep = h[2]
    #                 #print("h 2 : ", h[2])
    #             self.dictOfData[entName][entId][aAttribute].append(valueToRecordAtThisStep)
    #     #print(self.dictOfData)

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