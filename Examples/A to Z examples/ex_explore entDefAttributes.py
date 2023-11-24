import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(400,400)

Square = myModel.newGrid(5, 5, "square",size=45)
Square.setEntities("status",'black')
Square.setEntities("status",'white',lambda c: c.id%2==0)
Square.newPov("default","status",{"black":QColor.fromRgb(56, 62, 66),"white":QColor.fromRgb(254, 254, 226)})

Pawn=myModel.newAgentSpecies(name="Pawn",shape='ellipseAgent1',defaultSize=15,defaultColor=QColor.fromRgb(196,88,36))
# Pawn=myModel.newAgentSpecies(name="Pawn",shape='circleAgent',defaultSize=8,defaultColor=QColor.fromRgb(196,88,36))
        # TODO: circleAgent ne fonctionne pas comme shape.
Pawn.newAgentAtRandom(Square)

myModel.launch() 

sys.exit(monApp.exec_())
