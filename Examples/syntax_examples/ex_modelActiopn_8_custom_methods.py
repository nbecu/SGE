import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *


monApp = QtWidgets.QApplication([])


myModel = SGModel(550, 300, windowTitle="How to use modelAction - example 8 Custom methods")

Cell = myModel.newCellsOnGrid(5, 4, "square", size=60, gap=0,name='Cell')
Cell.setEntities("Resource", 1)
Cell.setEntities("ProtectionLevel", "Free")
Cell.setCell(3,1,"Resource", 2)
Cell.setCell(1,2,"Resource", 2)
Cell.setCell(2,2,"Resource", 0)
Cell.setCell(3,2,"Resource", 2)
Cell.setCell(4,2,"Resource", 3)
Cell.setCell(5,2,"Resource", 2)
Cell.setCell(2,3,"Resource", 3)
Cell.setCell(4,3,"Resource", 2)
Cell.setCell(2,4,"Resource", 3)
Cell.setCell(4,4,"Resource", 0)
Cell.setCell(5,4,"Resource", 2)

# GlobalColor.
Cell.newPov("Resource", "Resource", {
               0: Qt.white, 1: Qt.green, 2: QColor.fromRgb(30,190,0), 3: QColorConstants.DarkGreen})
Cell.newBorderPov("ProtectionLevel", "ProtectionLevel", {
                     "Reserve": Qt.magenta, "Free": Qt.black})

Workers = myModel.newAgentSpecies(
    "Workers", "triangleAgent1", {'harvest':{0},'total harvest':{0}})
Workers.setDefaultValue('harvest',0)
Workers.setDefaultValue('total harvest',0)


#modelAction - workers arrive
myModel.timeManager.newModelPhase(lambda: Workers.newAgentsAtRandom(5),name= 'Agents arrive')


#Custom method for modelAction - Example 1
harvestWhenOneHarvester=myModel.newModelAction(lambda: harvest1())
myModel.timeManager.newModelPhase(harvestWhenOneHarvester,name='modelAction: harvest1()')

def harvest1():
    for cell in myModel.getCells():
        if cell.nbAgents()==1:
            aQt = min(2,cell.value('Resource'))
            cell.getAgents()[0].incValue('harvest',aQt)
            cell.decValue('Resource',aQt)

#Custom method for modelAction - Example 2
myModel.timeManager.newModelPhase(myModel.newModelAction_onCells(lambda cell: harvest2(cell)),name='modelAction_onCells: harvest2(cell)')

def harvest2(cell):
    if cell.nbAgents()==1:
        aQt = min(2,cell.value('Resource'))
        cell.getAgents()[0].incValue('total harvest',aQt)
        cell.getAgents()[0].setValue('harvest',aQt)
        cell.decValue('Resource',aQt)
    elif cell.nbAgents()>1:
        aQt = min(2,cell.value('Resource'))
        for aAgt in random.sample(cell.getAgents(), aQt):
            aAgt.incValue('total harvest',1)
            aAgt.setValue('harvest',1)
            cell.decValue('Resource',1)



def harvest1_bis(): #this is an alternative to harvest1()
    for cell in myModel.getCells():
        if cell.nbAgents()==1:
            aQt = min(2,cell.value('Resource'))
            cell.getAgents()[0].incValue('total harvest',aQt)
            cell.getAgents()[0].setValue('harvest',aQt)
            cell.decValue('Resource',aQt)
        elif cell.nbAgents()>1:
            aQt = min(2,cell.value('Resource'))
            for aAgt in random.sample(cell.getAgents(), aQt):
                aAgt.incValue('total harvest',1)
                aAgt.setValue('harvest',1)
                cell.decValue('Resource',1)

#modelAction - workers leave
myModel.timeManager.newModelPhase(lambda: Workers.deleteAllEntities(),name= 'Agents leave')


GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.red)


myModel.launch()
sys.exit(monApp.exec_())

