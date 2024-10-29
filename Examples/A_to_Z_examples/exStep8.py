import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from mainClasses.SGTestGetData import SGTestGetData
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="Add a TextBox")

Cell=myModel.newCellsOnGrid(10,10,"square",size=45, gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("pov","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})

Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1")
#Sheeps.setDefaultValues({"health":(lambda: random.randint(0,10)*10)})
Sheeps.setDefaultValues({"health": (lambda: myModel.getDefaultAgentRandomValue(0, 10)*10)})

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
    aDict[aVal]=interpolate_color(0,100,Qt.red,Qt.blue,aVal) 
Sheeps.newPov("Sheeps -> Health","health",aDict)


m1=Sheeps.newAgentAtCoords(Cell,1,1)
m2=Sheeps.newAgentAtCoords(Cell,5,1)

theFirstLegend=myModel.newLegend()


Player1=myModel.newPlayer("Player 1",{"Percentage of grass":0})
Player1.addGameAction(myModel.newModifyAction('Cell',{"landUse":"grass"},3))
Player2=myModel.newPlayer("Player 2",{"Sheeps in good health":0})
Player2.addGameAction(myModel.newCreateAction(Sheeps,{"health":"good"},4))
Player1Legend=Player1.newControlPanel("Actions du Joueur 1")
Player2Legend=Player2.newControlPanel("Actions du Joueur 2")

userSelector=myModel.newUserSelector()


myModel.timeManager.newGamePhase('Phase 1', [Player1,Player2])
myModel.timeManager.newModelPhase([lambda: Cell.setRandomEntities("landUse","forest"),lambda: Cell.setRandomEntities("landUse","shrub",3)])

aModelAction2=myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2,condition=(lambda x: x.value("landUse") != "shrub" and x.value("landUse") != "forest"  )))
myModel.timeManager.newModelPhase(aModelAction2)

myModel.timeManager.newModelPhase(myModel.newModelAction(lambda: Sheeps.moveRandomly()))
myModel.timeManager.newModelPhase(myModel.newModelAction_onAgents('Sheeps',lambda aSheep: eat(aSheep)))

def eat(aSheep):
    if aSheep.cell.value('landUse') == "forest":
        aSheep.incValue('health',10)
        aSheep.cell.setValue('landUse',"grass")
    elif aSheep.cell.value('landUse') == "grass":
        aSheep.cell.setValue('landUse', "shrub")
        return
    elif aSheep.cell.value('landUse') == "shrub":
        aSheep.decValue('health',10)
    else:
        raise ValueError


GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.black)

DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.black)

score1= myModel.newSimVariable("Global Score:",0)
i1 = DashBoard.addIndicatorOnSimVariable(score1)

aModelAction4 =myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2))
aModelAction4.addCondition(lambda: Cell.nb_withValue("landUse","forest")> 10) 
aModelAction4.addFeedback(lambda: score1.incValue(3))
phase6 = myModel.timeManager.newModelPhase(aModelAction4)
phase6.addAction(myModel.newModelAction(lambda: Player1.setValue("Percentage of grass",Cell.nb_withValue("landUse","grass")/Cell.nbOfEntities())))
phase6.addAction(myModel.newModelAction(lambda: Player2.setValue("Sheeps in good health",Sheeps.nb_withValue("health","good"))))

# dataTest = SGTestGetData(myModel)
# myModel.timeManager.newModelPhase(lambda:dataTest.getAllDataSinceInitialization())

DashBoard.addIndicatorOnEntity(Cell.getCell(4,6),'landUse')
DashBoard.addIndicatorOnEntity(Cell.getCell(4,6),'landUse',logicOp='equal',value='forest')

DashBoard.showIndicators()

endGameRule = myModel.newEndGameRule(numberRequired=1)
endGameRule.addEndGameCondition_onIndicator(
    i1, "equal", 90, name="Score equal to 90")
endGameRule.showEndGameConditions()


myModel.setCurrentPlayer("Player1")
myModel.launch()


sys.exit(monApp.exec_())