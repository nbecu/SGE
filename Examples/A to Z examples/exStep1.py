import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

# This is your model. A Model is an interactive window where you will be able to
# add items later. You can choose its size, name and type of organization.
myModel = SGModel(550, 550, windowTitle="Hello World")

# This launchs your model and it will always be the last twwo lines of the code.
myModel.launch()
sys.exit(monApp.exec_())
