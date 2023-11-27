import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1700,800, windowTitle="Delmoges_FR", typeOfLayout ="grid")

aGrid=myModel.newCellsOnGrid(10,10,"square",size=60,gap=1)
aGrid.setEntities("type","mer")
aGrid.setEntities("sédim","sable")
aGrid.setEntities_withColumn("type","grandFond",1)
aGrid.setEntities_withColumn("type","côte",10)
aGrid.setEntities_withColumn("sédim","côte",10)
aGrid.setEntities_withColumn("sédim","vase",1)
Port=aGrid.getEntity(10,1)
Port.setValue("type",'port')
Rocher=aGrid.getRandom_withValue("type","mer")
Rocher.setValue("sédim","rocher")
# aGrid.setCell(3,4,"sédim","rocher")
# aGrid.setCell(10,1,"type",'port')
aGrid.setEntities("stockCellMerlu",0)
aGrid.setEntities("stockCellSole",0)
aGrid.setEntities("txPrésenceMerlu",0)
aGrid.setEntities("txPrésenceSole",0)
aGrid.setEntities("quantitéPêchéeMerlu",0)
aGrid.setEntities("quantitéPêchéeSole",0)
total_pêcheMerlu=0
total_pêcheSole=0

aGrid.newPov("Cell Type","type",{"côte":Qt.green,"mer":Qt.cyan,"grandFond":Qt.blue,"port":Qt.darkGray})
aGrid.newPov("Sédim","sédim",{"sable":Qt.yellow,"vase":Qt.darkGreen,"rocher":Qt.red,"côte":Qt.darkGray})

Soles=myModel.newAgentSpecies("Sole","triangleAgent1",{"stock":5478,"txrenouv":{1.0003},"sable":{1},"vase":{0.75},"rocher":{0}})
Merlus=myModel.newAgentSpecies("Merlu","triangleAgent2",{"stock":39455,"txrenouv":{1.0219},"sable":{1},"vase":{1},"rocher":{1}})
Navire=myModel.newAgentSpecies("Navire","arrowAgent1",{"txCapture_Sole":{2.75E-5},"txCapture_Merlu":{3.76E-5},"Quantité_pêchée_Merlu":{0},"Quantité_pêchée_Sole":{0},"PêcheCumMerlu":{0},"PêcheCumSole":{0}})
Navire.setDefaultValues({"txCapture_Sole":{2.75E-5},"txCapture_Merlu":{3.76E-5},"Quantité_pêchée_Merlu":0,"Quantité_pêchée_Sole":0,"PêcheCumMerlu":0,"PêcheCumSole":0})



EspècesHalieutiques=[Soles,Merlus]

Navire.newAgentAtCoords(aGrid,10,1)
Navire.newAgentAtCoords(aGrid,10,1)
Navire.newAgentAtCoords(aGrid,10,1)
Navire.newAgentAtCoords(aGrid,10,1)
Navire.newAgentAtCoords(aGrid,10,1)
Player1 = myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.newMoveAction(Navire, 'infinite'))

theTextBox=myModel.newTextBox("Premier tour ! Place les bateaux pour pêcher !","Comment jouer ?")

InitPhase=myModel.timeManager.newGamePhase("Début du jeu, le joueur peut jouer",Player1)

GamePhase=myModel.timeManager.newGamePhase("Le joueur peut jouer",Player1)
GamePhase.setTextBoxText(theTextBox,"Place les bateaux à l'endroit où ils doivent pêcher")


DashBoard=myModel.newDashBoard()
# totMerlu=myModel.newSimVariable("Total Merlu pêché",0)
# totSole=myModel.newSimVariable("Total Sole pêché",0)
# indTotMerlu = DashBoard.addIndicatorOnSimVariable(totMerlu)
# indTotSole = DashBoard.addIndicatorOnSimVariable(totSole)
CelltotalMerlu=DashBoard.addIndicator("sumAtt","Cell",attribute="quantitéPêchéeMerlu",indicatorName="Merlu pêché")
CelltotalSole=DashBoard.addIndicator("sumAtt","Cell",attribute="quantitéPêchéeSole",indicatorName="Sole pêché")
indicateursMerlu = {}
indicateursSole = {}
for i in range(1,6):
    indicateursMerlu[i] = DashBoard.addIndicatorOnEntity(Navire.getEntity(i), "PêcheCumMerlu", indicatorName=f"Merlu pêché par le bateau {i}")
    indicateursSole[i] = DashBoard.addIndicatorOnEntity(Navire.getEntity(i), "PêcheCumSole", indicatorName=f"Sole pêché par le bateau {i}")
