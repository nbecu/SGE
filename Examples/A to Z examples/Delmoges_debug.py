import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1700,800, windowTitle="Delmoges_FR", typeOfLayout ="grid",testMode=True)

Cells=myModel.newCellsOnGrid(10,10,"square",size=40,gap=1)
Cells.setEntities("type","mer")
Cells.setEntities("sédim","sable")
Cells.setEntities("incitation","neutre")
Cells.setEntities_withColumn("type","grandFond",1)
Cells.setEntities_withColumn("type","côte",10)
Cells.setEntities_withColumn("sédim","côte",10)
Cells.setEntities_withColumn("sédim","vase",1)
Port=Cells.getEntity(10,1)
Port.setValue("type",'port')
Cells.setRandomEntity_withValue("sédim","rocher","type","mer")
Cells.setEntities("stockCellMerlu",0)
Cells.setEntities("stockCellSole",0)
Cells.setEntities("txPrésenceMerlu",0)
Cells.setEntities("txPrésenceSole",0)
Cells.setEntities("quantitéPêchéeMerlu",0)
Cells.setEntities("quantitéPêchéeSole",0)
stockMerlu=0
stockSole=0


Cells.newPov("Cell Type","type",{"côte":Qt.green,"mer":Qt.cyan,"grandFond":Qt.blue,"port":Qt.darkGray})
Cells.newPov("Sédim","sédim",{"sable":Qt.yellow,"vase":Qt.darkGreen,"rocher":Qt.red,"côte":Qt.darkGray})
Cells.newBorderPovColorAndWidth("Incitation","incitation", {"neutre": [Qt.black,4], "bonus": [Qt.green,4], "malus": [Qt.red,4]})

Soles=myModel.newAgentSpecies("Sole","triangleAgent1",{"stock":5478,"txrenouv":{1.0003},"sable":{1},"vase":{0.75},"rocher":{0},"prix":14.6,"facteurTemps":6329}) #valeur initiale facteur temps : 1029. Changée à 6329 pour être dans les ordres de grandeur de l'impact des captures plus importantes (baisse de 5.5% à effort de référence sur 10 ans)
Merlus=myModel.newAgentSpecies("Merlu","triangleAgent2",{"stock":39455,"txrenouv":{1.0219},"sable":{1},"vase":{1},"rocher":{1},"prix":3.2,"facteurTemps":6329})
Navire=myModel.newAgentSpecies("Navire","arrowAgent1")
Navire.setDefaultValues({"txCapture_Sole":{2.75E-5},"txCapture_Merlu":{3.76E-5},"Quantité_pêchée_Merlu":0,"Quantité_pêchée_Sole":0,"PêcheCumMerlu":0,"PêcheCumSole":0,"facteurEffortMerlu":12.5,"facteurEffortSole":2.84,"lastIncitationValue":"neutre"})


EspècesHalieutiques=[Soles,Merlus]

Navire.newAgentsOnCell(5,Port)

Player1 = myModel.newPlayer("Pêcheur")
Move1=myModel.newMoveAction(Navire, 'infinite')
Move1.addFeedback(lambda navire: navire.setValue("lastIncitationValue",navire.cell.value("incitation")))
Player1.addGameAction(Move1)
Create1=myModel.newCreateAction(Navire,10)
Create1.addCondition(lambda TargetCell: TargetCell.value("type")=="port")
Player1.addGameAction(Create1)
Player1ControlPanel = Player1.newControlPanel("Actions Pêcheur")

Player2= myModel.newPlayer("Gestionnaire")
Update1=myModel.newUpdateAction("Cell","infinite",{"incitation":"bonus"},[lambda: (Cells.nb_withValue("incitation","bonus")+Cells.nb_withValue("incitation","malus"))<30])
Update2=myModel.newUpdateAction("Cell","infinite",{"incitation":"malus"},[lambda: (Cells.nb_withValue("incitation","bonus")+Cells.nb_withValue("incitation","malus"))<30])
Player2.addGameAction(Update1)
Player2.addGameAction(Update2)
Player2ControlPanel = Player2.newControlPanel("Actions Gestionnaire")


theTextBox=myModel.newTextBox("Premier tour ! Place les bateaux pour pêcher !","Comment jouer ?")

GamePhase=myModel.timeManager.newGamePhase("Le joueur peut jouer",[Player1])
GamePhase.setTextBoxText(theTextBox,"Place les bateaux à l'endroit où ils doivent pêcher")


DashBoard=myModel.newDashBoard("DashBoard Pêcheur")
DashBoard.addIndicator("sumAtt",Navire,attribute="PêcheCumMerlu",indicatorName="Merlu pêché (depuis an 0)")
DashBoard.addIndicator("sumAtt",Navire,attribute="PêcheCumSole",indicatorName="Sole pêché (depuis an 0)")
DashBoard.addSeparator()
DashBoard.addIndicator("sumAtt",Navire,attribute="Quantité_pêchée_Merlu",indicatorName="Merlu pêché (ce tour)")
DashBoard.addIndicator("sumAtt",Navire,attribute="Quantité_pêchée_Sole",indicatorName="Sole pêché (ce tour)")
revenuTour=myModel.newSimVariable("Revenus (k€)",0)
benefice=myModel.newSimVariable("Bénéfice (k€)",0)
indRevenu=DashBoard.addIndicatorOnSimVariable(revenuTour)
indBenefice=DashBoard.addIndicatorOnSimVariable(benefice)

