import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
import random

monApp = QtWidgets.QApplication([])


myModel = SGModel(550, 250)



myModel.newLabel('This is a text in a label',(70,100))



myModel.launch()
sys.exit(monApp.exec_())

