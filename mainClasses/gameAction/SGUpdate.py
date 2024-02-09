from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell
from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

#Class who manage the game mechanics of Update
class SGUpdate(SGAbstractAction):
    def __init__(self,entDef,number,dictNewValues,conditions=[],feedBack=[],conditionOfFeedBack=[]):
        super().__init__(entDef,number,conditions,feedBack,conditionOfFeedBack)
        self.dictNewValues=dictNewValues
        self.att = list(self.dictNewValues.keys())[0]  # Récupère la clé du dictionnaire
        self.value = self.dictNewValues[self.att]  # Récupère la valeur correspondante
        result = self.att + " " + str(self.value)
        self.name="UpdateAction "+result   
        self.addCondition(lambda aTargetEntity: aTargetEntity.classDef == self.targetEntDef)
        self.addCondition(lambda aTargetEntity: not aTargetEntity.isDeleted())
   

    def executeAction(self, aTargetEntity):
        # This should not be allowed. A condition has been added at the initilization of the UpdateAction to prevent this
        # if aTargetEntity.isDeleted(): aTargetEntity.classDef.reviveThisCell(aTargetEntity) 
        aTargetEntity.setValue(self.att,self.value)
        return aTargetEntity

    def generateLegendItems(self,aControlPanel):
        aList = []
        for aAtt, aValue in self.dictNewValues.items():
            aColor = self.targetEntDef.getColorOrColorandWidthOfFirstOccurenceOfAttAndValue(aAtt,aValue)
            # If it's a border color, it returns a dict, not a color.
            if isinstance(aColor,dict):
                borderColorAndWidth = aColor
                aColor =  self.targetEntDef.defaultShapeColor
                aList.append(SGLegendItem(aControlPanel,'symbol',aAtt+'='+str(aValue),self.targetEntDef,aColor,aAtt,aValue,isBorderItem = True, borderColorAndWidth = borderColorAndWidth , gameAction=self))
            # If not, its a shape color
            else:
                aList.append(SGLegendItem(aControlPanel,'symbol',aAtt+'='+str(aValue),self.targetEntDef,aColor,aAtt,aValue,gameAction=self))

        return aList
