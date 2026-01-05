import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(700,350, windowTitle="Use image for cells and agents")

#A first square grid with triangle agents
Cells=myModel.newCellsOnGrid(4,4,"square",gap=2,size=70)
Cells.setEntities("type","type1")
Cells.setEntities_withColumn("type","type2",1)
Cells.setRandomEntities("type","type3",3)
                
Cells.newPov("standard view","type",{"type1":QPixmap("./images/leaves.png"),
                                     "type2":QPixmap("./images/house2.png"),
                                     "type3":QPixmap("./images/oak-nut.png")})
################
AgentsA=myModel.newAgentType("Agent_A","circleAgent",defaultSize=30,locationInEntity="center")
AgentsA.setDefaultValues({"category":{"cat_1","cat_2"}})

AgentsA.newPov("standard view","category",{'cat_1':QPixmap("./images/shiny-coin1.svg"),
                                           'cat_2':QPixmap("./images/bird1.svg")})

AgentsA.newAgentAtCoords(Cells,2,2,{"category":"cat_1",})
AgentsA.newAgentAtCoords(Cells,3,3,{"category":"cat_2"})


# A second hexagonal grid with square agents
CellsHex = myModel.newCellsOnGrid(4, 4, "hexagonal", gap=0, size=70, backgroundColor=Qt.white)  # Créer une grille hexagonale
CellsHex.setEntities("type", "type1")
CellsHex.setRandomEntities("type", "type2", 4)
CellsHex.setRandomEntities("type", "type3", 3)

CellsHex.newPov("standard view", "type", {"type1": QPixmap("./images/five-petalled_flower.svg"),
                                           "type2": QPixmap("./images/house1.svg"),
                                           "type3": QPixmap("./images/pseudo-globe.svg")})
#############
AgentsB = myModel.newAgentType("Agent_B", "squareAgent", defaultSize=30, locationInEntity="center")  # Agents carrés
AgentsB.setDefaultValues({"category": {"cat_1", "cat_2"}})

AgentsB.newPov("standard view", "category", {'cat_1': QPixmap("./images/horse1.svg"),
                                              'cat_2': QPixmap("./images/fish1.png")})

AgentsB.newAgentAtCoords(CellsHex, 1, 1, {"category": "cat_1",})
AgentsB.newAgentAtCoords(CellsHex, 3, 1, {"category": "cat_1",})
AgentsB.newAgentAtCoords(CellsHex, 2, 2, {"category": "cat_2"})


####################
# aLegend=myModel.newLegend()

myModel.newModelPhase([lambda: AgentsA.moveRandomly(),lambda: AgentsB.moveRandomly()])
myModel.launch() 

sys.exit(monApp.exec_())
