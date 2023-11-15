from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

#Class who manage the game mechanics of Update
class SGUpdate(SGAbstractAction):
    def __init__(self,anObject,number,dictNewValues,conditions=[],feedBack=[],conditionOfFeedBack=[]):
        super().__init__(anObject,number,conditions,feedBack,conditionOfFeedBack)
        self.dictNewValues=dictNewValues
        self.att = list(self.dictNewValues.keys())[0]  # Récupère la clé du dictionnaire
        self.value = self.dictNewValues[self.att]  # Récupère la valeur correspondante
        result = self.att + " " + str(self.value)
        self.name="UpdateAction "+result   
   

    def executeAction(self, aTargetEntity):
        if aTargetEntity.isDeleted() : aTargetEntity.classDef.reviveThisCell(aTargetEntity) 
        aTargetEntity.setValue(self.att,self.value)
        return aTargetEntity

