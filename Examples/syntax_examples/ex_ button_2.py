import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
import random

monApp = QtWidgets.QApplication([])


myModel = SGModel(280, 200)


score=myModel.newSimVariable('Score',0, Qt.blue)
dash=myModel.newDashBoard()
dash.moveToCoords(80,50)
dash.addIndicatorOnSimVariable(score)
dash.addSeparator() 

# This implementation should be avoided, as the actions won't be taken into account in a distributed simulation between multiple computers
# Instead, use gameActions in buttons, so that it will be taken into account on distributed computers
myModel.newButton((lambda: score.incValue(10)),'Add 10',(80,110))
myModel.newButton((lambda: score.setValue(0)),'Reset',(80,150))



myModel.launch()
sys.exit(monApp.exec_())

