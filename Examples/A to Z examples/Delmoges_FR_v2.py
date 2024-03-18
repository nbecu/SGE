import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1700,800, windowTitle="Delmoges_FR", typeOfLayout ="grid")

aGrid=myModel.newGrid(10,10,"square",size=60,gap=1)
aGrid.setCells("type","mer")
aGrid.setCells("sédim","sable")
aGrid.setCells_withColumn("type","grandFond",1)
aGrid.setCells_withColumn("type","côte",10)
aGrid.setCells_withColumn("sédim","côte",10)
aGrid.setCells_withColumn("sédim","vase",1)
aGrid.setCell(3,4,"sédim","rocher")
aGrid.setCell(10,1,"type",'port')
aGrid.setCells("stockCellMerlu",0)
aGrid.setCells("stockCellSole",0)
aGrid.setCells("txPrésenceMerlu",0)
aGrid.setCells("txPrésenceSole",0)
aGrid.setCells("quantitéPêchéeMerlu",0)
aGrid.setCells("quantitéPêchéeSole",0)
total_pêcheMerlu=0
total_pêcheSole=0

myModel.newPov("Cell Type","type",{"côte":Qt.green,"mer":Qt.cyan,"grandFond":Qt.blue,"port":Qt.darkGray})
myModel.newPov("Sédim","sédim",{"sable":Qt.yellow,"vase":Qt.darkGreen,"rocher":Qt.red,"côte":Qt.darkGray})

Soles=myModel.newAgentSpecies("Sole","triangleAgent1",{"stock":5478,"txrenouv":{1.0003},"sable":{1},"vase":{0.75},"rocher":{0}},uniqueColor=Qt.yellow,aSpeciesDefaultSize=20)
Merlus=myModel.newAgentSpecies("Merlu","triangleAgent2",{"stock":39455,"txrenouv":{1.0219},"sable":{1},"vase":{1},"rocher":{1}},uniqueColor=Qt.green,aSpeciesDefaultSize=20)
Navire=myModel.newAgentSpecies("Navire","arrowAgent1",{"txCapture_Sole":{2.75E-5},"txCapture_Merlu":{3.76E-5},"Quantité_pêchée_Merlu":{0},"Quantité_pêchée_Sole":{0},"PêcheCumMerlu":{0},"PêcheCumSole":{0}},uniqueColor=Qt.darkBlue,aSpeciesDefaultSize=20)

EspècesHalieutiques=[Soles,Merlus]

myModel.newAgentAtCoords(aGrid,Navire,10,1)
myModel.newAgentAtCoords(aGrid,Navire,10,1)
myModel.newAgentAtCoords(aGrid,Navire,10,1)
myModel.newAgentAtCoords(aGrid,Navire,10,1)
myModel.newAgentAtCoords(aGrid,Navire,10,1)
Player1 = myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.newMoveAction(Navire, 'infinite'))

theTextBox=myModel.newTextBox("Premier tour ! Place les bateaux pour pêcher !","Comment jouer ?")

InitPhase=myModel.timeManager.newGamePhase("Début du jeu, le joueur peut jouer",Player1)

GamePhase=myModel.timeManager.newGamePhase("Le joueur peut jouer",Player1)
GamePhase.setTextBoxText(theTextBox,"Place les bateaux à l'endroit où ils doivent pêcher")


DashBoard=myModel.newDashBoard()
# totMerlu=myModel.newSimVariable(0,"Total Merlu pêché")
# totSole=myModel.newSimVariable(0,"Total Sole pêché")
# indTotMerlu = DashBoard.addIndicatorOnSimVariable(totMerlu)
# indTotSole = DashBoard.addIndicatorOnSimVariable(totSole)
CelltotalMerlu=DashBoard.addIndicator("sumAtt","cell",attribute="quantitéPêchéeMerlu",indicatorName="Merlu pêché")
CelltotalSole=DashBoard.addIndicator("sumAtt","cell",attribute="quantitéPêchéeSole",indicatorName="Sole pêché")
indicateursMerlu = {}
indicateursSole = {}
for i in range(1, 6):
    indicateursMerlu[i] = DashBoard.addIndicatorOnEntity(str(i), "PêcheCumMerlu", "Navire", indicatorName=f"Merlu pêché par le bateau {i}")
    indicateursSole[i] = DashBoard.addIndicatorOnEntity(str(i), "PêcheCumSole", "Navire", indicatorName=f"Sole pêché par le bateau {i}")
