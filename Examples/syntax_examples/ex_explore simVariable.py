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

score1= myModel.newSimVariable('score1',1)
score2= myModel.newSimVariable('score2',1)

a1= myModel.newModelAction(lambda: (score1.incValue(1)))
a2= myModel.newModelAction(lambda: (score2.calcValue(lambda x: x *1.1)))

myModel.timeManager.newModelPhase([a1,a2])

dashboard = myModel.newDashBoard()
dashboard.addIndicatorOnSimVariable(score1)
dashboard.addIndicatorOnSimVariable(score2)

myModel.newTimeLabel()
myModel.launch() 
sys.exit(monApp.exec_())
