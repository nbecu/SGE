import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(600,600, windowTitle="Step 2 (2) : Points of view and colors")

aGrid=myModel.newGrid(10,10,"square",Qt.gray,size=50,gap=8)
aGrid.setCells("landUse","grass")
aGrid.setCells_withColumn("landUse","forest",1)
aGrid.setCells_withColumn("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

myModel.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen},[aGrid])
myModel.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen},[aGrid])

#You can change the initial pov displayed with the instruction setInitialPov()
myModel.setInitialPov("ICantSeeShrub")
#If you don't set the initial pov, the first one which has been declared will be the initial one
#You can change POV by using the eye of the Model toolbar

myModel.launch() 

sys.exit(monApp.exec_())
