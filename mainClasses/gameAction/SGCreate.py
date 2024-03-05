from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction


#Class who manage the game mechanics of creation
class SGCreate(SGAbstractAction):
    def __init__(self,entDef,dictAttributs,number,conditions=[],feedBack=[],conditionOfFeedBack=[]):
        super().__init__(entDef,number,conditions,feedBack,conditionOfFeedBack)
        self.dictAttributs=dictAttributs
        self.name="Create "+str(self.targetEntDef.entityName)
        self.addCondition(lambda aTargetEntity: aTargetEntity.classDef.entityType() == 'Cell')


    def executeAction(self, aTargetEntity):
        return self.targetEntDef.newAgentOnCell(aTargetEntity,self.dictAttributs)


    def generateLegendItems(self,aControlPanel):
        if self.dictAttributs is None:
            aColor = self.targetEntDef.defaultShapeColor
            return [SGLegendItem(aControlPanel,'symbol','create',self.targetEntDef,aColor,gameAction=self)]
        else:
            aList = []
            for aAtt, aValue in self.dictAttributs.items():
                aColor = self.targetEntDef.getColorOrColorandWidthOfFirstOccurenceOfAttAndValue(aAtt,aValue)
                aList.append(SGLegendItem(aControlPanel,'symbol','create('+aAtt+'='+str(aValue)+')',self.targetEntDef,aColor,aAtt,aValue,gameAction=self))
            return aList


    

