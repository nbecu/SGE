import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="CarboneBleu")

Cell=myModel.newCellsOnGrid(15,18,"square",size=45, gap=2)


# ZONE EQUIPE A
Cell.setEntities("zones","Joueur A")
# ZONE EQUIPE C
for i in range(12,19,1):
    Cell.setEntities_withRow("zones", "Joueur C", i)
# ZONE EQUIPE B
zoneBCells=[cell for cell in Cell.entities if cell.xPos >7 and cell.yPos <12]
for aCell in zoneBCells:
    aCell.setValue("zones","Joueur B")

def defAménité(coords):
    if len(coords)>5:
        random_cells=random.sample(coords,2)
        for element in random_cells:
            aCell=Cell.getCell(element[0],element[1])
            neighbors=aCell.getNeighborCells(rule="neumann")
            for aNeighborCell in neighbors:
                if aNeighborCell.value("type")!="ZH":
                    aNeighborCell.setValue('type',"Aménité")
                    aNeighborCell.setValue('typeZH',"Aménité")
                    break
    else:
        random_cells=random.choice(coords)
        aCell=Cell.getCell(random_cells[0],random_cells[1])
        neighbors=aCell.getNeighborCells()
        for aNeighborCell in neighbors:
            if aNeighborCell.value("type")!="ZH":
                aNeighborCell.setValue('type',"Aménité")
                aNeighborCell.setValue('typeZH',"Aménité")
                break
    
    
# ZONES HUMIDES
Cell.setEntities("type","neutre")
Cell.setEntities('typeZH','neutre')

# Zone H 1
coords=[[3,2],[2,3],[3,3],[4,3],[3,4]]
for element in coords:
    Cell.setCell(element[0],element[1],"type","ZH")
    Cell.setCell(element[0],element[1],"typeZH","alpha")
defAménité(coords)

# Zone H 2
coords=[[12,6],[10,7],[11,7],[12,7],[13,7],[12,8],[13,8]]
for element in coords:
    Cell.setCell(element[0],element[1],"type","ZH")
    Cell.setCell(element[0],element[1],"typeZH","alpha")
defAménité(coords)

# Zone H 3
coords=[[6,10],[7,11],[8,11],[7,12],[8,12],[9,12],[8,13]]
for element in coords:
    Cell.setCell(element[0],element[1],"type","ZH")
    Cell.setCell(element[0],element[1],"typeZH","beta")
defAménité(coords)


# Zone H 4
coords=[[12,16],[13,16],[9,17],[10,17],[11,17],[12,17],[10,18],[11,18]]
for element in coords:
    Cell.setCell(element[0],element[1],"type","ZH")
    Cell.setCell(element[0],element[1],"typeZH","gamma")
defAménité(coords)


Cell.newPov("Type de terrain","type",{"ZH":Qt.green,"Aménité":Qt.magenta,"neutre":Qt.gray})
Cell.newPov("Type de zone humide","typeZH",{"alpha":Qt.darkGreen,"beta":Qt.darkBlue,"gamma":Qt.darkCyan,"neutre":Qt.gray,"Aménité":Qt.magenta})
Cell.newBorderPovColorAndWidth("Zones Joueurs","zones", {"Joueur A": [Qt.yellow,1], "Joueur B": [Qt.blue,1], "Joueur C": [Qt.red,1]})

Occupation=myModel.newAgentSpecies("Occupation du Joueur 1","triangleAgent2")
Occupation2=myModel.newAgentSpecies("Occupation du Joueur 2","arrowAgent1",defaultColor=Qt.yellow)
Occupation3=myModel.newAgentSpecies("Occupation du Joueur 3","ellipseAgent2",defaultColor=Qt.red)

theFirstLegend=myModel.newLegend()

Player1=myModel.newPlayer("Joueur A")
# Player1.addGameAction(myModel.newUpdateAction('Cell',{"landUse":"grass"},3))

Player1Legend=Player1.newControlPanel("Actions du Joueur A",showAgentsWithNoAtt=True)

userSelector=myModel.newUserSelector()


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