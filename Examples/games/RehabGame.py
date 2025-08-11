import sys
import random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *


monApp = QtWidgets.QApplication([])


myModel = SGModel(
    700, 500, x=5, windowTitle="dev project : Rehab Game - Player 1", typeOfLayout="grid")

Cell = myModel.newCellsOnGrid(5, 4, "square", size=60, gap=0,
                        name='grid1')
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

Cell.displayBorderPov('Parc info')

harvesters = myModel.newAgentSpecies(
    "harvesters", "triangleAgent1", {'total harvest':{0},'harvest':{0}})
harvesters.setDefaultValue('harvest',0)
harvesters.setDefaultValue('total harvest',0)

Bird = myModel.newAgentSpecies("Bird", "triangleAgent2", {'nb reproduction':{0,1,2}}, defaultColor=Qt.yellow)

Bird.setDefaultValue('nb reproduction',0)

Chick = myModel.newAgentSpecies("Chick","triangleAgent2", defaultSize=5, defaultColor=QColorConstants.Magenta)



Clans = myModel.newPlayer("Clan")
Clans.addGameAction(myModel.newCreateAction(harvesters, aNumber=20))

Player1ControlPanel = Clans.newControlPanel(showAgentsWithNoAtt=True)

Parc = myModel.newPlayer("Parc")

Parc.addGameAction(myModel.newModifyAction(
    Cell, {"ProtectionLevel": "Reserve"}, conditions = [lambda: Cell.nb_withValue("ProtectionLevel","Reserve")<3]))
Parc.addGameAction(myModel.newModifyAction(
    Cell, {"ProtectionLevel": "Free"}))
Player2ControlPanel = Parc.newControlPanel()


firstPhase = myModel.timeManager.newModelPhase(name='Birds Settle')
firstPhase.addAction(lambda: harvesters.setEntities('harvest',0))
settleAction= myModel.newModelAction_onCells(lambda cell: cell.newAgentHere(Bird),(lambda cell: cell.value('biomass')>=2))
firstPhase.addAction(settleAction)

myModel.timeManager.newPlayPhase('Parc actions', [Parc])
myModel.timeManager.newPlayPhase('Clans actions', [Clans])

myModel.timeManager.newModelPhase(myModel.newModelAction_onCells(lambda cell: allocateHarvests(cell)),name='harvest updated')

myModel.timeManager.newModelPhase(myModel.newModelAction_onAgents('Bird',lambda bird: reproduce(bird)),name='Bird reproduction')


def reproduce(aBird):
    if aBird.cell.nbAgents('harvesters') == 0 :
        listQuietNeighbours = [aCell for aCell in aBird.getNeighborCells() if aCell.nbAgents('harvesters') == 0 ]
        nbQuietNeighbours = len(listQuietNeighbours)
        ratioQuietness = float(nbQuietNeighbours / len(aBird.getNeighborCells()))
        if (ratioQuietness > 0.5) & (ratioQuietness < 0.8) : aBird.setValue('nb reproduction',1)
        elif ratioQuietness >= 0.8 : aBird.setValue('nb reproduction',2)
    for i in range(aBird.value('nb reproduction')):
        aBird.cell.newAgentHere(Chick)

myModel.timeManager.newModelPhase(myModel.newModelAction_onCells(lambda cell: renewBiomass(cell)),name='biomass updated')
myModel.timeManager.newModelPhase(lambda : myModel.deleteAllAgents(),name='gameboard cleared')


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


GameRounds = myModel.newTimeLabel(None, Qt.white, Qt.black, Qt.red)


userSelector=myModel.newUserSelector()

TextBox = myModel.newTextBox(
    title='Info', textToWrite="Welcome to ReHab game !")

DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.red)
i1 = DashBoard.addIndicator(Cell, "sumAtt", attribute='biomass',color=Qt.black, title='Total biomass')
i2 = DashBoard.addIndicator(Cell, "avgAtt", attribute='biomass',color=Qt.black, title='Avg biomass')
i3 = DashBoard.addIndicator('harvesters', "sumAtt", attribute='harvest',color=Qt.black)
i4 = DashBoard.addIndicator('harvesters', "sumAtt", attribute='total harvest',color=Qt.black)
i5 = DashBoard.addIndicator('Bird',"nb", color=Qt.magenta)
i6 = DashBoard.addIndicator('Bird', "sumAtt", attribute='nb reproduction',color=Qt.magenta)


myModel.launch()
# myModel.launch_withMQTT("Instantaneous") # https://mosquitto.org/download/


sys.exit(monApp.exec_())

