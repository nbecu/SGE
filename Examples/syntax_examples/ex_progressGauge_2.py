import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor
from collections import defaultdict
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(600,600, windowTitle="examplify progressGauge feature")

Cell = myModel.newCellsOnGrid(5, 4, "square", size=30,neighborhood='neumann')
Cell.setEntities("cover", "empty")
Cell.setRandomEntities('cover','building',6)
Cell.setEntities_withColumn('cover','road',randint(1,Cell.grid.columns))
Cell.setEntities_withRow('cover','road',randint(1,Cell.grid.rows))

Cell.newPov("base","cover",{"empty":Qt.white,"building":Qt.blue,"road":Qt.lightGray})
Cars=myModel.newAgentSpecies("car","circleAgent",defaultSize=10, locationInEntity="center")
Cars.newAgentsAtRandom(2,condition= lambda cell : cell.isValue('cover','road'))

p1 = myModel.timeManager.newModelPhase()
carsMove = Cars.newModelAction(actions = lambda car : processMove(car))
p1.addAction(carsMove)

def processMove(car):
    aDestinationCell = car.moveAgent(condition= lambda cell : cell.isValue('cover','road'))
    if aDestinationCell.nbAgents() > 1 : 
        simVarCollision.incValue() 

simVarQoL = myModel.newSimVariable("Qualité de vie", 0)
simVarEnv = myModel.newSimVariable("Environnement", 0)
simVarAttract  = myModel.newSimVariable("Attractivité", 0)
simVarCollision = myModel.newSimVariable("Collision", 0)


jaugeQoL = myModel.newProgressGauge(simVarQoL,-2,10,"Qualité de vie", orientation='vertical',unit = ' Pts',bar_width=40,colorRanges=[(-10,0,"red"),(0,10,"blue")])

jaugeEnv = myModel.newProgressGauge(simVarEnv, -2,  10, "Environnement", bar_width=70,title_position='below', unit=' biodiversity points')
jaugeEnv.setThresholdValue(6, lambda: print("Up Env"), lambda: print("Down Env"))

jaugeAtt = myModel.newProgressGauge(simVarAttract, -2,  10, "Attractivité",bar_length=300,bar_width=20,display_value_on_top=False)
jaugeAtt.setThresholdValue(5, lambda: print("Up Att"), lambda: print("Down Att"))

jaugeCollision = myModel.newProgressGauge(simVarCollision, 0, 10, "Collision", orientation='vertical',bar_width=40,bar_length=60,colorRanges=[(0,1,"green"),(2,3,"blue"),(4,5,"orange"),(6,20,"red")])



myModel.newButton((lambda: changeAll(1)),'Add 1',(70,300))

myModel.newButton((lambda: changeAll(-1)),'Remove 1',(70,320))

myModel.newButton((lambda: addGivenValue()),'add "x"',(70,350))


def addGivenValue():
    userDefinedValue = simpledialog.askinteger("Input", "Enter a value between -10 and 10:",  
                                             minvalue=-10, maxvalue=10)
    changeAll(userDefinedValue)


def changeAll(delta):
    simVarQoL.incValue(delta)
    simVarEnv.incValue(delta)
    simVarAttract.incValue(delta)

# Launch


myModel.launch()
sys.exit(monApp.exec_())
