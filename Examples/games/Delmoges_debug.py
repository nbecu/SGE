import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1100,550, windowTitle="Delmoges_FR", typeOfLayout ="grid")

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
Cells.newBorderPovColorAndWidth("Incitation","incitation", {"neutre": [Qt.black,1], "bonus": [Qt.green,4], "malus": [Qt.red,4]})

Soles=myModel.newAgentSpecies("Sole","triangleAgent1",{"stock":5478,"txrenouv":1.0003,"sable":1,"vase":0.75,"rocher":0,"prix":14.6,"facteurTemps":6329}) #valeur initiale facteur temps : 1029. Changée à 6329 pour être dans les ordres de grandeur de l'impact des captures plus importantes (baisse de 5.5% à effort de référence sur 10 ans)
Merlus=myModel.newAgentSpecies("Merlu","triangleAgent2",{"stock":39455,"txrenouv":1.0219,"sable":1,"vase":1,"rocher":1,"prix":3.2,"facteurTemps":6329})
Navire=myModel.newAgentSpecies("Navire","arrowAgent1")
Navire.setDefaultValues({"txCapture_Sole":2.75E-5,"txCapture_Merlu":3.76E-5,"Quantité_pêchée_Merlu":0,"Quantité_pêchée_Sole":0,"PêcheCumMerlu":0,"PêcheCumSole":0,"facteurEffortMerlu":12.5,"facteurEffortSole":2.84,"lastIncitationValue":"neutre"})#,"Invisibility":"True"})

Navire.setAttributeValueToDisplayInContextualMenu("Quantité_pêchée_Merlu",'Merlu pêché')
Navire.setAttributeValueToDisplayInContextualMenu("Quantité_pêchée_Sole",'Sole pêché')

EspècesHalieutiques=[Soles,Merlus]

Navire.newAgentsOnCell(5,Port)

Player1 = myModel.newPlayer("Pêcheur",attributesAndValues=None)
Move1=myModel.newMoveAction(Navire, 'infinite')
Move1.addFeedback(lambda navire: navire.setValue("lastIncitationValue",navire.cell.value("incitation")))
Player1.addGameAction(Move1)
Create1=myModel.newCreateAction(Navire,aNumber=10)
Create1.addCondition(lambda TargetCell: TargetCell.value("type")=="port")
Player1.addGameAction(Create1)
Player1ControlPanel = Player1.newControlPanel("Actions Pêcheur")

Player2= myModel.newPlayer("Gestionnaire",attributesAndValues=None)
Update1=myModel.newModifyAction("Cell",{"incitation":"bonus"},listOfRestriction=[lambda: (Cells.nb_withValue("incitation","bonus")+Cells.nb_withValue("incitation","malus"))<30])
Update2=myModel.newModifyAction("Cell",{"incitation":"malus"},listOfRestriction=[lambda: (Cells.nb_withValue("incitation","bonus")+Cells.nb_withValue("incitation","malus"))<30])
Player2.addGameAction(Update1)
Player2.addGameAction(Update2)
Player2ControlPanel = Player2.newControlPanel("Actions Gestionnaire")


theTextBox=myModel.newTextBox("Le jeu n'a pas encore commencé. Avance d'un tour pour commencer","Comment jouer ?")

def tx_présence():
    CellsMer=[cell for cell in myModel.getCells(Cells) if (cell.value('type') in ['mer', 'grandFond'])]
    nbCellsMer=len(CellsMer)
    nbNavireEquivalentEffortRefZone=len(myModel.getAgentsOfSpecie("Navire"))
    for Species in EspècesHalieutiques:
        for cell in CellsMer:
            cell.setValue("txPrésence"+Species.entityName,Species.value(cell.value("sédim"))/(nbCellsMer*nbNavireEquivalentEffortRefZone))

def pêche(cell):
    if len(cell.agents)!=0:
        for navire in cell.agents:
            navire.setValue('Quantité_pêchée_Merlu',round(cell.value("txPrésenceMerlu")*Merlus.value("stock")*navire.value("txCapture_Merlu")*Merlus.value("facteurTemps")*navire.value("facteurEffortMerlu"),0))
            navire.setValue('Quantité_pêchée_Sole',round(cell.value("txPrésenceSole")*Soles.value("stock")*navire.value("txCapture_Sole")*Soles.value("facteurTemps")*navire.value("facteurEffortSole"),0))
            navire.setValue("PêcheCumMerlu",navire.value("PêcheCumMerlu")+navire.value('Quantité_pêchée_Merlu'))
            navire.setValue("PêcheCumSole",navire.value("PêcheCumSole")+navire.value('Quantité_pêchée_Sole'))
            

def feedbackPêche():
    sommePêcheMerlu=0
    sommePêcheSole=0
    
    for navire in myModel.getAgentsOfSpecie("Navire"):
        sommePêcheMerlu=sommePêcheMerlu+navire.value('Quantité_pêchée_Merlu')
        sommePêcheSole=sommePêcheSole+navire.value('Quantité_pêchée_Sole')
            
    stockMerlu=round((Merlus.value("stock")-sommePêcheMerlu)*Merlus.value("txrenouv"),0)
    stockSole=round((Soles.value("stock")-sommePêcheSole)*Soles.value("txrenouv"),0)
    Soles.setValue("stock",stockSole)
    Merlus.setValue("stock",stockMerlu)

