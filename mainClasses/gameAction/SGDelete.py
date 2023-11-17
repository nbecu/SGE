from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell
from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

import copy

#Class who manage the game mechanics of delete
class SGDelete(SGAbstractAction):
    def __init__(self,anObject,number,dictAttValue,aListOfrestrictions=[],feedBack=[],conditionOfFeedBack=[]):
        self.anObject=anObject
        self.number=number
        self.numberUsed=0
        self.dictAttValue=dictAttValue
        if anObject == SGCell:
            entName="Cell"
        else:
            entName=anObject.species
        self.name="Delete "+entName
        self.restrictions=copy.deepcopy(aListOfrestrictions)
        self.feedback=feedBack
        self.conditionOfFeedBack=conditionOfFeedBack
        self.addRestrictions(lambda selectedEntity: selectedEntity.species == entName)

    def executeAction(self, aTargetEntity):
                    self.classDef.deleteEntity(self)


    def generateLegendItems(self,aControlPanel):
        entDef = self.anObject
        aColor = entDef.defaultShapeColor
        return [SGLegendItem(aControlPanel,'symbol','delete',entDef,aColor,gameAction=self)]
