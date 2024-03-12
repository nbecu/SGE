import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="CarboneBleu")

"""NOMENCLATURE
Cells :
- txFlux : taux du flux sédimentaire / flux de carbone
- qtSed : quantité de sédiments dans une cellule
- txSeqC : taux de séquestration du carbone
- qtSeqC : quantité de carbone séquestré
=> calcul pour une ZH complète = somme des paramètres de ses cellules
- nbPlaces : nombre de places d'une aménité

- typeZH : neutre pour les cases nonZH puis 3 types de ZH : alpha / beta / gamma (marais, slikke...)
- Mode de Gestion : mode1 / mode2 / mode3

Joueurs:
- A / B / C
- Update actions sur le mode de gestion
- Create action sur leur agent d'Occoupation (Occoupation/Occoupation2/Occoupation3)
- Delete action sur leur agent d'Occoupation
"""

Cell=myModel.newCellsOnGrid(15,18,"square",size=45, gap=0)
Cell.setDefaultValues({'txFlux':0,'qtSed':0,"txSeqC":0,'qtSeqC':0,"nbPlaces":0})

ModeGestion=myModel.newAgentSpecies("Mode de Gestion","circleAgent",{"Mode de Gestion":{"mode1","mode2","mode3"}},defaultSize=8,locationInEntity="topLeft")
ModeGestion.newPov("Mode de gestion de la ZH","Mode de Gestion",{'mode1':Qt.blue,'mode2':Qt.white,'mode3':Qt.green})
ModeGestion.setAttributesConcernedByUpdateMenu("Mode de Gestion","Mode de Gestion - Modifier")

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
    """Cette fonction place automatiquement les aménités autour des ZH."""
    if len(coords)>5:
        random_cells=random.sample(coords,2)
        for element in random_cells:
            aCell=Cell.getCell(element[0],element[1])
            neighbors=aCell.getNeighborCells(rule="neumann")
            for aNeighborCell in neighbors:
                if aNeighborCell.value("typeZH")=="neutre":
                    aNeighborCell.setValue('typeZH',"Aménité")
                    break
    else:
        random_cells=random.choice(coords)
        aCell=Cell.getCell(random_cells[0],random_cells[1])
        neighbors=aCell.getNeighborCells()
        for aNeighborCell in neighbors:
            if aNeighborCell.value("typeZH")=="neutre":
                aNeighborCell.setValue('typeZH',"Aménité")
                break
    
    
# ZONES HUMIDES
Cell.setEntities('typeZH','neutre')

# Zone H 1
coords=[[3,2],[2,3],[3,3],[4,3],[3,4]] #Coordonnées des cellules choisies pour être ZH
for element in coords:
    Cell.setCell(element[0],element[1],"typeZH","alpha")
defAménité(coords)
ModeGestion.newAgentAtCoords(Cell,3,2,{"Mode de Gestion":"mode1"})

# Zone H 2
coords=[[12,6],[10,7],[11,7],[12,7],[13,7],[12,8],[13,8]]
for element in coords:
    Cell.setCell(element[0],element[1],"typeZH","alpha")
defAménité(coords)
ModeGestion.newAgentAtCoords(Cell,12,6,{"Mode de Gestion":"mode2"})

# Zone H 3
coords=[[6,10],[7,11],[8,11],[7,12],[8,12],[9,12],[8,13]]
for element in coords:
    Cell.setCell(element[0],element[1],"typeZH","beta")
defAménité(coords)
ModeGestion.newAgentAtCoords(Cell,6,10,{"Mode de Gestion":"mode1"})


# Zone H 4
coords=[[12,16],[13,16],[9,17],[10,17],[11,17],[12,17],[10,18],[11,18]]
for element in coords:
    Cell.setCell(element[0],element[1],"typeZH","gamma")
defAménité(coords)
ModeGestion.newAgentAtCoords(Cell,12,16,{"Mode de Gestion":"mode3"})

Cell.newPov("Type de zone humide","typeZH",{"alpha":Qt.darkGreen,"beta":Qt.darkBlue,"gamma":Qt.darkCyan,"neutre":Qt.gray,"Aménité":Qt.magenta})
Cell.newBorderPovColorAndWidth("Zones Joueurs","zones", {"Joueur A": [Qt.yellow,1], "Joueur B": [Qt.blue,1], "Joueur C": [Qt.red,1]})

Occupation=myModel.newAgentSpecies("Occupation du Joueur 1","triangleAgent2")
Occupation2=myModel.newAgentSpecies("Occupation du Joueur 2","arrowAgent1",defaultColor=Qt.yellow)
Occupation3=myModel.newAgentSpecies("Occupation du Joueur 3","ellipseAgent2",defaultColor=Qt.red)
nbMaxOccupation=5


