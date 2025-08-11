import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])



#TODO Cet exemple est en cours.

myModel=SGModel(400,400)
myModel.displayTimeInWindowTitle()

Square = myModel.newCellsOnGrid(5, 5, "square",size=45)
Square.setEntities("status",'black')
Square.setEntities("status",'white',lambda c: c.id%2==0)
Square.newPov("default","status",{"black":QColor.fromRgb(56, 62, 66),"white":QColor.fromRgb(254, 254, 226)})

player_Clara = myModel.newPlayer('Clara',attributesAndValues={'foo':5})
player_Clara.setValue('Clara score',0)
myModel.setCurrentPlayer('Clara')



PlayPhase = myModel.timeManager.newPlayPhase('Play phase',[player_Clara])

myModel.newActivateAction(None,
                                        lambda : printTest(),
                                        setControllerButton=(250,100),
                                        aNameToDisplay="print test")

activatePrint=myModel.newActivateAction(None,
                                        lambda : printTest(),
                                        setControllerContextualMenu=True)
player_Clara.addGameAction(activatePrint)


def printTest():
    print('This is a print test')

dashboard = myModel.newDashBoard()
dashboard.addIndicatorOnEntity(player_Clara,'foo')
dashboard.addIndicatorOnEntity(player_Clara,"Clara score")

myModel.launch() 
sys.exit(monApp.exec_())
