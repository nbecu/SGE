import sys
import random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *


monApp = QtWidgets.QApplication([])


myModel = SGModel(
    900, 900, x=5, windowTitle="dev project : Rehab Game - Player 1", typeOfLayout="grid")

Cell = myModel.newGrid(5, 4, "square", size=60, gap=0,
                        name='grid1')  # ,posXY=[20,90]
Cell.setEntities("biomass", 1)
Cell.setEntities("ProtectionLevel", "Free")
Cell.setEntities("noHarvestPeriod", 0)
Cell.setCell(3,1,"biomass", 2)
Cell.setCell(1,2,"biomass", 2)
Cell.setCell(2,2,"biomass", 0)
Cell.setCell(3,2,"biomass", 2)
Cell.setCell(4,2,"biomass", 3)
Cell.setCell(5,2,"biomass", 2)
Cell.setCell(2,3,"biomass", 3)
Cell.setCell(4,3,"biomass", 2)
Cell.setCell(2,4,"biomass", 3)
Cell.setCell(4,4,"biomass", 0)
Cell.setCell(5,4,"biomass", 2)

# GlobalColor.
Cell.newPov("biomass", "biomass", {
               0: Qt.white, 1: Qt.green, 2: QColor.fromRgb(30,190,0), 3: QColorConstants.DarkGreen})
Cell.newBorderPov("Parc info", "ProtectionLevel", {
                     "Reserve": Qt.magenta, "Free": Qt.black})

harvesters = myModel.newAgentSpecies(
    "harvesters", "triangleAgent1", {'total harvest':{0},'harvest':{0}},uniqueColor=Qt.black)
harvesters.setDefaultValue('harvest',0)
harvesters.setDefaultValue('total harvest',0)
# aHarvester = myModel.newAgentAtCoords(Cell,harvesters,5,2)
Bird = myModel.newAgentSpecies("Bird", "triangleAgent2", {'nb reproduction':{0,1,2}}, uniqueColor=Qt.yellow)
# Bird.newPov("Bird -> repro","nb reproduction",{0:Qt.yellow,1:QColor.fromRgb(170,205,50),2:Qt.green})
# Bird.newPov("Bird -> repro","nb reproduction",{0:Qt.yellow,1:Qt.black,2:Qt.green})
Bird.setDefaultValue('nb reproduction',0)

Chick = myModel.newAgentSpecies("Chick","triangleAgent2", defaultSize=5, uniqueColor=QColorConstants.Magenta)


# globalLegend = myModel.newLegend("Global Legend", showAgentsWithNoAtt=True)

Clans = myModel.newPlayer("Clan")
Clans.addGameAction(myModel.newCreateAction(harvesters, 20))
# Clans.addGameAction(myModel.newDeleteAction(harvesters, "infinite"))
# Clans.addGameAction(myModel.newUpdateAction('Cell', 3, {"biomass": 3}))
# Clans.addGameAction(myModel.newMoveAction(harvesters, 1))
Player1ControlPanel = Clans.newControlPanel(showAgentsWithNoAtt=True)

Parc = myModel.newPlayer("Parc")

Parc.addGameAction(myModel.newUpdateAction(
    "Cell", "infinite", {"ProtectionLevel": "Reserve"}
    ,[lambda: Cell.nbCells_withValue("ProtectionLevel","Reserve")<3]))
Parc.addGameAction(myModel.newUpdateAction(
    "Cell", "infinite", {"ProtectionLevel": "Free"}))
Player2ControlPanel = Parc.newControlPanel()


firstPhase = myModel.timeManager.newModelPhase(name='Birds Settle')
firstPhase.addModelAction(lambda: harvesters.setEntities('harvest',0))
#faut changer le nom addModelAction() par addAction()
settleAction= myModel.newModelAction_onCells(lambda cell: cell.newAgentHere(Bird),(lambda cell: cell.value('biomass')>=2))
firstPhase.addModelAction(settleAction)

myModel.timeManager.newGamePhase('Parc actions', [Parc])
myModel.timeManager.newGamePhase('Clans actions', [Clans])

# myModel.timeManager.newModelPhase(myModel.newModelAction_onCells(lambda cell: harvest(cell)))
myModel.timeManager.newModelPhase(myModel.newModelAction_onCells(lambda cell: allocateHarvests(cell)))

myModel.timeManager.newModelPhase(myModel.newModelAction_onAgents('Bird',lambda bird: reproduce(bird)),name='Bird reproduction')


def reproduce(aBird):
    if aBird.cell.nbAgents('harvesters') == 0 :
        listQuietNeighbours = [aCell for aCell in aBird.cell.getNeighborCells() if aCell.nbAgents('harvesters') == 0 ]
        nbQuietNeighbours = len(listQuietNeighbours)
        ratioQuietness = float(nbQuietNeighbours / len(aBird.cell.getNeighborCells()))
        if (ratioQuietness > 0.5) & (ratioQuietness < 0.8) : aBird.setValue('nb reproduction',1)
        elif ratioQuietness >= 0.8 : aBird.setValue('nb reproduction',2)
    for i in range(aBird.value('nb reproduction')):
        aBird.cell.newAgentHere(Chick)

myModel.timeManager.newModelPhase(myModel.newModelAction_onCells(lambda cell: renewBiomass(cell)),name='update biomass')
myModel.timeManager.newModelPhase(lambda : myModel.deleteAllAgents(),name='Clear the gameboard')


# def harvest(cell):
#     if cell.nbAgents()==1:
#         aQt = min(2,cell.value('biomass'))
#         cell.getAgents()[0].incValue('total harvest',aQt)
#         cell.getAgents()[0].setValue('harvest',aQt)
#         cell.decValue('biomass',aQt)
#     elif cell.nbAgents()>1:
#         aQt = min(2,cell.value('biomass'))
#         for aAgt in random.sample(cell.getAgents(), aQt):
#             aAgt.incValue('total harvest',1)
#             aAgt.setValue('harvest',1)
#             cell.decValue('biomass',1)

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
# myModel.setCurrentPlayer('Player 1')

userSelector=myModel.newUserSelector()

TextBox = myModel.newTextBox(
    title='Info', textToWrite="Welcome to ReHab game !")

# TextBox.addText("J'espère que vous allez bien!!!", toTheLine=True)

DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.red)
i1 = DashBoard.addIndicator("sumAtt", Cell, attribute='biomass',color=Qt.black, indicatorName='Total biomass')
i2 = DashBoard.addIndicator("avgAtt", Cell, attribute='biomass',color=Qt.black, indicatorName='Avg biomass')
i3 = DashBoard.addIndicator("sumAtt", 'harvesters', attribute='harvest',color=Qt.black)
i4 = DashBoard.addIndicator("sumAtt", 'harvesters', attribute='total harvest',color=Qt.black)
i5 = DashBoard.addIndicator("nb", 'Bird',color=Qt.magenta)
i6 = DashBoard.addIndicator("sumAtt", 'Bird', attribute='nb reproduction',color=Qt.magenta)

DashBoard.showIndicators()

# endGameRule = myModel.newEndGameRule(numberRequired=2)
# endGameRule.addEndGameCondition_onIndicator(
#     i1, "equal", 90, name="biomass equal to 90")
# endGameRule.addEndGameCondition_onEntity(
#     "cell1-2", 'biomass', "greater", 2, name="Cell 1-2 biomass is greater than 2",Cell=Cell)
# endGameRule.showEndGameConditions()


myModel.launch()
# myModel.launch_withMQTT("Instantaneous") # https://mosquitto.org/download/


sys.exit(monApp.exec_())

