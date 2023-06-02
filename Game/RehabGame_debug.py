import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGSGE import *


monApp=QtWidgets.QApplication([])


#STEP1 Create the model

myModel=SGModel(1800,900, windowTitle="dev project : Rehab Game", typeOfLayout ="grid")


#STEP2 Create the model
aGrid=myModel.newGrid(7,7,"square",size=60, gap=2,name='grid1') #,posXY=[20,90]
aGrid.setCells("Resource","2")
aGrid.setCells("ProtectionLevel","Free")
aGrid.setRandomCells("Resource","3",7)
aGrid.setRandomCells("Resource","1",3)

aGrid.setRandomCells("Resource","0",8)
aGrid.setRandomCells("ProtectionLevel","Reserve",1)


myModel.newPov("Resource","Resource",{"3":Qt.darkGreen,"2":Qt.green,"1":Qt.yellow,"0":Qt.white})
myModel.newBorderPov("ProtectionLevel","ProtectionLevel",{"Reserve":Qt.magenta,"Free":Qt.black})

Workers=myModel.newAgentSpecies("Workers","triangleAgent1",uniqueColor=Qt.black)
Birds=myModel.newAgentSpecies("Birds","triangleAgent2",uniqueColor=Qt.yellow)




theFirstLegend=myModel.newLegendAdmin("Légende globale",showAgents=True)

Player1=myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.createCreateAction(Workers,20))
Player1.addGameAction(myModel.createDeleteAction(Workers,"infinite"))
Player1.addGameAction(myModel.createUpdateAction('Cell',3,{"Resource":"3"}))
Player1.addGameAction(myModel.createMoveAction(Workers,1))
Player1Legend=Player1.newLegendPlayer("Actions du Joueur 1",showAgents=True)

Player2=myModel.newPlayer("Player 2")
Player2.addGameAction(myModel.createUpdateAction("Cell",3,{"ProtectionLevel":"Reserve"}))
Player2.addGameAction(myModel.createUpdateAction("Cell","infinite",{"ProtectionLevel":"Free"}))
Player2Legend=Player2.newLegendPlayer("Actions du Joueur 2")

myModel.timeManager.newGamePhase('Phase 1',[Player1,Player2])
myModel.timeManager.newGamePhase('Phase 2',[Player1,Player2])
GameRounds=myModel.newTimeLabel("My Game Time",Qt.white,Qt.black,Qt.red)
myModel.currentPlayer='Player 1'



TextBox=myModel.newTextBox(title='Début du jeu',textToWrite="Bonjour et bienvenue dans RehabGame !")

TextBox.addText("J'espère que vous allez bien!!!",toTheLine=True)
#TextBox.setTextColor()

DashBoard=myModel.newDashBoard(borderColor=Qt.black,backgroundColor=Qt.transparent,textColor=Qt.red)
i1=DashBoard.addIndicator("sumAtt",'cell','Resource')
i2=DashBoard.addIndicator("avgAtt",'cell','Resource')
DashBoard.showIndicators()


userSelector=myModel.newUserSelector()

endGameRule=myModel.newEndGameRule(numberRequired=2)
endGameRule.addEndGameCondition_onIndicator(i1,"equal",90)
targetCell = aGrid.getCell(1,5)
endGameRule.addEndGameCondition_onEntity(targetCell,'Resource',"greater",2)
endGameRule.showEndGameConditions()




myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())