def renouvellementStock_port():
    sommeBenef=0
    sommeRevenus=0
    malus=0
    bonus=0
    for navire in myModel.getAgentsOfSpecie("Navire"):
        revenusBateau=navire.value('Quantité_pêchée_Merlu')*Merlus.value("prix")+navire.value('Quantité_pêchée_Sole')*Soles.value("prix")
        sommeRevenus=sommeRevenus+revenusBateau
        if navire.value('lastIncitationValue')=="bonus":
            benefBateau=revenusBateau+revenusBateau*0.1
            bonus=bonus+benefBateau
        if navire.value('lastIncitationValue')=="malus":
            benefBateau=revenusBateau-revenusBateau*0.1
            malus=malus+benefBateau
        else:
            benefBateau=revenusBateau
        sommeBenef=sommeBenef+benefBateau
        benefBateau=0
        navire.setValue('Quantité_pêchée_Merlu',0)
        navire.setValue('Quantité_pêchée_Sole',0)
        navire.moveAgent(method='cell',cellID=10)

        

    revenuTour.setValue(round(sommeRevenus,0))
    benefice.setValue(round(sommeBenef,0))
    revenuMalus.setValue(round(malus,0))
    revenuBonus.setValue(round(bonus,0))

def reset():
    revenuBonus.setValue(0)
    revenuMalus.setValue(0)
    revenuTour.setValue(0)
    benefice.setValue(0)
    for navire in myModel.getAgentsOfSpecie("Navire"):
        navire.setValue("lastIncitationValue","neutre")


PhaseReset=myModel.timeManager.newModelPhase(myModel.newModelAction(lambda: reset()), name = 'Init du tour',autoForwardOn=True)

GamePhase=myModel.timeManager.newGamePhase("Les joueurs peuvent jouer",[Player1,Player2])
GamePhase.setTextBoxText(theTextBox,"Place les bateaux à l'endroit où ils doivent pêcher")

ModelActionPêche=myModel.newModelAction_onCells(lambda cell: pêche(cell))
ModelActionFeedback=myModel.newModelAction(lambda: feedbackPêche())
ModelActionRésolution=myModel.newModelAction(lambda : renouvellementStock_port())

PhasePêche=myModel.timeManager.newModelPhase([ModelActionPêche,ModelActionFeedback], name="Pêche")
PhasePêche.setTextBoxText(theTextBox,"Pêche en cours")
PhaseRésolution=myModel.timeManager.newModelPhase(ModelActionRésolution, name="Renouvellement stocks")
PhaseRésolution.setTextBoxText(theTextBox,"Résolution en cours")

DashBoard=myModel.newDashBoard("DashBoard Pêcheur")
DashBoard.addIndicator(Navire,"sumAtt",attribute="PêcheCumMerlu",title="Merlu pêché (depuis an 0)")
DashBoard.addIndicator(Navire,"sumAtt",attribute="PêcheCumSole",title="Sole pêché (depuis an 0)")
DashBoard.addSeparator()
DashBoard.addIndicator(Navire,"sumAtt",attribute="Quantité_pêchée_Merlu",title="Merlu pêché (ce tour)")
DashBoard.addIndicator(Navire,"sumAtt",attribute="Quantité_pêchée_Sole",title="Sole pêché (ce tour)")
revenuTour=myModel.newSimVariable("Revenus (k€)",0)
benefice=myModel.newSimVariable("Bénéfice (k€)",0)
indRevenu=DashBoard.addIndicatorOnSimVariable(revenuTour)
indBenefice=DashBoard.addIndicatorOnSimVariable(benefice)

revenuMalus=myModel.newSimVariable("Total malus prélevé (k€)",0)
revenuBonus=myModel.newSimVariable("Total bonus versé (k€)",0)
DashBoard2=myModel.newDashBoard("DashBoard Gestionnaire")
indMerlu=DashBoard2.addIndicatorOnEntity(Merlus,"stock",title="Stock de Merlus")
indSole=DashBoard2.addIndicatorOnEntity(Soles,"stock",title="Stock de Soles")
sep2=DashBoard2.addSeparator()
indNbBonus=DashBoard2.addIndicator(Navire,"nb",attribute="lastIncitationValue",value="bonus",title="Nb Bateau en zone bonus",displayRefresh="onTimeConditions",onTimeConditions={"phaseNumber":[4,1]})
indBenefice=DashBoard2.addIndicatorOnSimVariable(revenuBonus)
indNbMalus=DashBoard2.addIndicator(Navire,"nb",attribute="lastIncitationValue",value="malus",title="Nb Bateau en zone malus",displayRefresh="onTimeConditions",onTimeConditions={"phaseNumber":[4,1]})
indBenefice=DashBoard2.addIndicatorOnSimVariable(revenuMalus)


Legend=myModel.newLegend(showAgentsWithNoAtt=True)
TimeLabel=myModel.newTimeLabel("Time")

userSelector=myModel.newUserSelector()
tx_présence()

# DELMOGES CUSTOM LAYOUT SOLUTION
Cells.grid.moveToCoords(250,100)
TimeLabel.moveToCoords(700,45)
theTextBox.moveToCoords(20,45)
Player1ControlPanel.moveToCoords(20,220)
Player2ControlPanel.moveToCoords(700,220)
userSelector.moveToCoords(280,35)
Legend.moveToCoords(970,120)
DashBoard.moveToCoords(20,330)
DashBoard2.moveToCoords(700,330)

myModel.launch()
# myModel.launch_withMQTT("Instantaneous")
sys.exit(monApp.exec_())