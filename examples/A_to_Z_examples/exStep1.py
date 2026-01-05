# This set the directory path and import the SGE library.
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# This launches the app to display your simulation/game
monApp = QtWidgets.QApplication([])

# This is your model.
# You need to set size of the window of the model
# You can specify the model name, the typeOfLayout name and the windowTitle
myModel = SGModel(550, 550)

# This launchs your model and it will ALWAYS be the last two lines of the code.
myModel.launch()
sys.exit(monApp.exec_())
