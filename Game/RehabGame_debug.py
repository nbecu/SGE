import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGSGE import *


monApp=QtWidgets.QApplication([])

myModel=SGModel(1800,900, windowTitle="dev project : Rehab Game", typeOfLayout ="grid")

aGrid=myModel.newGrid(7,7,"square",size=60, gap=2,name='grid1')
aGrid.setValueCell("Resource","2")
aGrid.setRandomCells("Resource","3",7)
aGrid.setRandomCells("Resource","1",3)
aGrid.setRandomCells("Resource","0",2)


myModel.newPov("Resource","Resource",{"3":Qt.darkGreen,"2":Qt.green,"1":Qt.yellow,"0":Qt.white})

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

DashBoard=myModel.newDashBoard()
DashBoard.addIndicator("sumAtt",'cell','Resource')
DashBoard.show()

#"Indicateur test","sumAtt","Resource",2,
myModel.iAm("Admin")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())