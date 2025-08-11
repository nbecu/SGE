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

gameAction_add10 =myModel.newActivateAction(None,"add10")
def add10():
    score.incValue(10)
player_Salim.addGameAction(gameAction_add10)

myModel.newButton(gameAction_add10,'Add 10',(80,110))

PlayPhase = myModel.timeManager.newPlayPhase('Game phase',[player_Salim])

# This implementation should be avoided, as the actions won't be taken into account in a distributed simulation between multiple computers
# Instead, use gameActions in buttons, so that it will be taken into account on distributed computers
myModel.newButton((lambda: score.setValue(0)),'Reset',(80,150))
myModel.newButton((lambda: addGivenValue()),'Add "x"',(80,180))


from tkinter import simpledialog
def addGivenValue():
    userDefinedValue = simpledialog.askinteger("Input", "Enter a value between 1 and 100:",  
                                             minvalue=1, maxvalue=100)
    score.incValue(userDefinedValue)
    

myModel.launch()
sys.exit(monApp.exec_())

