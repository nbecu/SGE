import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(600,600, windowTitle="Step 2 (2) : Points of view and colors")

Cell=myModel.newCellsOnGrid(10,10,"square",color=Qt.gray,size=40,gap=8)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

#You can change the initial pov displayed with the instruction setInitialPov()
Cell.setInitialPov("ICantSeeShrub")
#If you don't set the initial pov, the first one which has been declared will be the initial one
#You can change POV by using the eye of the Model toolbar

myModel.launch() 

sys.exit(monApp.exec_())
