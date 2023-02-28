import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1080,960,"An another example with agents")

theFirstGrid=myModel.createGrid(10,10,"hexagonal",Qt.gray, name="basicGrid")
myModel.setUpEntityValueAndPov("Forester",{"Forest":{"Niv1":Qt.yellow,"Niv2":Qt.red,"Niv3":Qt.green},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},[theFirstGrid],"sea","reasonable")
myModel.setInitialPov("Forester")

theFirstGrid.setForRandom({"Forest":"Niv1"},30)
theFirstGrid.setForRandom({"Forest":"Niv2"},4)

# You can create an Agent by giving a name, a shape and the associates grids
anAgentLac=myModel.newAgent("lac","circleAgent",[theFirstGrid])

# Tou can also put a name for a special pov for this same Agent.
myModel.setUpEntityValueAndPov("Forester",{"boat":{"new":Qt.blue,"old":Qt.cyan}},"lac","boat","old",[theFirstGrid])

theFirstLegend=myModel.createLegendAdmin()
myModel.show() 

sys.exit(monApp.exec_())