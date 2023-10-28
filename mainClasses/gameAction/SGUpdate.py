from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

#Class who manage the game mechanics of Update
class SGUpdate(SGAbstractAction):
    def __init__(self,anObject,number,dictNewValues,restrictions=[],feedBack=[],conditionOfFeedBack=[]):
        self.anObject=anObject
        self.number=number
        self.numberUsed=0
        self.dictNewValues=dictNewValues
        key = list(self.dictNewValues.keys())[0]  # Récupère la clé du dictionnaire
        value = self.dictNewValues[key]  # Récupère la valeur correspondante
        result = key + " " + str(value)
        self.name="UpdateAction "+result
        self.restrictions=restrictions
        self.feedback=feedBack
        self.conditionOfFeedBack=conditionOfFeedBack            
   