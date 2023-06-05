import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(700,600, windowTitle="About pov (1)", typeOfLayout='vertical')

myModel.newTextBox(textToWrite='You can change the point of view (pov), using the "eye" menu in the top panel')

aGrid=myModel.newGrid(10,10,"square",Qt.gray,size=50)
aGrid.setCells("landUse","grass")
aGrid.setCells_withColumn("landUse","forest",1)
aGrid.setCells_withColumn("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

#Pov (point of view), allow to specify different ways to view the state of the cells
#A pov allow to define the color displayed for a certain value of a given attribute of the cell
#In this example there are two pov:
#The first can see the difference between grass and schrub, the second cannot
myModel.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen},[aGrid])
myModel.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen},[aGrid])


myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
