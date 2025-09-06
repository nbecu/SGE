import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(550,450, windowTitle="A simulation/game with agents", typeOfLayout ="grid")

Cell=myModel.newCellsOnGrid(6,6,"square",size=60,gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("base","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})


# You can put numerical values or string values.
# Here is an example with numerical values
Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent2",defaultSize=25)
Sheeps.setDefaultValues_randomNumeric({"health": range(0, 100, 10), "hunger": range(0, 100, 10)})

# define color gradients for both attributes
health_colors = {
    100: Qt.blue,                    # (0, 0, 255)
    90: QColor(32, 0, 223),         # blue-violet
    80: QColor(64, 0, 191),         # lighter blue-violet
    70: QColor(96, 0, 159),         # dark violet
    60: QColor(128, 0, 128),        # violet
    50: QColor(159, 0, 96),         # dark magenta
    40: QColor(191, 0, 64),         # magenta
    30: QColor(223, 0, 32),         # red-magenta
    20: QColor(255, 0, 0),          # bright red
    10: QColor(192, 0, 0),          # dark red
    0: QColor(128, 0, 0)            # very dark red
}
hunger_colors = {
    100: Qt.green,                   # (0, 255, 0)
    90: QColor(64, 255, 0),          # green tending to yellow
    80: QColor(128, 255, 0),         # green-yellow
    70: QColor(192, 255, 0),         # lighter green-yellow
    60: QColor(224, 224, 0),         # yellow-green
    50: QColor(255, 255, 0),         # pure yellow
    40: QColor(255, 223, 0),         # golden yellow
    30: QColor(255, 191, 0),         # orange-yellow
    20: QColor(255, 159, 0),         # light orange
    10: QColor(255, 128, 0),         # orange
    0: QColor(255, 255, 128)         # very pale yellow (almost white, to signal extreme)
}
Sheeps.newPov("Health","health",health_colors)
Sheeps.newPov("Hunger","hunger",hunger_colors)

m1=Sheeps.newAgentAtCoords(Cell,1,1,{"health":70,"hunger":20})
m2=Sheeps.newAgentAtCoords(Cell,None,None)
Sheeps.newAgentsAtRandom(10,Cell)




Legend=myModel.newLegend(alwaysDisplayDefaultAgentSymbology=True)
myModel.launch() 

sys.exit(monApp.exec_())
