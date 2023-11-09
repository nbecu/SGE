import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1700,800, windowTitle="Delmoges_FR", typeOfLayout ="grid")

aGrid=myModel.newGrid(10,10,"square",size=60,gap=1)
aGrid.setCells("type","mer")
aGrid.setCells("sédim","sable")
aGrid.setCells_withColumn("type","grandFond",1)
aGrid.setCells_withColumn("type","côte",10)
aGrid.setCells_withColumn("sédim","côte",10)
aGrid.setCells_withColumn("sédim","vase",1)
aGrid.setCell(3,4,"sédim","rocher")
aGrid.setCell(10,1,"type",'port')
aGrid.setCells("stockCellMerlu",0)
aGrid.setCells("stockCellSole",0)
aGrid.setCells("txPrésenceMerlu",0)
aGrid.setCells("txPrésenceSole",0)
aGrid.setCells("quantitéPêchéeMerlu",0)
aGrid.setCells("quantitéPêchéeSole",0)

myModel.newPov("Cell Type","type",{"côte":Qt.green,"mer":Qt.cyan,"grandFond":Qt.blue,"port":Qt.darkGray})
myModel.newPov("Sédim","sédim",{"sable":Qt.yellow,"vase":Qt.darkGreen,"rocher":Qt.red,"côte":Qt.darkGray})

Soles=myModel.newAgentSpecies("Sole","triangleAgent1",{"stock":{5478},"txrenouv":{1.0003},"txSable":{1},"txVase":{0.75},"txRocher":{0}},uniqueColor=Qt.yellow,aSpeciesDefaultSize=20)
Merlus=myModel.newAgentSpecies("Merlu","triangleAgent2",{"stock":{39455},"txrenouv":{1.0219},"txSable":{1},"txVase":{1},"txRocher":{1}},uniqueColor=Qt.green,aSpeciesDefaultSize=20)
Navires=myModel.newAgentSpecies("Navire","arrowAgent1",{"txCapture_Sole":{2.75E-5},"txCapture_Merlu":{3.76E-5},"Quantité_pêchée_Merlu":{0},"Quantité_pêchée_Sole":{0}},uniqueColor=Qt.darkBlue,aSpeciesDefaultSize=20)
myModel.newAgentAtCoords(aGrid,Navires,10,1)
myModel.newAgentAtCoords(aGrid,Navires,10,1)
myModel.newAgentAtCoords(aGrid,Navires,10,1)
myModel.newAgentAtCoords(aGrid,Navires,10,1)
myModel.newAgentAtCoords(aGrid,Navires,10,1)
Player1 = myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.newMoveAction(Navires, 'infinite'))

myModel.newTextBox("Place les bateaux à l'endroit où ils doivent pêcher","Comment jouer ?")
myModel.newLegendAdmin(showAgentsWithNoAtt=True)


def tx_présence():
    for Species in myModel.getAgentSpecies():
        for cell in myModel.getCells():  
            pass  
    pass

myModel.launch()
sys.exit(monApp.exec_())