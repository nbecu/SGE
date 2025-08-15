import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from mainClasses.SGTestGetData import SGTestGetData
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="Production and Consumption")
myModel.displayTimeInWindowTitle()

score=myModel.newSimVariable('Score',0)


## Define Production Units
ProductionUnits=myModel.newCellsOnGrid(10,10,"square",size=45, gap=2, name="Production Unit")
ProductionUnits.setEntities("production system",(lambda: random.choice(['constant','not constant'])))
ProductionUnits.setEntities("energy",lambda: random.randint(2,4)*10)

    # Define pov 
aDict = generate_color_gradient(
    QColor.fromRgb(239, 255, 232),QColor.fromRgb(1,50,32),
    mapping={"values": list(range(0, 100, 10)), "value_min": 0, "value_max": 100},
    as_dict=True
)
aDict = generate_color_gradient(
    QColor.fromRgb(239, 255, 232),QColor.fromRgb(1,50,32),
    mapping={"values": list(range(0, 100, 10)), "value_min": 0, "value_max": 100},
    as_dict=True
)
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
aDict = generate_color_gradient(
    Qt.red, Qt.blue,
    mapping={"values": list(range(0, 110, 10)), "value_min": 0, "value_max": 100},
    as_dict=True
)
Consumers.newPov("energy","energy",aDict)

    # Define methods
def move(aConsumer):
    dest = sorted(list(aConsumer.getNeighborCells()),  key=lambda x:x.value('energy'))[-1]
    return aConsumer.moveTo(dest)

def moveAndConsume(aConsumer):
    consume(move(aConsumer))

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
    aConsumer.decValue('energy',20,0)
    if aConsumer.value('energy') <=20:
        print('del: '+str(aConsumer.id))
        Consumers.deleteEntity(aConsumer)
        score.decValue(1)

## Define Regulator
Regulators=myModel.newAgentSpecies("Regulator","circleAgent")
Regulators.setValue("satisf constant",0)
Regulators.setValue("satisf not constant",0)
Regulators.newAgentsAtRandom(5,ProductionUnits)


    # Define methods
def evaluate(aRegulator):
    aCell = aRegulator.cell
    if aCell.value('production system') == 'boosted' and aCell.value('energy') == 100:
        if aRegulator.entDef.value("satisf constant") == aRegulator.entDef.value("satisf not constant"):
            if random.random() < 0.5:
                newS = 'constant'
            else :
                newS = 'not constant'
        else :
            ratio = aRegulator.entDef.value("satisf constant") / (aRegulator.entDef.value("satisf constant") + aRegulator.entDef.value("satisf not constant"))
            if random.random < ratio :
                newS = 'constant'
            else :
                newS = 'not constant'
            aCell.setValue('production system',newS)

    if aCell.value('production system') == 'constant' and aCell.value('energy') == 100:
        aRegulator.classDef.incValue("satisf constant",1)
    if aCell.value('production system') == 'not constant' and aCell.value('energy') == 100:
        aRegulator.classDef.incValue("satisf not constant",1)
    if aCell.value('production system') == 'constant' and aCell.value('energy') <= 10:
        aRegulator.classDef.decValue("satisf constant",1)
        aRegulator.cell.setValue('production system','boosted')
    if aCell.value('production system') == 'not constant' and aCell.value('energy') <= 10:
        aRegulator.classDef.decValue("satisf not constant",1)
        aRegulator.cell.setValue('production system','boosted')


def evaluateCell(aCell):
    if (aCell.value('production system') == 'boosted') and (aCell.value('energy') >= 50):
        if Regulators.value("satisf constant") == Regulators.value("satisf not constant"):
            if random.random() < 0.5:
                newS = 'constant'
            else :
                newS = 'not constant'
        else :
            ratio = (Regulators.value("satisf constant")+100) / (Regulators.value("satisf constant") +200+ Regulators.value("satisf not constant"))
            if random.random() < ratio :
                newS = 'constant'
            else :
                newS = 'not constant'
            aCell.setValue('production system',newS)


## Model actions 

modelAction1=myModel.newModelAction_onCells(lambda aPU: produce(aPU))
# modelAction2=myModel.newModelAction(lambda : Consumers.moveRandomly())
# modelAction2=myModel.newModelAction_onAgents("Consumer",(lambda aConsumer: move(aConsumer)))
# modelAction3=myModel.newModelAction_onAgents("Consumer",(lambda aConsumer: consume(aConsumer)))
modelAction2=myModel.newModelAction_onAgents("Consumer",(lambda aConsumer: moveAndConsume(aConsumer)))
modelAction4=myModel.newModelAction_onAgents("Consumer",(lambda aConsumer: reproAndDie(aConsumer)))
modelAction5=myModel.newModelAction(lambda : Regulators.moveRandomly())
modelAction6=myModel.newModelAction_onAgents("Regulator",(lambda aRegulator: evaluate(aRegulator)))

modelAction7=myModel.newModelAction_onCells((lambda aCell: evaluateCell(aCell)))


myModel.timeManager.newModelPhase([modelAction1,modelAction2,modelAction4,modelAction5,modelAction6,modelAction7])


# def rdCustom():
#     if random.random() < 0.2 : score.incValue(2)
# myModel.timeManager.newModelPhase([lambda : rdCustom()])

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