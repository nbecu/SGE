import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1100,550, windowTitle="Solutré", typeOfLayout ="grid")

Cells=myModel.newCellsOnGrid(8,8,"hexagonal",size=80,gap=10)
Cells.deleteEntity(Cells.getEntity(1,1))
Cells.deleteEntity(Cells.getEntity(2,1))
Cells.deleteEntity(Cells.getEntity(3,1))
Cells.deleteEntity(Cells.getEntity(4,1))
Cells.deleteEntity(Cells.getEntity(5,1))
Cells.deleteEntity(Cells.getEntity(8,1))
Cells.deleteEntity(Cells.getEntity(1,2))
Cells.deleteEntity(Cells.getEntity(2,2))
Cells.deleteEntity(Cells.getEntity(3,2))
Cells.deleteEntity(Cells.getEntity(8,2))
Cells.deleteEntity(Cells.getEntity(1,3))
Cells.deleteEntity(Cells.getEntity(2,3))
Cells.deleteEntity(Cells.getEntity(1,5))
Cells.deleteEntity(Cells.getEntity(1,6))
Cells.deleteEntity(Cells.getEntity(7,6))
Cells.deleteEntity(Cells.getEntity(8,6))
Cells.deleteEntity(Cells.getEntity(1,7))
Cells.deleteEntity(Cells.getEntity(2,7))
Cells.deleteEntity(Cells.getEntity(6,7))
Cells.deleteEntity(Cells.getEntity(7,7))
Cells.deleteEntity(Cells.getEntity(8,7))
Cells.deleteEntity(Cells.getEntity(1,8))
Cells.deleteEntity(Cells.getEntity(2,8))
Cells.deleteEntity(Cells.getEntity(4,8))
Cells.deleteEntity(Cells.getEntity(5,8))
Cells.deleteEntity(Cells.getEntity(6,8))
Cells.deleteEntity(Cells.getEntity(7,8))
Cells.deleteEntity(Cells.getEntity(8,8))










# Cells.newPov("Zones joueurs","zone",{"Roches":Qt.white,"Naturaliste":Qt.green,"Viticulteur":Qt.magenta,"Elu":Qt.blue})

myModel.launch()
# myModel.launch_withMQTT("Instantaneous")
sys.exit(monApp.exec_())