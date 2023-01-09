import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of rework POVS CEll


myModel=SGModel(1080,960,"grid")

theFirstGrid=myModel.createGrid(10,10,"hexagonal",Qt.gray)

theSecondGrid=myModel.createGrid("secondGrid",10,10,"square")


myModel.setUpEntityValueAndPov("Forester",{"Forest":{"Niv3":Qt.green,"Niv2":Qt.red,"Niv1":Qt.yellow},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},[theFirstGrid,theSecondGrid],"sea","reasonable")

myModel.setUpEntityValueAndPov("Fireman",{"FireRisk":{"Niv2":Qt.black,"Niv1":Qt.gray}},[theFirstGrid,theSecondGrid])

myModel.setInitialPov("Forester")

theFirstGrid.setForRandom({"Forest":"Niv3"},30)






myModel.newAgent("lac","circleAgent",[theFirstGrid,theSecondGrid])

myModel.setUpEntityValueAndPov("Forester",{"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},"lac","sea","reasonable",[theFirstGrid,theSecondGrid])
myModel.setUpEntityValueAndPov("Fireman",{"FireRisk":{"Niv2":Qt.black,"Niv1":Qt.gray}},"lac","FireRisk","Niv2",[theFirstGrid,theSecondGrid])


theFirstLegend=myModel.createLegendAdmin()




theSecondLegend=myModel.createLegendForPlayer("theTestLegend",{"basicGrid":{"Forester":{"Forest":{"Niv3":Qt.green}}}})

theSecondLegend.addToTheLegend({"basicGrid":{"Forester":{"Forest":{"Niv2":Qt.red}}}})

theSecondLegend.addAgentToTheLegend("lac")


theSecondLegend.addDeleteButton()

theFirstGrid.addOnXandY("lac",1,1)
theFirstGrid.addOnXandY("lac",2,2,"deep sea")


theFirstGrid.getCell("cell0-0").setUpCellValue({"Forest":"Niv3"})

theFirstGrid.getCell("cell0-0").setUpCellValue({"sea":"deep sea"})

theFirstGrid.getCell("cell0-0").getAgentsOfType("lac")[0].setUpAgentValue({"sea":"deep sea"})

theFirstGrid.setUpPov("addedPov",{"hopital":{"medecin":Qt.green,"interne":Qt.white}})

theSecondGrid.setUpPov("addedPov",{"hopital":{"medecin":Qt.green,"interne":Qt.white}})

theFirstGrid.setUpPov("addedPov",{"hopital":{"medecin":Qt.green,"interne":Qt.white}},"agents","lac")

theFirstGrid.setValueForCells({"hopital":"medecin"})
theSecondGrid.setValueForCells({"hopital":"medecin"})
theFirstGrid.setValueForAgents("lac",{"hopital":"interne"})
theSecondGrid.setValueForAgents("lac",{"hopital":"interne"})


theFirstGrid.setValueForModelAgents("lac",{"hopital":"medecin"})
theFirstGrid.addOnXandY("lac",4,4)

theFirstGrid.setValueAgentsOnCell("lac",{"hopital":"medecin"},"cell0-0")


theFirstGrid.addOnXandY("lac",5,5)
theFirstGrid.setForAnAgentOfCell("lac",{"hopital":"interne"},"cell4-4")



myModel.show() 

sys.exit(monApp.exec_())
