import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1080,960,"About agents (2)")

theFirstGrid=myModel.createGrid(10,10,"hexagonal",Qt.gray, name="basicGrid")
myModel.setUpEntityValueAndPov("Forester",{"Forest":{"Niv1":Qt.yellow,"Niv2":Qt.red,"Niv3":Qt.green},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},[theFirstGrid],"sea","reasonable")
myModel.setInitialPov("Forester")

theFirstGrid.setForRandom({"Forest":"Niv1"},30)
theFirstGrid.setForRandom({"Forest":"Niv2"},4)

anAgentLac=myModel.newAgent("lac","circleAgent",[theFirstGrid])
myModel.setUpEntityValueAndPov("Forester",{"boat":{"new":Qt.blue,"old":Qt.cyan}},"lac","boat","old",[theFirstGrid])
theFirstLegend=myModel.createLegendAdmin()

# You can add Agents directly on cell at initialisation with cell row and column:
theFirstGrid.addOnXandY("lac",5,8)
theFirstGrid.addOnXandY("lac",2,7)

myModel.show() 

sys.exit(monApp.exec_())