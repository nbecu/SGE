from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction

#Class who manage the game mechanics of Update
class SGModify(SGAbstractAction):
    def __init__(self,entDef,dictNewValues,number,conditions=[],feedBack=[],conditionOfFeedBack=[],nameToDisplay=None,setControllerContextualMenu=False,setOnController=True):
        super().__init__(entDef,number,conditions,feedBack,conditionOfFeedBack,nameToDisplay,setControllerContextualMenu,setOnController)
        self.dictNewValues=dictNewValues
        self.entityDef=entDef
        self.att = list(self.dictNewValues.keys())[0]  #  Get dict key
        self.value = self.dictNewValues[self.att]  # Get associate value
        if nameToDisplay is None:
            # self.name="ModifyAction "+ self.att + " " + str(self.value)
            self.name=f"{self.att}->{self.value}"
        else:
            self.name=nameToDisplay 
        self.actionType="Modify"
        self.addCondition(lambda aTargetEntity: aTargetEntity.classDef == self.targetEntDef)
        self.addCondition(lambda aTargetEntity: not aTargetEntity.isDeleted())
        self.addCondition(lambda aTargetEntity: aTargetEntity.value(self.att) != self.value)
   

    def executeAction(self, aTargetEntity):
        aTargetEntity.setValue(self.att,self.value)
        return aTargetEntity

    def generateLegendItems(self,aControlPanel):
        if self.setControllerContextualMenu == False:
            aList = []
            for aAtt, aValue in self.dictNewValues.items():
                aColor = self.targetEntDef.getColorOrColorandWidthOfFirstOccurenceOfAttAndValue(aAtt,aValue)
                # If it's a border color, it returns a dict, not a color.
                if isinstance(aColor,dict):
                    borderColorAndWidth = aColor
                    aColor =  self.targetEntDef.defaultShapeColor
                    #todo Modifs pour MTZC pour que ce soit plus simple
                    aList.append(SGLegendItem(aControlPanel,'symbol',str(aValue),self.targetEntDef,aColor,aAtt,aValue,isBorderItem = True, borderColorAndWidth = borderColorAndWidth , gameAction=self))
                # If not, its a shape color
                else:
                    #todo Modifs pour MTZC pour que ce soit plus simple
                    aList.append(SGLegendItem(aControlPanel,'symbol',str(aValue),self.targetEntDef,aColor,aAtt,aValue,gameAction=self))

            return aList
