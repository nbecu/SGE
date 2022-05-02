import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets
  


monApp=QtWidgets.QApplication([])
#Example of a simple grid 

myModel=SGModel(640,480)

myModel.Grid.initializeTheGrid(8,8,"hexagon")

myModel.Grid.initANewPovForCell("Basic")

myModel.Grid.setInitialPov("Basic")

myModel.show() 

sys.exit(monApp.exec_())
