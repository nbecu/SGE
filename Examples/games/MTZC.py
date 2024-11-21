import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
import random

monApp=QtWidgets.QApplication([])

myModel=SGModel(1500,900, windowTitle="MTZC", typeOfLayout ="grid", x=4,y=4)

sPC = 2
sGC = 4
    
# Définition des zones avec leurs caractéristiques
ZHs = {
    "marais doux": {
        "sequestration": 0.25,
        "couleur": QColor(173, 216, 230, 120)
    },
    "marais doux agricole": {
        "sequestration": 0.1,
        "couleur": QColor(139, 69, 19, 120)
    },
    "marais saumatre": {
        "sequestration": 1.51,
        "couleur": QColor(147, 112, 219, 120)
    },
    "marais sale": {
        "sequestration": 1.51,
        "couleur": QColor(0, 255, 0, 120)
    },
    "oestricole": {
        "sequestration": 1,  # à vérifier
        "couleur": QColor(128, 128, 128, 120)
    },
    "pres sales": {
        "sequestration": 2.4,
        "couleur": QColor(70, 110, 70, 120)
    },
    "vasiere nue": {
        "sequestration": 0.4,
        "couleur": QColor(210, 180, 140, 120)
    },
    "demi-herbier": {
        "sequestration": 0.9,  # moitié zoostère, moitié vasière nue
        "couleur": QColor(130, 180, 100, 120)
    },
    "herbier": {
        "sequestration": 1.4,
        "couleur": QColor(0, 128, 0, 120)
    },
    "prairie agricole": {
        "sequestration": 0.05,  # à vérifier
        "couleur": QColor(255, 0, 0, 120)
    },
    "mer": {
        "sequestration": 0.004,
        "couleur": QColor(0, 0, 255, 120)
    },
    "plage": {
        "sequestration": 0,
        "couleur": QColor(255, 218, 185, 120)
    },
    "vide": {
        "sequestration": 0,
        "couleur": QColor(0, 0, 0, 0)
    },
}

# Accès aux valeurs
t0 = "vide"
tD = "marais doux"
tDA = "marais doux agricole"
tSAU = "marais saumatre"
tSAL = "marais sale"
tO = "oestricole"
tPS = "pres sales"
tV = "vasiere nue"
tH2 = "demi-herbier"
tH = "herbier"
tA = "prairie agricole"
tM = "mer"
tP = "plage"

# Exemple d'accès aux valeurs
sequestration_vide = ZHs[t0]["sequestration"]
couleur_vide = ZHs[t0]["couleur"]

sequestration_marais_doux = ZHs[tD]["sequestration"]
couleur_marais_doux = ZHs[tD]["couleur"]

