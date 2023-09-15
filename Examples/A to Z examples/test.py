import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *


monApp = QtWidgets.QApplication([])


# STEP1 Model

myModel = SGModel(
    1800, 900, x=5, windowTitle="test Agents", typeOfLayout="grid")


aAgent=myModel.newAgentTest("1","triangleAgent1")

myModel.launch()


sys.exit(monApp.exec_())