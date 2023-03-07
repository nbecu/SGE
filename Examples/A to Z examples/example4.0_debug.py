import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="A simulation/game with one agent")

aGrid=myModel.createGrid(10,10,"square",size=60, gap=2)
aGrid.setValueForCells({"landUse":"grass"})
aGrid.setForX({"landUse":"forest"},1)
aGrid.setForX({"landUse":"forest"},2)
aGrid.setForRandom({"landUse":"shrub"},10)

myModel.setUpPov("Farmer",{"landUse":{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen}})
myModel.setUpPov("Visitor",{"landUse":{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen}})


Mouton=myModel.newAgentSpecies("Mouton","circleAgent",{"health":{"good","bad"},"age":{"baby","adult","elder"}})

myModel.newAgent(aGrid,Mouton,None,None)
myModel.newAgent(aGrid,Mouton,None,None)




#myModel.updateAgent(Mouton,'M02','health','bad')

#theFirstLegend=myModel.createLegendAdmin()












myModel.iAm("Admin")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
