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
Navire=myModel.newAgentSpecies("Navire","arrowAgent1",{"txCapture_Sole":{2.75E-5},"txCapture_Merlu":{3.76E-5},"Quantité_pêchée_Merlu":{0},"Quantité_pêchée_Sole":{0}},uniqueColor=Qt.darkBlue,aSpeciesDefaultSize=20)
myModel.newAgentAtCoords(aGrid,Navire,10,1)
myModel.newAgentAtCoords(aGrid,Navire,10,1)
myModel.newAgentAtCoords(aGrid,Navire,10,1)
myModel.newAgentAtCoords(aGrid,Navire,10,1)
myModel.newAgentAtCoords(aGrid,Navire,10,1)
Player1 = myModel.newPlayer("Player 1")
Player1.addGameAction(myModel.newMoveAction(Navire, 'infinite'))
myModel.timeManager.newGamePhase("Le joueur peut jouer",Player1)

DashBoard=myModel.newDashBoard()
indicateurPêcheMerlu = DashBoard.addIndicator("sumAtt","cell",attribute="quantitéPêchéeMerlu",indicatorName="Quantité de merlu pêchée")
indicateurPêcheSole = DashBoard.addIndicator("sumAtt","cell",attribute="quantitéPêchéeSole",indicatorName="Quantité de sole pêchée")

def tx_présence():
    nbNavires=len(myModel.getAgents("Navire"))
    for Species in myModel.getAgentSpecies():
        if Species.name != "Navire":
            for cell in myModel.getCells(aGrid):  
                if cell.dictOfAttributs["sédim"] != "côte":
                    cell.dictOfAttributs["txPrésence"+Species.name]=list(Species.dictOfAttributs[cell.dictOfAttributs["sédim"]])[0]/(90*nbNavires)

def pêche(cell):
    if len(cell.agents)!=0:
        for navire in cell.agents:
            navire.dictOfAttributs['Quantité_pêchée_Merlu']=cell.dictOfAttributs["txPrésenceMerlu"]*Merlus.dictOfAttributs["stock"]*navire.dictOfAttributs["txCapture_Merlu"]
            navire.dictOfAttributs['Quantité_pêchée_Sole']=cell.dictOfAttributs["txPrésenceSole"]*Soles.dictOfAttributs["stock"]*navire.dictOfAttributs["txCapture_Sole"] 
            cell.dictOfAttributs["quantitéPêchéeMerlu"]=+navire.dictOfAttributs['Quantité_pêchée_Merlu']
            cell.dictOfAttributs["quantitéPêchéeSole"]=+navire.dictOfAttributs['Quantité_pêchée_Sole']

def renouvellementStock_port():
    sommePêcheMerlu=0
    sommePêcheSole=0
    for navire in myModel.getAgents("Navire"):
        sommePêcheMerlu=+navire.dictOfAttributs['Quantité_pêchée_Merlu']
        sommePêcheSole=+navire.dictOfAttributs['Quantité_pêchée_Sole']
        navire.dictOfAttributs['Quantité_pêchée_Merlu']=0
        navire.dictOfAttributs['Quantité_pêchée_Sole']=0
        
    Soles.dictOfAttributs["stock"]=(-sommePêcheSole)*list(Soles.dictOfAttributs["txrenouv"])[0]
    Merlus.dictOfAttributs["stock"]=(-sommePêcheMerlu)*list(Merlus.dictOfAttributs["txrenouv"])[0]
    total_pêcheMerlu=+sommePêcheMerlu
    total_pêcheSole=+sommePêcheSole

    print("total merlu péché"+str(total_pêcheMerlu))
    print("total sole péché"+str(total_pêcheSole))




    for navire in myModel.getAgents("Navire"):
        navire.moveAgent(method='cell',cellID='cell10-1')

ModelActionPêche=myModel.newModelAction_onCells(lambda cell: pêche(cell))
ModelActionRésolution=myModel.newModelAction(lambda : renouvellementStock_port())

PhasePêche=myModel.timeManager.newModelPhase(ModelActionPêche, name="Pêche")
PhaseRésolution=myModel.timeManager.newModelPhase(ModelActionRésolution, name="Renouvellement des stocks et retour au port")

myModel.newTextBox("Place les bateaux à l'endroit où ils doivent pêcher","Comment jouer ?")
myModel.newLegendAdmin(showAgentsWithNoAtt=True)
myModel.newTimeLabel()

tx_présence()

myModel.launch()
sys.exit(monApp.exec_())