import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGSGE import *


monApp=QtWidgets.QApplication([])

myModel=SGModel(1800,900, windowTitle="dev project : Rehab Game", typeOfLayout ="grid")

aGrid=myModel.newGrid(7,7,"square",size=60, gap=2,name='grid1')
aGrid.setValueCell("resource","R2")
aGrid.setRandomCells("resource","R3",7)
aGrid.setRandomCells("resource","R1",3)
aGrid.setRandomCells("resource","R0",2)


myModel.newPov("Resources","resource",{"R3":Qt.darkGreen,"R2":Qt.green,"R1":Qt.yellow,"R0":Qt.white})

Workers=myModel.newAgentSpecies("Workers","triangleAgent1",uniqueColor=Qt.black)
Birds=myModel.newAgentSpecies("Birds","triangleAgent2",uniqueColor=Qt.yellow)

w1=myModel.newAgent(aGrid,Workers)
b1=myModel.newAgent(aGrid,Birds)


theFirstLegend=myModel.newLegendAdmin()


GameRounds=myModel.newTimeLabel()
myModel.timeManager.newGamePhase('Phase 1')
myModel.timeManager.newGamePhase('Phase 2')

TextBox=myModel.newTextBox(title='Début du jeu',textToWrite='Bonjour!')

TextBox.addText("J'espère que vous allez bien!!!")
TextBox.setTextColor()

myModel.iAm("Admin")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())