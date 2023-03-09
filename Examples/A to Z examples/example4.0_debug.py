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


Moutons=myModel.newAgentSpecies("Moutons","circleAgent",{"health":{"good","bad"},"age":{"baby","adult","elder"}})
Moutons.setUpPov("Veto","health",{'good':Qt.blue,'bad':Qt.red})
Moutons.setUpPov("Child","health",{'good':Qt.blue,'bad':Qt.blue})

m1=myModel.newAgent(aGrid,Moutons,3,7)
m2=myModel.newAgent(aGrid,Moutons,6,3)
m2.updateAgentValue('health','bad')
m1.updateAgentValue('health','good')
print(myModel.AgentSpecies['Moutons'])






#myModel.updateAgent(Mouton,'M02','health','bad')

#theFirstLegend=myModel.createLegendAdmin()












myModel.iAm("Admin")

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
