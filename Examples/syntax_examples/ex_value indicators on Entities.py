import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(400,400)

Square = myModel.newCellsOnGrid(5, 5, "square",size=45)
Square.setEntities("status",'black')
Square.setEntities("status",'white',lambda c: c.id%2==0)
Square.newPov("default","status",{"black":QColor.fromRgb(56, 62, 66),"white":QColor.fromRgb(254, 254, 226)})

Pawn=myModel.newAgentSpecies(name="Pawn",shape='circleAgent',defaultSize=8,defaultColor=QColor.fromRgb(196,88,36))

Pawn.setDefaultValue('age',(lambda: random.randint(12, 99)))

Pawn.newAgentAtRandom(Square)
Pawn.newAgentsAtRandom(3, Square)

def step2():
        Pawn.moveRandomly()
        a1= Pawn.getEntity(1)
        a1.incValue('age',2)
        a2=Pawn.getEntity(2)
        a2.incValue('age')
myModel.timeManager.newModelPhase(lambda: step2())

scores = myModel.newDashBoard()
scores.addIndicatorOnEntity(Pawn.getEntity(1),'age')
scores.addIndicatorOnEntity(Pawn.getEntity(2),'age')
scores.addIndicator(Pawn,'avgAtt',attribute='age')

myModel.launch() 
sys.exit(monApp.exec_())
