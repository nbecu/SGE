import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *


monApp = QtWidgets.QApplication([])


# STEP1 Model

myModel = SGModel(
    1800, 900, x=5, windowTitle="dev project : Rehab Game", typeOfLayout="grid")


# STEP2 Grid and Cells
aGrid = myModel.newGrid(7, 7, "square", size=60, gap=2,
                        name='grid1')  # ,posXY=[20,90]
aGrid.setCells("Resource", "2")
aGrid.setCells("ProtectionLevel", "Free")
aGrid.setRandomCells("Resource", "3", 7)
aGrid.setRandomCells("Resource", "1", 3)

aGrid.setRandomCells("Resource", "0", 8)
aGrid.setRandomCells("ProtectionLevel", "Reserve", 1)


myModel.newPov("Resource", "Resource", {
               "3": Qt.darkGreen, "2": Qt.green, "1": Qt.yellow, "0": Qt.white})
myModel.newBorderPov("ProtectionLevel", "ProtectionLevel", {
                     "Reserve": Qt.magenta, "Free": Qt.black})

# STEP3 Agents
Workers = myModel.newAgentSpecies(
    "Workers", "triangleAgent1", uniqueColor=Qt.black)
Birds = myModel.newAgentSpecies(
    "Birds", "triangleAgent2", uniqueColor=Qt.yellow)
Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1",{"health":{"good","bad"},"hunger":{"good","bad"}})
Sheeps.newPov("Sheeps -> Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Sheeps -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})

cell_A = aGrid.getCell(4,4)
cell_B = aGrid.getCell(2,2)
cell_C = aGrid.getCell(3,3)

aSecondBird=myModel.placeAgent(cell_A,Birds,None)
aWorker=myModel.placeAgent(cell_B,Workers,None)
aSheep=myModel.placeAgent(cell_C,Sheeps,None)


myModel.launch()


sys.exit(monApp.exec_())

