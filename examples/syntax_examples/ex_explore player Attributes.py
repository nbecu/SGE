import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(400,400)
myModel.displayTimeInWindowTitle()

Square = myModel.newCellsOnGrid(5, 5, "square",size=45)
Square.setEntities("status",'black')
Square.setEntities("status",'white',lambda c: c.id%2==0)
Square.newPov("default","status",{"black":QColor.fromRgb(56, 62, 66),"white":QColor.fromRgb(254, 254, 226)})

player_Clara = myModel.newPlayer('Clara',attributesAndValues={'foo':5})
player_Clara.setValue('Clara score',0)


aPhase = myModel.newModelPhase((lambda: player_Clara.incValue('Clara score',3)))

resetScoreAction=myModel.newModelAction((lambda : player_Clara.setValue('Clara score',0)),(lambda: myModel.roundNumber()%4==0))
aPhase.addAction(resetScoreAction)

dashboard = myModel.newDashBoard()
dashboard.addIndicatorOnEntity(player_Clara,'foo')
dashboard.addIndicatorOnEntity(player_Clara,"Clara score")

myModel.launch() 
sys.exit(monApp.exec_())
