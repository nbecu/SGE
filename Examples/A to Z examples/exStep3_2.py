import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1700,800, windowTitle="A simulation/game with agents", typeOfLayout ="grid")

aGrid=myModel.newGrid(6,6,"square",gap=2)
aGrid.setCells("landUse","grass")
aGrid.setCells_withColumn("landUse","forest",1)
aGrid.setCells_withColumn("landUse","forest",2)
aGrid.setRandomCells("landUse","shrub",10)

myModel.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
myModel.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

# You can put numerical values or string values.
# Here is an example with numerical values
Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1",{"health":{"100","90","80","70","60","50","40","30","20","10","0"},"hunger":{"100","90","80","70","60","50","40","30","20","10","0"}})

Sheeps.newPov("Sheeps -> Health","health",{"100":Qt.blue,"90":Qt.blue,"80":Qt.blue,"70":Qt.blue,"60":Qt.blue,"50":Qt.blue,"40":Qt.red,"30":Qt.red,"20":Qt.red,"10":Qt.red,"0":Qt.red})
Sheeps.newPov("Sheeps -> Hunger","hunger",{"100":Qt.green,"90":Qt.green,"80":Qt.green,"70":Qt.green,"60":Qt.green,"50":Qt.green,"40":Qt.yellow,"30":Qt.yellow,"20":Qt.yellow,"10":Qt.yellow,"0":Qt.yellow})

m1=myModel.newAgentAtCoords(aGrid,Sheeps,1,1,aDictofAttributs={"health":"70","hunger":"20"})
m2=myModel.newAgentAtCoords(aGrid,Sheeps,None,None)

m2.setValueAgent('health','90')
m2.setValueAgent('hunger','90')



Legend=myModel.newLegendAdmin(showAgentsWithNoAtt=True)
myModel.launch() 

sys.exit(monApp.exec_())