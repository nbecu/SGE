import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1700,800, windowTitle="Delmoges_FR", typeOfLayout ="grid")

aGrid=myModel.newGrid(10,10,"square",gap=1)
aGrid.setCells("type","mer")
aGrid.setCells("sédim","sable")
aGrid.setCells_withColumn("type","grandFond",1)
aGrid.setCells_withColumn("type","côte",10)
aGrid.setCells_withColumn("sédim","côte",10)
aGrid.setCells_withColumn("sédim","vase",1)
aGrid.setCell(3,4,"sédim","rocher")

myModel.newPov("Cell Type","type",{"côte":Qt.green,"mer":Qt.cyan,"grandFond":Qt.blue})
myModel.newPov("Sédim","sédim",{"sable":Qt.yellow,"vase":Qt.darkGreen,"rocher":Qt.red,"côte":Qt.darkGray})

Soles=myModel.newAgentSpecies("Sole","triangleAgent1",{"stock":{200},"txrenouv":{0.1}},uniqueColor=Qt.yellow)
Merlus=myModel.newAgentSpecies("Merlu","triangleAgent2",{"stock":{350},"txrenouv":{0.2}},uniqueColor=Qt.green)
Navires=myModel.newAgentSpecies("Navire","arrowAgent1",{"txCapture_Sole":{0.4},"txCapture_Merlu":{0.5},"Quantité_pêchée":{0}},uniqueColor=Qt.green)
myModel.newAgentAtCoords(aGrid,Navires,10,1)
myModel.newAgentAtCoords(aGrid,Navires,10,1)
myModel.newAgentAtCoords(aGrid,Navires,10,1)
myModel.newAgentAtCoords(aGrid,Navires,10,1)
myModel.newAgentAtCoords(aGrid,Navires,10,1)
Player1 = myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.newMoveAction(Navires, 'infinite'))
Player1ControlPanel = Player1.newControlPanel("Player 1 Actions", showAgentsWithNoAtt=True)

myModel.launch()
sys.exit(monApp.exec_())