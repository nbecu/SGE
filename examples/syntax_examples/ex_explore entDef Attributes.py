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

Pawn=myModel.newAgentType(name="Pawn",shape='ellipseAgent1',entDefAttributesAndValues={'foo':5})


Pawn.calcValue('foo',(lambda x: 2*x*x+ 5*x -14))

myModel.newModelPhase((lambda: Pawn.decValue('foo',1)))


dashboard = myModel.newDashBoard()
dashboard.addIndicatorOnEntity(Pawn,'foo')

myModel.launch() 
sys.exit(monApp.exec_())
