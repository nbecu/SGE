import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(1500,800, windowTitle="MTZC", typeOfLayout ="grid", x=4,y=4)

# data_inst=pd.read_excel("./data/solutre_hex_inst.xlsx")
def constructPlateau():
    cases=myModel.newCellsOnGrid(21,21,"square",size=40,gap=0,backGroundImage=QPixmap("./icon/MTZC/plateau-jeu.jpg"))
    # Liste des coordonnées spécifiques à préserver
    cases_preservees = [
        (10,2), (11,2), (13,2), (9,3), (10,3), (11,3), (13,3), (14,3), (18,3),
        (9,4), (10,4), (12,5), (13,5), (14,5), (18,4), (19,4), (8,5), (10,5),
        (7,7), (8,5), (18,6), (19,6), (20,6), (21,5), (21,6),(7,6),(8,6),(9,6),(10,6), (10,7), (11,7),(12,7), (13,7),
        (12,6), (13,6), 
        (3,9)
    ]
    
    # Balayage de toutes les cases
    for x in range(1, 22):
        for y in range(1, 22):
            # On vérifie si les coordonnées actuelles ne sont pas dans la liste des cases à préserver
            if (x,y) not in cases_preservees:
                try:
                    cases.deleteEntity(cases.getEntity(x,y))
                except:
                    pass
    
    cases.setEntities("typeZH","vide")
    cases.setEntities("surface",1)
    cases.getEntity(11,2).setValue("surface",2)
    return cases

def constructZH1(): #ex. estran, ou marais doux
    aZH=myModel.newCellsOnGrid(2,3,"square",size=60,gap=2,name="ZH1",color=QColor.fromRgb(135,206,235))
    aZH.getEntity(1,1).setValue("action1","marche")
    aZH.getEntity(1,2).setValue("action1","observation")
    # aZH.defaultShapeColor = Qt.yellow
    return aZH
def constructZH2(): #ex. estran, ou marais doux
    aZH2=myModel.newCellsOnGrid(2,3,"square",size=60,gap=2,name="ZH1",color=Qt.green)
    aZH2.getEntity(1,1).setValue("action1","marche")
    aZH2.getEntity(1,2).setValue("action1","observation")
    # aZH.defaultShapeColor = Qt.yellow
    return aZH2
    
    

cases=constructPlateau()
pZH1=constructZH1()
# pZH2=constructZH2()



cases.newPov("vue normal","typeZH",{"vide":QColor(0,0,0,0), "zh1":QColor.fromRgb(176,224,230),"zh2":Qt.green})
cases.newBorderPovColorAndWidth("bords","surface", {1: [Qt.black,1], 2: [Qt.black,4]})
pZH1.newPov("vue normal","actions1",{"marche":Qt.blue,"observation":QColor.fromRgb(255,165,0)})
cases.displayBorderPov("vue normal")

DashBoardInd=myModel.newDashBoard("Suivi des indicateurs")
sequestration=myModel.newSimVariable("Sequestration",0)
economie=myModel.newSimVariable("Economie",0)
indSequestration=DashBoardInd.addIndicatorOnSimVariable(sequestration)
indEconomie=DashBoardInd.addIndicatorOnSimVariable(economie)


# Player1 = myModel.newPlayer("PlayerTest",attributesAndValues={"nbCubes":6})
# Player2 = myModel.newPlayer("PlayerTest2",attributesAndValues={"nbCubes":6})

# Touriste=myModel.newAgentSpecies("Touriste","squareAgent",defaultSize=40,defaultImage=QPixmap("./icon/solutre/touriste.png"))
# Bouteille=myModel.newAgentSpecies("Bouteille de vin conventionnel","ellipseAgent",defaultSize=20,defaultColor=Qt.magenta)
# Touriste.newAgentAtCoords(reserve)

# MoveHexagone=myModel.newMoveAction(Hexagones_test, 'infinite',feedback=[lambda aHex: execEffetInstantane(aHex),lambda aHex:updateCubes(aHex)])
# Player1.addGameAction(MoveHexagone)
# Player1ControlPanel = Player1.newControlPanel("Actions")

# GamePhase=myModel.timeManager.newGamePhase("Les joueurs peuvent jouer",[Player1,Player2])

# userSelector=myModel.newUserSelector()
# myModel.setCurrentPlayer("PlayerTest")
# Legend=myModel.newLegend(grid="combined")
Legend=myModel.newLegend('Type de zone humide à placer')

myModel.launch()
# myModel.launch_withMQTT("Instantaneous")
sys.exit(monApp.exec_())