def constructPlateau():
    cases=myModel.newCellsOnGrid(21,21,"square",size=40,gap=0,backGroundImage=QPixmap("./icon/MTZC/plateau-jeu.jpg"))
    # Liste des coordonnées spécifiques à préserver avec leur valeur de surface
    cases_preservees = {
        (10,2): [sPC, tH2], (11,2): [sGC, tPS], (13,2): [sGC, tA],
        (9,3): [sPC, tH2], (10,3): [sGC, tV], (11,3): [sPC, tPS], (13,3): [sGC, tA], (14,3): [sGC, tA],          (18,3): [sPC, tA],
        (9,4): [sPC, tPS], (10,4): [sPC, tPS],                                          (18,4): [sGC, tA], (19,4): [sGC, tA],
        (8,5): [sPC, tSAL],   (10,5): [sGC, tSAU],       (12,5): [sPC, tSAU], (13,5): [sGC, tSAU], (14,5): [sPC, tSAU],                                                                                                                                                    (21,5): [sPC, tA],
        (7,6): [sPC, tP], (8,6): [sPC, tO], (9,6): [sPC, tO],     (10,6): [sPC, tSAU],         (12,6): [sPC, tA], (13,6): [sPC, tA],                                                                                           (18,6): [sGC, tA], (19,6): [sPC, tA], (20,6): [sGC, tA], (21,6): [sPC, tA],        
        (7,7): [sPC, tP],  (10,7): [sPC, tSAU], (11,7): [sPC, tA], (12,7): [sPC, tA], (13,7): [sPC, tA], 
        (3,8): [sPC, tH2], (4,8): [sPC, tV], (5,8): [sPC, tV],          (7,8): [sPC, tDA],
        (2,9): [sPC, tV],                                           (6,9): [sPC, tA], (7,9): [sPC, tDA], (8,9): [sPC, tDA],  (9,9): [sGC, tDA], (10,9): [sGC, tDA], (11,9): [sGC, tDA],                                                     (19,9): [sPC, tA], (20,9): [sPC, tA],  
        (2,10): [sPC, tV],                                                                          (7,10): [sPC, tDA], (8,10): [sPC, tDA], (9,10): [sGC, tDA], (10,10): [sGC, tDA], (11,10): [sGC, tDA],                                       (18,10): [sPC, tA], (19,10): [sPC, tA], (20,10): [sGC, tA],  
        (4,11): [sPC, t0], (5,11): [sGC, t0],                                                                         (8,11): [sPC, tDA], (9,11): [sGC, tDA], (10,11): [sGC, tDA], (11,11): [sGC, tDA], (12,11): [sGC, tDA], (13,11): [sGC, tDA],         (16,11): [sPC, tA], (17,11): [sGC, tA], (18,11): [sGC, tA], (19,11): [sGC, tA], (20,11): [sGC, tA],  
                                                                                                                                                               (10,12): [sPC, tDA], (11,12): [sPC, tDA], (12,12): [sPC, tDA],                    (16,12): [sPC, tA], (17,12): [sPC, tA], (18,12): [sGC, tA], (19,12): [sGC, tA], (20,12): [sGC, tA],  
                                                                                                                                                                                                                                                                                               (19,13): [sGC, tA], 
                         (4,15): [sPC, tO], (5,15): [sPC, tO], 
        (3,18): [sPC, tP], 
        (3,19): [sGC, tP],
                         (4,20): [sPC, tSAU], (5,20): [sGC, tSAU],                                 (9,20): [sGC, t0],       (12,20): [sPC, tD], (13,20): [sPC, tD],    (16,20): [sPC, tD], (17,20): [sPC, tD],
        (3,21): [sGC, tSAU], (4,21): [sGC, tSAU], (5,21): [sGC, tSAU], (6,21): [sGC, tSAU],        (9,21): [sGC, t0],                                              (17,21): [sPC, tD], (18,21): [sGC, tD], (19,21): [sGC, tD],

    }
    # Balayage de toutes les cases
    for aCase in cases.getEntities():
        if (aCase.xPos,aCase.yPos) in cases_preservees:
            aCase.setValue("surface", cases_preservees[(aCase.xPos, aCase.yPos)][0])  # Définir la valeur de surface
            aCase.setValue("typeZH", cases_preservees[(aCase.xPos, aCase.yPos)][1])  # Définir la valeur de TYPEzh
        else:
            try:
                cases.deleteEntity(aCase)
            except:
                pass
    # cases.setEntities("typeZH","vide")
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
dicoCouleurs = {zh: infos["couleur"] for zh, infos in ZHs.items()}
cases.newPov("vue normal","typeZH",dicoCouleurs)
cases.newBorderPovColorAndWidth("bords","surface", {2: [Qt.black,1], 4: [Qt.black,4]})
cases.displayBorderPov("bords")

pZH1=constructZH1()
# pZH2=constructZH2()
pZH1.newPov("vue normal","actions1",{"marche":Qt.blue,"observation":QColor.fromRgb(255,165,0)})

