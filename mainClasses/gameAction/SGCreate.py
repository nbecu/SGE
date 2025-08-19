from mainClasses.SGLegendItem import SGLegendItem
from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
from PyQt5.QtWidgets import QInputDialog



#Class who manage the game mechanics of creation
class SGCreate(SGAbstractAction):
    def __init__(self,entDef,dictAttributs,number,conditions=[],feedBack=[],conditionOfFeedBack=[],nameToDisplay=None,setControllerContextualMenu=False , create_several_at_each_click = False, writeAttributeInLabel=False):
        super().__init__(entDef,number,conditions,feedBack,conditionOfFeedBack,nameToDisplay,setControllerContextualMenu)
        self.dictAttributs=dictAttributs
        if nameToDisplay is None:
            self.nameToDisplay="+"
            if self.dictAttributs is not None:
                textAttributes = ' ('
                for aAtt,aVal in self.dictAttributs.items():
                    if writeAttributeInLabel:
                        textAttributes = textAttributes + f'{aAtt}→{aVal},'
                    else:
                        textAttributes = textAttributes + f'{aVal},'
                textAttributes = textAttributes[:-1]+')'
                self.nameToDisplay += textAttributes
            else:
                self.nameToDisplay += " create"
        else:
            self.nameToDisplay=nameToDisplay
        self.actionType="Create"
        self.addCondition(lambda aTargetEntity: aTargetEntity.classDef.entityType() == 'Cell')
        self.create_several_at_each_click=create_several_at_each_click


    def executeAction(self, aTargetEntity):
        nbOfAgents = 1 if not self.create_several_at_each_click else self.numberOfAgentsToCreate()
        listOfNewAgents = [self.targetEntDef.newAgentOnCell(aTargetEntity, self.dictAttributs) for _ in range(nbOfAgents)]
        return listOfNewAgents[0] if len(listOfNewAgents) == 1 else listOfNewAgents or None

    def numberOfAgentsToCreate(self):
        number, ok = QInputDialog.getInt(None, f"Create {self.targetEntDef.entityName}", "Number to create:", 1, 1)
        if ok:
            return number
        return 0

    def generateLegendItems(self,aControlPanel):
        if self.setControllerContextualMenu == False:
            if self.dictAttributs is None:
                aColor = self.targetEntDef.defaultShapeColor
                return [SGLegendItem(aControlPanel,'symbol',self.nameToDisplay,self.targetEntDef,aColor,gameAction=self)]
            else:
                aList = []
                for aAtt, aValue in self.dictAttributs.items():
                    aColor = self.targetEntDef.getColorOrColorandWidthOfFirstOccurenceOfAttAndValue(aAtt,aValue)
                    
                    #todo Modifs pour MTZC pour que ce soit plus simple
                    aList.append(SGLegendItem(aControlPanel,'symbol',self.nameToDisplay,self.targetEntDef,aColor,aAtt,aValue,gameAction=self))
                return aList


    

