import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])


myModel = SGModel(280, 230)
myModel.displayTimeInWindowTitle()

### THIS CASE IS FOR ACTIVATE ACTION IN A BUTTON BUT IT DOES NOT WORK YET

score=myModel.newSimVariable('Score',0, Qt.blue)
dash=myModel.newDashBoard()
dash.moveToCoords(80,50)
dash.addIndicatorOnSimVariable(score)
dash.addSeparator() 


player_Salim = myModel.newPlayer('Salim')
myModel.setCurrentPlayer(player_Salim)

# player_Salim.newControlPanel()
gameAction_add10=myModel.newActivateAction(None,
                                        lambda : add10(),
                                        setControllerButton=(80,110),
                                        label="add 10")
player_Salim.addGameAction(gameAction_add10)
PlayPhase = myModel.newPlayPhase('Play phase',[player_Salim])
# This implementation should be avoided, as the actions won't be taken into account in a distributed simulation between multiple computers
# Instead, use gameActions in buttons, so that it will be taken into account on distributed computers
myModel.newButton((lambda: score.setValue(0)),'Reset',(80,150))
myModel.newButton((lambda: addGivenValue()),'Add "x"',(80,180))



def add10():
    score.incValue(10)

def addGivenValue():
    userDefinedValue = simpledialog.askinteger("Input", "Enter a value between 1 and 100:",  
                                             minvalue=1, maxvalue=100)
    score.incValue(userDefinedValue)
    

# myModel.newUserSelector()

myModel.launch()
sys.exit(monApp.exec_())

