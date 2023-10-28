import sys
import random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *


monApp = QtWidgets.QApplication([])


myModel = SGModel(
    900, 900, x=5, windowTitle="dev project : Rehab Game - Player 1", typeOfLayout="grid")

aGrid = myModel.newGrid(5, 4, "square", size=60, gap=0,
                        name='grid1')  # ,posXY=[20,90]
aGrid.setCells("biomass", 1)
aGrid.setCells("ProtectionLevel", "Free")
aGrid.setCells("noHarvestPeriod", 0)
aGrid.setCell(3,1,"biomass", 2)
aGrid.setCell(1,2,"biomass", 2)
aGrid.setCell(2,2,"biomass", 0)
aGrid.setCell(3,2,"biomass", 2)
aGrid.setCell(4,2,"biomass", 3)
aGrid.setCell(5,2,"biomass", 2)
aGrid.setCell(2,3,"biomass", 3)
aGrid.setCell(4,3,"biomass", 2)
aGrid.setCell(2,4,"biomass", 3)
aGrid.setCell(4,4,"biomass", 0)
aGrid.setCell(5,4,"biomass", 2)

# GlobalColor.
myModel.newPov("biomass", "biomass", {
               0: Qt.white, 1: Qt.green, 2: QColor.fromRgb(30,190,0), 3: QColorConstants.DarkGreen})
myModel.newBorderPov("ProtectionLevel", "ProtectionLevel", {
                     "Reserve": Qt.magenta, "Free": Qt.black})

harvesters = myModel.newAgentSpecies(
    "harvesters", "triangleAgent1", {'total harvest':{0},'harvest':{0}},uniqueColor=Qt.black)
# harvesters.initDefaultAttValue('harvest',0)
Birds = myModel.newAgentSpecies(
    "Birds", "triangleAgent2", uniqueColor=Qt.yellow)

aWorker = myModel.newAgentAtCoords(aGrid,harvesters,5,2)


# globalLegend = myModel.newLegendAdmin("Global Legend", showAgentsWithNoAtt=True)

Player1 = myModel.newPlayer("Harvesters")
Player1.addGameAction(myModel.newCreateAction(harvesters, 20))
Player1.addGameAction(myModel.newDeleteAction(harvesters, "infinite"))
Player1.addGameAction(myModel.newUpdateAction('Cell', 3, {"biomass": 3}))
Player1.addGameAction(myModel.newMoveAction(harvesters, 1))
Player1ControlPanel = Player1.newControlPanel(showAgentsWithNoAtt=True)

Player2 = myModel.newPlayer("Parc")

Player2.addGameAction(myModel.newUpdateAction(
    "Cell", "infinite", {"ProtectionLevel": "Reserve"}
    ,[lambda: aGrid.nbCells_withValue("ProtectionLevel","Reserve")<3]))
Player2.addGameAction(myModel.newUpdateAction(
    "Cell", "infinite", {"ProtectionLevel": "Free"}))
Player2ControlPanel = Player2.newControlPanel()

myModel.timeManager.newModelPhase(lambda: myModel.setAgents('harvesters','harvest',0))
myModel.timeManager.newGamePhase('Phase 1', [Player1,Player2])
# myModel.timeManager.newModelPhase(lambda: harvest())
# myModel.timeManager.newModelPhase(myModel.newModelAction_onCells(lambda cell: harvest(cell)))
myModel.timeManager.newModelPhase(myModel.newModelAction_onCells(lambda cell: allocateHarvests(cell)))
myModel.timeManager.newModelPhase(myModel.newModelAction_onCells(lambda cell: renewBiomass(cell)))


def harvest(cell):
    if cell.nbAgents()==1:
        aQt = min(2,cell.value('biomass'))
        cell.getAgents()[0].incValue('total harvest',aQt)
        cell.getAgents()[0].setValue('harvest',aQt)
        cell.decValue('biomass',aQt)
    elif cell.nbAgents()>1:
        aQt = min(2,cell.value('biomass'))
        for aAgt in random.sample(cell.getAgents(), aQt):
            aAgt.incValue('total harvest',1)
            aAgt.setValue('harvest',1)
            cell.decValue('biomass',1)

def updateNoHarvestPeriod(cell):
    if len(cell.getAgents('harvesters')) == 0:
        cell.incValue('noHarvestPeriod')
    else:
        cell.setValue('noHarvestPeriod',0)

def allocateHarvests(cell):
    updateNoHarvestPeriod(cell)
    randAgts = random.sample(cell.getAgents('harvesters'), cell.nbAgents('harvesters'))
    if cell.nbAgents('harvesters') > 0:
        if cell.value('biomass') <3:
            randAgts[0].setValue('harvest',cell.value('biomass'))
        else:
            randAgts[0].setValue('harvest',2)
            if len(randAgts)>1:
                randAgts[1].setValue('harvest',1)
    for aAgt in cell.getAgents('harvesters'):
        aAgt.incValue('total harvest',aAgt.value('harvest'))


def renewBiomass(cell):
    nbHarvesters = cell.nbAgents('harvesters')
    if nbHarvesters ==0:
        if cell.value('noHarvestPeriod') == 1: cell.incValue('biomass',1,max=3)
        if cell.value('noHarvestPeriod') == 2: cell.decValue('biomass',1,min=0)
    if nbHarvesters >0: cell.decValue('biomass',nbHarvesters,min=0)


GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.red)
# myModel.currentPlayer = 'Player 1'

userSelector=myModel.newUserSelector()

TextBox = myModel.newTextBox(
    title='Info', textToWrite="Welcome to ReHab game !")

# TextBox.addText("J'espère que vous allez bien!!!", toTheLine=True)

DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.red)
i1 = DashBoard.addIndicator("sum", 'cell', attribute='biomass',color=Qt.black)
i2 = DashBoard.addIndicator("avg", 'cell', attribute='biomass',color=Qt.black)
# i3 = DashBoard.addIndicator("sum", 'harvesters', attribute='harvest',color=Qt.black)
# i4 = DashBoard.addIndicator("sum", 'harvesters', attribute='total harvest',color=Qt.black)
# i3 = DashBoard.addIndicator("score",None,indicatorName="Score : ")
DashBoard.showIndicators()
# aModelAction4.addFeedback(lambda: i3.setResult(i3.result + 5))
# myModel.timeManager.newModelPhase(aModelAction4)


endGameRule = myModel.newEndGameRule(numberRequired=2)
endGameRule.addEndGameCondition_onIndicator(
    i1, "equal", 90, name="biomass equal to 90")
endGameRule.addEndGameCondition_onEntity(
    "cell1-2", 'biomass', "greater", 2, name="Cell 1-2 biomass is greater than 2",aGrid=aGrid)
endGameRule.showEndGameConditions()


myModel.launch()
# myModel.launch_withMQTT("Instantaneous") # https://mosquitto.org/download/


sys.exit(monApp.exec_())

