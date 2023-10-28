import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *


monApp = QtWidgets.QApplication([])


myModel = SGModel(
    900, 900, x=5, windowTitle="dev project : Rehab Game - Player 1", typeOfLayout="grid")

aGrid = myModel.newGrid(5, 4, "square", size=60, gap=0,
                        name='grid1')  # ,posXY=[20,90]
aGrid.setCells("Resource", 1)
aGrid.setCells("ProtectionLevel", "Free")
aGrid.setCell(3,1,"Resource", 2)
aGrid.setCell(1,2,"Resource", 2)
aGrid.setCell(2,2,"Resource", 0)
aGrid.setCell(3,2,"Resource", 2)
aGrid.setCell(4,2,"Resource", 3)
aGrid.setCell(5,2,"Resource", 2)
aGrid.setCell(2,3,"Resource", 3)
aGrid.setCell(4,3,"Resource", 2)
aGrid.setCell(2,4,"Resource", 3)
aGrid.setCell(4,4,"Resource", 0)
aGrid.setCell(5,4,"Resource", 2)

# GlobalColor.
myModel.newPov("Resource", "Resource", {
               0: Qt.white, 1: Qt.green, 2: QColor.fromRgb(30,190,0), 3: QColorConstants.DarkGreen})
myModel.newBorderPov("ProtectionLevel", "ProtectionLevel", {
                     "Reserve": Qt.magenta, "Free": Qt.black})

Workers = myModel.newAgentSpecies(
    "Workers", "triangleAgent1", {'harvest':{0}},uniqueColor=Qt.black)
# Workers.initDefaultAttValue('harvest',0)
Birds = myModel.newAgentSpecies(
    "Birds", "triangleAgent2", uniqueColor=Qt.yellow)

aWorker = myModel.newAgentAtCoords(aGrid,Workers,5,2)


# globalLegend = myModel.newLegendAdmin("Global Legend", showAgentsWithNoAtt=True)

Player1 = myModel.newPlayer("Harvesters")
Player1.addGameAction(myModel.newCreateAction(Workers, 20))
Player1.addGameAction(myModel.newDeleteAction(Workers, "infinite"))
Player1.addGameAction(myModel.newUpdateAction('Cell', 3, {"Resource": 3}))
Player1.addGameAction(myModel.newMoveAction(Workers, 1))
Player1ControlPanel = Player1.newControlPanel(showAgentsWithNoAtt=True)

Player2 = myModel.newPlayer("Parc")

Player2.addGameAction(myModel.newUpdateAction(
    "Cell", "infinite", {"ProtectionLevel": "Reserve"}
    ,[lambda: aGrid.nbCells_withValue("ProtectionLevel","Reserve")<3]))
Player2.addGameAction(myModel.newUpdateAction(
    "Cell", "infinite", {"ProtectionLevel": "Free"}))
Player2ControlPanel = Player2.newControlPanel()

myModel.timeManager.newGamePhase('Phase 1', [Player1,Player2])
# harvestWhenOneHarvester=myModel.newModelAction(lambda: harvest(myModel.getCells()))
# harvestWhenOneHarvester=myModel.newModelAction_onCells(lambda cell: cell.getAgents()[0].incValue('harvest',min(2,cell.value('Resource'))), lambda cell: cell.nbAgents()==1   )
# harvestWhenOneHarvester=myModel.newModelAction_onCells(lambda cell: harvest2(cell))
harvestWhenOneHarvester=myModel.newModelAction(lambda: harvest3())
myModel.timeManager.newModelPhase(harvestWhenOneHarvester)

def harvest3():
    for cell in myModel.getCells():
        if cell.nbAgents()==1:
            aQt = min(2,cell.value('Resource'))
            cell.getAgents()[0].incValue('harvest',aQt)
            cell.decValue('Resource',aQt)
def harvest2(cell):
    print(myModel)
    if cell.nbAgents()==1:
        aQt = min(2,cell.value('Resource'))
        cell.getAgents()[0].incValue('harvest',aQt)
        cell.decValue('Resource',aQt)

def harvest(cells):
    for cell in cells:
        if cell.nbAgents()==1:
            aQt = min(2,cell.value('Resource'))
            cell.getAgents()[0].incValue('harvest',aQt)
            cell.decValue('Resource',aQt)
    return 1    

# myModel.timeManager.newModelPhase(lambda: harvest())

myModel.timeManager.newModelPhase(myModel.newModelAction_onCells(lambda cell: harvest2(cell)))

def harvest():
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

# myModel.timeManager.newModelPhase([lambda: aGrid.setRandomCell("Resource",3),lambda: aGrid.setRandomCells("Resource",1,3)])
# aModelAction2=myModel.newModelAction(lambda: aGrid.setRandomCells("Resource",3,2,condition=(lambda x: x.value("Resource") != 1 and x.value("Resource") != 0  )))
# myModel.timeManager.newModelPhase(aModelAction2)
# aModelAction4=myModel.newModelAction(lambda: aGrid.setRandomCells("landUse","forest",2))
# aModelAction4.addCondition(lambda: myModel.getCurrentRound()==2) 

GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.red)
# myModel.currentPlayer = 'Player 1'

userSelector=myModel.newUserSelector()

TextBox = myModel.newTextBox(
    title='Info', textToWrite="Welcome to ReHab game !")

# TextBox.addText("J'espère que vous allez bien!!!", toTheLine=True)

DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.red)
i1 = DashBoard.addIndicator("sum", 'cell', attribute='Resource',color=Qt.black)
i2 = DashBoard.addIndicator("avg", 'cell', attribute='Resource',color=Qt.black)
i3 = DashBoard.addIndicator("score",None,indicatorName="Score : ")
DashBoard.showIndicators()
# aModelAction4.addFeedback(lambda: i3.setResult(i3.result + 5))
# myModel.timeManager.newModelPhase(aModelAction4)


endGameRule = myModel.newEndGameRule(numberRequired=2)
endGameRule.addEndGameCondition_onIndicator(
    i1, "equal", 90, name="Resource equal to 90")
endGameRule.addEndGameCondition_onEntity(
    "cell1-2", 'Resource', "greater", 2, name="Cell 1-2 Resource is greater than 2",aGrid=aGrid)
endGameRule.showEndGameConditions()


myModel.launch()
# myModel.launch_withMQTT("Instantaneous") # https://mosquitto.org/download/


sys.exit(monApp.exec_())