DashBoard.showIndicators()

DashBoard2=myModel.newDashBoard("DashBoard Gestionnaire")
indMerlu=DashBoard2.addIndicatorOnEntity(Merlus,"stock",indicatorName="Stock de Merlus")
indSole=DashBoard2.addIndicatorOnEntity(Soles,"stock",indicatorName="Stock de Soles")
DashBoard2.addSeparator()
indNbBonus=DashBoard2.addIndicator("nb",Navire,attribute="lastIncitationValue",value="bonus",indicatorName="Nb Bateau en zone bonus")
indNbMalus=DashBoard2.addIndicator("nb",Navire,attribute="lastIncitationValue",value="malus",indicatorName="Nb Bateau en zone malus")
DashBoard2.showIndicators()

def tx_présence():
    CellsMer=[cell for cell in myModel.getCells(Cells) if (cell.value('type') in ['mer', 'grandFond'])]
    nbCellsMer=len(CellsMer)
    nbNavireEquivalentEffortRefZone=len(myModel.getAgentsOfSpecie("Navire"))
    for Species in EspècesHalieutiques:
        for cell in CellsMer:
            cell.setValue("txPrésence"+Species.entityName,list(Species.value(cell.value("sédim")))[0]/(nbCellsMer*nbNavireEquivalentEffortRefZone))

def setAgentsMenu():
    for navire in myModel.getAgentsOfSpecie("Navire"):
        navire.setNewMenuEntry("Pêche Merlu du tour :"+str(navire.value("Quantité_pêchée_Merlu")))
        navire.setNewMenuEntry("Pêche Sole du tour :"+str(navire.value("Quantité_pêchée_Sole")))

def pêche(cell):
    if len(cell.agents)!=0:
        for navire in cell.agents:
            navire.setValue('Quantité_pêchée_Merlu',round(cell.value("txPrésenceMerlu")*Merlus.value("stock")*list(navire.value("txCapture_Merlu"))[0]*Merlus.value("facteurTemps")*navire.value("facteurEffortMerlu"),0))
            navire.setValue('Quantité_pêchée_Sole',round(cell.value("txPrésenceSole")*Soles.value("stock")*list(navire.value("txCapture_Sole"))[0]*Soles.value("facteurTemps")*navire.value("facteurEffortSole"),0))
            navire.setValue("PêcheCumMerlu",navire.value("PêcheCumMerlu")+navire.value('Quantité_pêchée_Merlu'))
            navire.setValue("PêcheCumSole",navire.value("PêcheCumSole")+navire.value('Quantité_pêchée_Sole'))
            

def feedbackPêche():
    sommePêcheMerlu=0
    sommePêcheSole=0
    sommeBenef=0
    sommeRevenus=0
    for navire in myModel.getAgentsOfSpecie("Navire"):
        sommePêcheMerlu=sommePêcheMerlu+navire.value('Quantité_pêchée_Merlu')
        sommePêcheSole=sommePêcheSole+navire.value('Quantité_pêchée_Sole')
        revenusBateau=navire.value('Quantité_pêchée_Merlu')*Merlus.value("prix")+navire.value('Quantité_pêchée_Sole')*Soles.value("prix")
        sommeRevenus=sommeRevenus+revenusBateau
        print("Incitation Navire : "+str(navire.value('lastIncitationValue')))
        print("Incitation Cellule : "+str(navire.cell.value('incitation')))
        print("---------")
        if navire.value('lastIncitationValue')=="bonus":
            benefBateau=revenusBateau+revenusBateau*0.1
        if navire.value('lastIncitationValue')=="malus":
            benefBateau=revenusBateau-revenusBateau*0.1
        else:
            benefBateau=revenusBateau
        sommeBenef=sommeBenef+benefBateau
        benefBateau=0

    revenuTour.setValue(round(sommeRevenus,0))
    benefice.setValue(round(sommeBenef,0))    
    stockMerlu=round((Merlus.value("stock")-sommePêcheMerlu)*list(Merlus.value("txrenouv"))[0],0)
    stockSole=round((Soles.value("stock")-sommePêcheSole)*list(Soles.value("txrenouv"))[0],0)
    Soles.setValue("stock",stockSole)
    Merlus.setValue("stock",stockMerlu)

def renouvellementStock_port():
    for navire in myModel.getAgentsOfSpecie("Navire"):
        navire.setValue('Quantité_pêchée_Merlu',0)
        navire.setValue('Quantité_pêchée_Sole',0)
        navire.moveAgent(method='cell',cellID=10)

ModelActionPêche=myModel.newModelAction_onCells(lambda cell: pêche(cell))
ModelActionFeedback=myModel.newModelAction(lambda: feedbackPêche())
ModelActionRésolution=myModel.newModelAction(lambda : renouvellementStock_port())

PhasePêche=myModel.timeManager.newModelPhase([ModelActionPêche,ModelActionFeedback], name="Pêche")
PhasePêche.setTextBoxText(theTextBox,"Pêche en cours")
PhaseRésolution=myModel.timeManager.newModelPhase(ModelActionRésolution, name="Renouvellement des stocks et retour au port")
PhaseRésolution.setTextBoxText(theTextBox,"Résolution en cours")

myModel.newLegend(showAgentsWithNoAtt=True)
myModel.newTimeLabel("GameTime")

userSelector=myModel.newUserSelector()
tx_présence()
setAgentsMenu()

myModel.launch()
sys.exit(monApp.exec_())