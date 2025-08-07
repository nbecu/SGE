import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1700,800, windowTitle="A simulation/game with agents", typeOfLayout ="grid")

Cell=myModel.newCellsOnGrid(6,6,"square",gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

# You can put numerical values or string values.
# Here is an example with numerical values
Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1")
Sheeps.setDefaultValues({"health":(lambda: random.randint(0,10)*10),"hunger":(lambda: random.randint(0,10)*10)})

def interpolate_color(value_min, value_max, color_min, color_max, a_value):
    # Ensure that the intermediate value lies between the min and max values
    a_value = max(min(a_value, value_max), value_min)
    # convert color_min and color_max to rgb format
    color_min_rgb = QColor(color_min).getRgb()
    color_max_rgb = QColor(color_max).getRgb()
    # Interpolate RGB components
    proportion = (a_value - value_min) / (value_max - value_min)
    aList=[]
    for i in range(0,3):
        aList.append(int(color_min_rgb[i] + proportion * (color_max_rgb[i] - color_min_rgb[i])))
    return QColor(*aList)


aDict={}
for aVal in list(range(0,110,10)):
    aDict[aVal]=interpolate_color(0,100,Qt.red,Qt.blue,aVal) 
Sheeps.newPov("Health","health",aDict)

aDict={}
for aVal in list(range(0,110,10)):
    aDict[aVal]=interpolate_color(0,100,Qt.yellow,QColor.fromRgb(1,80,32),aVal) 
Sheeps.newPov("Hunger","hunger",aDict)

m1=Sheeps.newAgentAtCoords(Cell,1,1,{"health":70,"hunger":20})
Sheeps.newAgentsAtRandom(10,Cell)

Sheeps.getEntity(2).setValue('health',90)
Sheeps.getEntity(2).setValue('hunger',90)



Legend=myModel.newLegend(showAgentsWithNoAtt=True)
myModel.launch() 

sys.exit(monApp.exec_())
