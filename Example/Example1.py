import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets

monApp=QtWidgets.QApplication([])
#-----------------------------------------------------------
#Example of a simple square grid 
#We create a Model
myModel=SGModel(640,480)

myModel.Grid.initializeTheGrid(10,10,"square")

myModel.Grid.initANewPovForCell("Basic")

myModel.Grid.setInitialPov("Basic")

myModel.show() 

sys.exit(monApp.exec_())
