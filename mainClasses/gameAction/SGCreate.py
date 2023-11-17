from email import feedparser
from mainClasses.SGAgent import SGAgent
from mainClasses.SGCell import SGCell
from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction


#Class who manage the game mechanics of creation
class SGCreate(SGAbstractAction):
    def __init__(self,anObject,number,dictAttributs,conditions=[],feedBack=[],conditionOfFeedBack=[]):
        super().__init__(anObject,number,conditions,feedBack,conditionOfFeedBack)

        self.dictAttributs=dictAttributs
        self.name="CreateAction "+str(anObject.entityName)

    def executeAction(self, aTargetEntity):
        entDef = self.anObject
        return entDef.newAgentOnCell(aTargetEntity,self.dictAttributs)


    def generateLegendItems(self,aControlPanel):
        entDef = self.anObject
        if self.dictAttributs is None:
            aColor = entDef.defaultShapeColor
            return [SGLegendItem(aControlPanel,'symbol','create',entDef,aColor,gameAction=self)]
        else:
            aList = []
            for aAtt, aValue in self.dictAttributs.items():
                aColor = entDef.getColorOfFirstOccurenceOfAttAndValue(aAtt,aValue)
                aList.append(SGLegendItem(aControlPanel,'symbol','create',entDef,aColor,aAtt,aValue,gameAction=self))
            return aList


    