DashBoard.showIndicators()


def tx_présence():
    CellsMer=[cell for cell in myModel.getCells(aGrid) if (cell.value('type') in ['mer', 'grandFond'])]
    nbCellsMer=len(CellsMer)
    nbNavires=len(myModel.getAgents("Navire"))
    for Species in EspècesHalieutiques:
        for cell in CellsMer:
            cell.setValue("txPrésence"+Species.name,list(Species.value(cell.value("sédim")))[0]/(nbCellsMer*nbNavires))

def pêche(cell):
    if len(cell.agents)!=0:
        for navire in cell.agents:
            navire.setValue('Quantité_pêchée_Merlu',cell.value("txPrésenceMerlu")*Merlus.value("stock")*navire.value("txCapture_Merlu"))
            navire.setValue('Quantité_pêchée_Sole',cell.value("txPrésenceSole")*Soles.value("stock")*navire.value("txCapture_Sole"))
            cell.setValue("quantitéPêchéeMerlu",cell.value("quantitéPêchéeMerlu")+navire.value('Quantité_pêchée_Merlu'))
            cell.setValue("quantitéPêchéeSole",cell.value("quantitéPêchéeSole")+navire.value('Quantité_pêchée_Sole'))
    

def renouvellementStock_port(total_pêcheMerlu,total_pêcheSole):
    sommePêcheMerlu=0
    sommePêcheSole=0
    for navire in myModel.getAgents("Navire"):
        sommePêcheMerlu=sommePêcheMerlu+navire.value('Quantité_pêchée_Merlu')
        sommePêcheSole=sommePêcheSole+navire.value('Quantité_pêchée_Sole')
        print("Pêche du jour :")
        print(navire.value('Quantité_pêchée_Merlu'))
        navire.setValue("PêcheCumMerlu", navire.value("PêcheCumMerlu")+navire.value('Quantité_pêchée_Merlu'))
        navire.setValue("PêcheCumSole", navire.value("PêcheCumSole")+navire.value('Quantité_pêchée_Sole'))
        navire.setValue('Quantité_pêchée_Merlu',0)
        navire.setValue('Quantité_pêchée_Sole',0)
        indBateauMerlu = indicateursMerlu[int(navire.id)]
        indBateauSole = indicateursSole[int(navire.id)]
        indBateauSole.setResult(navire.value("PêcheCumSole"))
        indBateauMerlu.setResult(navire.value("PêcheCumMerlu"))  
    
    Soles.setValue("stock",((Soles.value("stock")-sommePêcheSole)*list(Soles.value("txrenouv"))[0]))
    Merlus.setValue("stock",((Merlus.value("stock")-sommePêcheMerlu)*list(Merlus.value("txrenouv"))[0]))
    print("STOCK MERLU :")
    print(Merlus.value("stock"))
    print(myModel.timeManager.currentRound)
    total_pêcheMerlu=total_pêcheMerlu+sommePêcheMerlu
    total_pêcheSole=total_pêcheSole+sommePêcheSole
    # indTotMerlu.setResult(total_pêcheMerlu)
    # indTotSole.setResult(total_pêcheSole)
    
    for navire in myModel.getAgents("Navire"):
        navire.moveAgent(method='cell',cellID='cell10-1')

ModelActionPêche=myModel.newModelAction_onCells(lambda cell: pêche(cell))
ModelActionRésolution=myModel.newModelAction(lambda : renouvellementStock_port(total_pêcheMerlu,total_pêcheSole))

PhasePêche=myModel.timeManager.newModelPhase(ModelActionPêche, name="Pêche")
PhasePêche.setTextBoxText(theTextBox,"Pêche en cours")
PhaseRésolution=myModel.timeManager.newModelPhase(ModelActionRésolution, name="Renouvellement des stocks et retour au port")
PhaseRésolution.setTextBoxText(theTextBox,"Résolution en cours")

myModel.newLegendAdmin(showAgentsWithNoAtt=True)
myModel.newTimeLabel()

tx_présence()

myModel.launch()
sys.exit(monApp.exec_())