pionAction1=myModel.newAgentSpecies("Action1","circleAgent",{'joueur':{'J1','J2','J3','J4'}},defaultSize=10,)
pionAction1.newPov("joueur","joueur",{'J1': Qt.blue, 'J2': Qt.red, 'J3': Qt.yellow, 'J4':Qt.green})



sequestration=myModel.newSimVariable("Sequestration",0)
economie=myModel.newSimVariable("Economie",0)


Player = myModel.newPlayer("Player")
# pionAction1=myModel.newAgentSpecies("Action1","circleAgent",defaultSize=40,defaultImage=QPixmap("./icon/solutre/touriste.png"))
# Bouteille=myModel.newAgentSpecies("Bouteille de vin conventionnel","ellipseAgent",defaultSize=20,defaultColor=Qt.magenta)
# Touriste.newAgentAtCoords(reserve)

# MoveHexagone=myModel.newMoveAction(Hexagones_test, 'infinite',feedback=[lambda aHex: execEffetInstantane(aHex),lambda aHex:updateCubes(aHex)])

# zh1Action=myModel.newModifyAction(cases, {"typeZH":"marais doux"},feedback=[lambda : updateJauges()])
# Player.addGameAction(zh1Action)
for aZH in ZHs.keys():
    Player.addGameAction(myModel.newModifyAction(cases, {"typeZH":aZH},feedback=[lambda : updateJauges()]))
# Player.addGameAction(myModel.newModifyAction(cases, {"typeZH":"vide"},feedback=[lambda : updateJauges()]))

Player.addGameAction(myModel.newCreateAction(pionAction1, {"joueur":'J1'}, listOfRestriction=[lambda : pionAction1.nb_withValue("joueur",'J1') < 12, lambda aCell: aCell.classDef != cases], feedback=[lambda : updateActions1()]))
Player.addGameAction(myModel.newCreateAction(pionAction1, {"joueur":'J2'}, listOfRestriction=[lambda : pionAction1.nb_withValue("joueur",'J2') < 12, lambda aCell: aCell.classDef != cases], feedback=[lambda : updateActions1()]))
Player.addGameAction(myModel.newCreateAction(pionAction1, {"joueur":'J3'}, listOfRestriction=[lambda : pionAction1.nb_withValue("joueur",'J3') < 12, lambda aCell: aCell.classDef != cases], feedback=[lambda : updateActions1()]))
Player.addGameAction(myModel.newCreateAction(pionAction1, {"joueur":'J4'}, listOfRestriction=[lambda : pionAction1.nb_withValue("joueur",'J4') < 12, lambda aCell: aCell.classDef != cases], feedback=[lambda : updateActions1()]))


def updateJauges():
    totSequest = 0
    totEco = 0
    
    for aCase in cases.getEntities():
        valeur = ZHs[aCase.getValue('typeZH')]["sequestration"]  # 0 si la clé n'est pas trouvée
        sequestCase  = valeur * aCase.getValue('surface')
        totSequest += sequestCase
    sequestration.setValue(round(totSequest,1))  # Arrondi à l'unité

def updateActions1():
    totEco = 0
    
    for aPion in pionAction1.getEntities():
        valeur = random.randint(1, 3)
        totEco  += valeur
    economie.setValue(round(totEco))


Player1ControlPanel = Player.newControlPanel("Actions")

GamePhase=myModel.timeManager.newGamePhase("Jouer",[Player])

# userSelector=myModel.newUserSelector()
myModel.setCurrentPlayer("Player")
# Legend=myModel.newLegend(grid="combined")

DashBoardInd=myModel.newDashBoard("Suivi des indicateurs")
indSequestration=DashBoardInd.addIndicatorOnSimVariable(sequestration)
indEconomie=DashBoardInd.addIndicatorOnSimVariable(economie)

# Legend=myModel.newLegend('Type de zone humide à placer')

updateJauges()

myModel.launch()
# myModel.launch_withMQTT("Instantaneous")
sys.exit(monApp.exec_())