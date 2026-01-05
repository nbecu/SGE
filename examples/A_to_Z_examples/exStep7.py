import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="Add a TextBox")

Cell=myModel.newCellsOnGrid(10,10,"square",size=45, gap=2)
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

Sheeps=myModel.newAgentType("Sheeps","triangleAgent1")
Sheeps.setDefaultValues({"health":(lambda: random.choice(["good","bad"])),"hunger":(lambda: random.choice(["good","bad"]))})

Sheeps.newPov("Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})
m1=Sheeps.newAgentAtCoords(Cell,1,1,{"health":"good","hunger":"bad"})
m2=Sheeps.newAgentAtCoords(Cell,5,1)

theFirstLegend=myModel.newLegend()


Player1=myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.newModifyAction(Cell,{"landUse":"grass"},3))

Player1ControlPanel=Player1.newControlPanel("Actions du Joueur 1")

userSelector=myModel.newUserSelector()


myModel.newPlayPhase('Phase 1', [Player1])
myModel.newModelPhase([lambda: Cell.setRandomEntities("landUse","forest"),lambda: Cell.setRandomEntities("landUse","shrub",3)])


aModelAction2=myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2,condition=(lambda x: x.value("landUse") != "shrub" and x.value("landUse") != "forest"  )))

aModelAction4 =myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2))
aModelAction4.addCondition(lambda: Cell.nb_withValue("landUse","forest")> 10) 

myModel.newModelPhase(aModelAction2)

GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.black)

DashBoard = myModel.newDashBoard('The indicators',borderColor=Qt.black, textColor=Qt.black,layout='vertical')

score1= myModel.newSimVariable("Global Score",0)
i1 = DashBoard.addIndicatorOnSimVariable(score1)

aModelAction4.addFeedback(lambda: score1.incValue(3))
myModel.newModelPhase(aModelAction4)

DashBoard.addIndicatorOnEntity(Cell.getCell(4,6),'landUse')
DashBoard.addIndicatorOnEntity(Cell.getCell(4,6),'landUse',logicOp='equal',value='forest')

endGameRule = myModel.newEndGameRule(numberRequired=1)
endGameRule.addEndGameCondition_onIndicator(
    i1, "equal", 90, name="Score equal to 90")
endGameRule.displayEndGameConditions()

# You can add TextBoxes to your game
# You can cuztomize the text, the title color and font by using the proper functions.
TextBox = myModel.newLabel(
    text="Your game is starting...\nWelcome !",alignement='Center')

myModel.setCurrentPlayer("Player1")
myModel.launch()


sys.exit(monApp.exec_())