DashBoard.showIndicators()


def tx_présence():
    CellsMer=[cell for cell in myModel.getCells(aGrid) if (cell.value('type') in ['mer', 'grandFond'])]
    nbCellsMer=len(CellsMer)
    nbNavires=len(myModel.getAgentsOfSpecie("Navire"))
    for Species in EspècesHalieutiques:
        for cell in CellsMer:
            cell.setValue("txPrésence"+Species.entityName,list(Species.value(cell.value("sédim")))[0]/(nbCellsMer*nbNavires))

def pêche(cell):
    if len(cell.agents)!=0:
        for navire in cell.agents:
            navire.setValue('Quantité_pêchée_Merlu',cell.value("txPrésenceMerlu")*Merlus.value("stock")*list(navire.value("txCapture_Merlu"))[0])
            navire.setValue('Quantité_pêchée_Sole',cell.value("txPrésenceSole")*Soles.value("stock")*list(navire.value("txCapture_Sole"))[0])
            cell.setValue("quantitéPêchéeMerlu",cell.value("quantitéPêchéeMerlu")+navire.value('Quantité_pêchée_Merlu'))
            cell.setValue("quantitéPêchéeSole",cell.value("quantitéPêchéeSole")+navire.value('Quantité_pêchée_Sole'))
    

def renouvellementStock_port(total_pêcheMerlu,total_pêcheSole):
    sommePêcheMerlu=0
    sommePêcheSole=0
    for navire in myModel.getAgentsOfSpecie("Navire"):
        sommePêcheMerlu=sommePêcheMerlu+navire.value('Quantité_pêchée_Merlu')
        sommePêcheSole=sommePêcheSole+navire.value('Quantité_pêchée_Sole')
        print("Pêche du jour :")
        print(navire.value('Quantité_pêchée_Merlu'))
        navire.setValue("PêcheCumMerlu", navire.value("PêcheCumMerlu")+navire.value('Quantité_pêchée_Merlu'))
        navire.setValue("PêcheCumSole", navire.value("PêcheCumSole")+navire.value('Quantité_pêchée_Sole'))
        navire.setValue('Quantité_pêchée_Merlu',0)
        navire.setValue('Quantité_pêchée_Sole',0)
        # indBateauMerlu = indicateursMerlu[int(navire.id)]
        # indBateauSole = indicateursSole[int(navire.id)]
        # indBateauSole.setResult(navire.value("PêcheCumSole"))
        # indBateauMerlu.setResult(navire.value("PêcheCumMerlu"))  
    
    Soles.setValue("stock",((Soles.value("stock")-sommePêcheSole)*list(Soles.value("txrenouv"))[0]))
    Merlus.setValue("stock",((Merlus.value("stock")-sommePêcheMerlu)*list(Merlus.value("txrenouv"))[0]))
    print("STOCK MERLU :")
    print(Merlus.value("stock"))
    print(myModel.timeManager.currentRound)
    total_pêcheMerlu=total_pêcheMerlu+sommePêcheMerlu
    total_pêcheSole=total_pêcheSole+sommePêcheSole
    # indTotMerlu.setResult(total_pêcheMerlu)
    # indTotSole.setResult(total_pêcheSole)
    
    for navire in myModel.getAgentsOfSpecie("Navire"):
        navire.moveAgent(method='cell',cellID=10)

ModelActionPêche=myModel.newModelAction_onCells(lambda cell: pêche(cell))
ModelActionRésolution=myModel.newModelAction(lambda : renouvellementStock_port(total_pêcheMerlu,total_pêcheSole))

PhasePêche=myModel.timeManager.newModelPhase(ModelActionPêche, name="Pêche")
PhasePêche.setTextBoxText(theTextBox,"Pêche en cours")
PhaseRésolution=myModel.timeManager.newModelPhase(ModelActionRésolution, name="Renouvellement des stocks et retour au port")
PhaseRésolution.setTextBoxText(theTextBox,"Résolution en cours")

myModel.newLegend(showAgentsWithNoAtt=True)
myModel.newTimeLabel("GameTime")

tx_présence()

myModel.launch()
sys.exit(monApp.exec_())