theFirstLegend=myModel.newLegend()

Player1=myModel.newPlayer("Joueur A")
Player1.addGameAction(myModel.newUpdateAction(ModeGestion,{"Mode de Gestion":"mode1"}))
Player1.addGameAction(myModel.newUpdateAction(ModeGestion,{"Mode de Gestion":"mode2"}))
Player1.addGameAction(myModel.newUpdateAction(ModeGestion,{"Mode de Gestion":"mode3"}))
#TODO Il faut améliorer la portée de la update action pour udpate l'attribut "Mode de Gestion" de toutes les cellules de la ZH en même temps
Player1.addGameAction(myModel.newCreateAction(Occupation,listOfRestriction=[lambda: myModel.getAgentsOfSpecie(Occupation)<nbMaxOccupation,]))
#TODO Il faut modifier les Create et Update actions pour ajouter les mêmes fonctionnalités que la Move Action : des conditions sur la celulle cible
#TODO Create Action : revoir la condition sur l'agent (si elle est nécessaire)
Player1.addGameAction(myModel.newDeleteAction(Occupation))
#TODO sur le principe de EntityDef.setAttributesConcernedByUpdateMenu il faut ajouter la Delete Action dans le menu contextuel
Player1Legend=Player1.newControlPanel("Actions du Joueur A",showAgentsWithNoAtt=True)

Player2=myModel.newPlayer("Joueur B")
Player2.addGameAction(myModel.newUpdateAction(ModeGestion,{"Mode de Gestion":"mode1"}))
Player2.addGameAction(myModel.newUpdateAction(ModeGestion,{"Mode de Gestion":"mode2"}))
Player2.addGameAction(myModel.newUpdateAction(ModeGestion,{"Mode de Gestion":"mode3"}))
Player2.addGameAction(myModel.newCreateAction(Occupation2,listOfRestriction=[lambda: myModel.getAgentsOfSpecie(Occupation2)<nbMaxOccupation]))
Player2.addGameAction(myModel.newDeleteAction(Occupation2))
Player2Legend=Player2.newControlPanel("Actions du Joueur B",showAgentsWithNoAtt=True)

Player3=myModel.newPlayer("Joueur C")
Player3.addGameAction(myModel.newUpdateAction(ModeGestion,{"Mode de Gestion":"mode1"}))
Player3.addGameAction(myModel.newUpdateAction(ModeGestion,{"Mode de Gestion":"mode2"}))
Player3.addGameAction(myModel.newUpdateAction(ModeGestion,{"Mode de Gestion":"mode3"}))
Player3.addGameAction(myModel.newCreateAction(Occupation3,listOfRestriction=[lambda: myModel.getAgentsOfSpecie(Occupation3)<nbMaxOccupation]))
Player3.addGameAction(myModel.newDeleteAction(Occupation3))
Player3Legend=Player3.newControlPanel("Actions du Joueur C",showAgentsWithNoAtt=True)

userSelector=myModel.newUserSelector()
theTextBox=myModel.newTextBox("Le jeu n'a pas encore commencé. Avance d'un tour pour commencer","Comment jouer ?")

PhaseGestion=myModel.timeManager.newGamePhase('Phase Mode Gestion', [Player1,Player2,Player3])
PhaseGestion.setTextBoxText(theTextBox,"Vous pouvez modifier les modes des gestion des zones humides")

def transfert():
    #TODO
    pass

def séquestrer():
    #TODO
    pass

def impactAménité():
    #TODO
    pass

modelActions1=myModel.newModelAction([transfert(),séquestrer(),impactAménité()])
PhaseCalcul=myModel.timeManager.newModelPhase([modelActions1],autoForwardOn=True)
PhaseCalcul.setTextBoxText(theTextBox,"Calculs en cours...")

PhaseScoring=myModel.timeManager.newGamePhase('Phase Scoring', [Player1,Player2,Player3])
PhaseScoring.setTextBoxText(theTextBox,"Vous pouvez placer vos Occupations dans les aménités de la carte")

def résolution():
    #TODO
    pass

def init():
    #TODO
    pass
modelActions2=myModel.newModelAction([résolution(),init()])
LastPhase=myModel.timeManager.newModelPhase(modelActions2,autoForwardOn=True)
LastPhase.setTextBoxText(theTextBox,"Fin du tour... Calculs en cours...")


GameRounds = myModel.newTimeLabel("Temps", Qt.white, Qt.black, Qt.black)

# DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.black)
#TODO

# endGameRule = myModel.newEndGameRule(numberRequired=1)
#TODO

myModel.launch()


sys.exit(monApp.exec_())