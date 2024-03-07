import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="CarboneBleu")

Cell=myModel.newCellsOnGrid(15,18,"square",size=45, gap=2)
Cell.setEntities("type","neutre")
Cell.setEntities("zones","A")
Cell.setEntities_withRow("zones", "C", 12)
Cell.setEntities_withRow("zones", "C", 13)
Cell.setEntities_withRow("zones", "C", 14)
Cell.setEntities_withRow("zones", "C", 15)
Cell.setEntities_withRow("zones", "C", 16)
Cell.setEntities_withRow("zones", "C", 18)
Cell.setEntities_withRow("zones", "C", 17)
zoneBCells=[cell for cell in Cell.entities if cell.xPos >7 and cell.yPos <12]
for aCell in zoneBCells:
    aCell.setValue("zones","B")

Cell.newPov("Type de terrain","type",{"ZH":Qt.green,"Aménité":Qt.magenta,"neutre":Qt.darkGray})
Cell.newBorderPovColorAndWidth("Zones Joueurs","zones", {"A": [Qt.yellow,1], "B": [Qt.blue,1], "C": [Qt.red,1]})

Occupation=myModel.newAgentSpecies("Occupation","triangleAgent1")

theFirstLegend=myModel.newLegend()

# Player1=myModel.newPlayer("Player 1")
# Player1.addGameAction(myModel.newUpdateAction('Cell',{"landUse":"grass"},3))

# Player1Legend=Player1.newControlPanel("Actions du Joueur 1",showAgentsWithNoAtt=True)

# userSelector=myModel.newUserSelector()


# myModel.timeManager.newGamePhase('Phase 1', [Player1])
# myModel.timeManager.newModelPhase([lambda: Cell.setRandomEntities("landUse","forest"),lambda: Cell.setRandomEntities("landUse","shrub",3)])


# aModelAction2=myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2,condition=(lambda x: x.value("landUse") != "shrub" and x.value("landUse") != "forest"  )))

# aModelAction4 =myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","forest",2))
# aModelAction4.addCondition(lambda: Cell.nb_withValue("landUse","forest")> 10) 

# myModel.timeManager.newModelPhase(aModelAction2)

# GameRounds = myModel.newTimeLabel("My Game Time", Qt.white, Qt.black, Qt.black)

# DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.black)

# score1= myModel.newSimVariable("Global Score:",0)
# i1 = DashBoard.addIndicatorOnSimVariable(score1)

# aModelAction4.addFeedback(lambda: score1.incValue(3))
# myModel.timeManager.newModelPhase(aModelAction4)

# DashBoard.addIndicatorOnEntity(Cell.getCell(4,6),'landUse')
# DashBoard.addIndicatorOnEntity(Cell.getCell(4,6),'landUse',logicOp='equal',value='forest')

# endGameRule = myModel.newEndGameRule(numberRequired=1)
# endGameRule.addEndGameCondition_onIndicator(
#     i1, "equal", 90, name="Score equal to 90")
# endGameRule.showEndGameConditions()

# # You can add TextBoxes to your game
# # You can cuztomize the text, the title color and font by using the proper functions.
# TextBox = myModel.newTextBox(
#     title='Your game is starting...', textToWrite="Welcome !")

# myModel.setCurrentPlayer("Player1")
myModel.launch()


sys.exit(monApp.exec_())