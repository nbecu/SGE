import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1530,830, windowTitle="About pov (2)")

aGrid=myModel.createGrid(10,10,"square",Qt.gray,size=75)
aGrid.setValueForCells({"landUse":"grass"})
aGrid.setForX({"landUse":"forest"},1)
aGrid.setForX({"landUse":"forest"},2)
aGrid.setForRandom({"landUse":"shrub"},10)


myModel.setUpPov("ICanSeeShrub",{"landUse":{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen}},[aGrid])
myModel.setUpPov("ICantSeeShrub",{"landUse":{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen}},[aGrid])


#You can change the initial pov displayed with the instruction setInitialPov()
myModel.setInitialPov("ICantSeeShrub")
#If you don't set the initial pov, the first one which has been declared will be the initial one

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
