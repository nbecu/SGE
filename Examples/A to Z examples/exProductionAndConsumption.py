import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from mainClasses.SGTestGetData import SGTestGetData
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="Production and Consumption")

score=myModel.newSimVariable('Score',0)


## Define Production Units
ProductionUnits=myModel.newCellsOnGrid(10,10,"square",size=45, gap=2, name="Production Unit")
ProductionUnits.setEntities("production system",(lambda: random.choice(['constant','not constant'])))
ProductionUnits.setEntities("energy",lambda: random.randint(2,4)*10)

    # Define pov 
def interpolate_color(value_min, value_max, color_min, color_max, a_value):
    # Assurez-vous que la valeur intermédiaire se trouve entre les valeurs min et max
    a_value = max(min(a_value, value_max), value_min)
    # convertir les color_min et color_max en  un format rgb 
    color_min_rgb = QColor(color_min).getRgb()
    color_max_rgb = QColor(color_max).getRgb()
    # Interpoler les composantes RGB
    proportion = (a_value - value_min) / (value_max - value_min)
    aList=[]
    for i in range(0,3):
        aList.append(int(color_min_rgb[i] + proportion * (color_max_rgb[i] - color_min_rgb[i])))
    return QColor(*aList)
aDict={}
for aVal in list(range(0,110,10)):
    aDict[aVal]=interpolate_color(0,100,QColor.fromRgb(239, 255, 232),QColor.fromRgb(1,50,32),aVal) 
ProductionUnits.newPov("energy","energy",aDict)

ProductionUnits.newPov("prod system","production system",{"constant":Qt.green,"not constant":Qt.blue,"boosted":QColor.fromRgb(255,127,0)})

    # Define methods
def produce(aPU):
    if aPU.value("production system") ==  'constant':
        aPU.incValue("energy",10,100)
    if aPU.value("production system") ==  'not constant':
        aPU.incValue("energy",(lambda: random.randint(-1,2)*10),100)
    if aPU.value("production system") ==  'boosted':
        aPU.incValue("energy",20,100)

    if aPU.value('energy') == 100:
        score.incValue(1) 

## Define Consumers
Consumers=myModel.newAgentSpecies("Consumer","triangleAgent1")
Consumers.setDefaultValues({"energy":50})
Consumers.newAgentsAtRandom(20,ProductionUnits,{"strategy":(lambda: random.choice(['restrained','unrestrained']))})

    #define pov
aDict={}
for aVal in list(range(0,110,10)):
    aDict[aVal]=interpolate_color(0,100,Qt.red,Qt.blue,aVal) 
Consumers.newPov("energy","energy",aDict)

    # Define methods

def consume(aConsumer):
    if aConsumer.value('strategy') == 'unrestrained':
        consumptionPercentage  = 0.8
    if aConsumer.value('strategy') == 'restrained':
        consumptionPercentage  = 0.3

    qtConsume = (round((aConsumer.cell.value('energy') * consumptionPercentage)/10))*10
    aConsumer.incValue('energy',qtConsume,100)
    aConsumer.cell.decValue('energy',qtConsume,0)
    if aConsumer.cell.value('energy') < 10:
        score.decValue(1)




def reproAndDie(aConsumer):
    if aConsumer.value('energy') == 100:
        Consumers.newAgentOnCell(aConsumer.cell,{"strategy":aConsumer.value('strategy')})
        aConsumer.setValue('energy',50)
        score.incValue(1)
        return
    aConsumer.decValue('energy',10,0)
    if aConsumer.value('energy') <=40:
        Consumers.deleteEntity(aConsumer)
        score.decValue(1)



## Model actions 

modelAction1=myModel.newModelAction_onCells(lambda aPU: produce(aPU))
modelAction2=myModel.newModelAction(lambda : Consumers.moveRandomly())
modelAction3=myModel.newModelAction_onAgents("Consumer",(lambda aConsumer: consume(aConsumer)))
modelAction4=myModel.newModelAction_onAgents("Consumer",(lambda aConsumer: reproAndDie(aConsumer)))

myModel.timeManager.newModelPhase([modelAction1,modelAction2,modelAction3,modelAction4])


## Define other interface widgets
myModel.newLegend()
myModel.newTimeLabel("Time", Qt.white, Qt.black, Qt.black)
DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.black)
DashBoard.addIndicatorOnSimVariable(score)
DashBoard.showIndicators()




## open the simulation

# dataTest = SGTestGetData(myModel)
# myModel.timeManager.newModelPhase(lambda:dataTest.getAllDataSinceInitialization())
myModel.launch()
sys.exit(monApp.exec_())