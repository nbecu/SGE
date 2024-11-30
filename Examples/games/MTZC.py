import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
import random

monApp=QtWidgets.QApplication([])

myModel=SGModel(1500,900, name="MTZC", typeOfLayout ="grid", x=5,y=4)
    
#********************************************************************

nbJoueurs = 5
listeJoueurs = {
    'J1': Qt.blue,
    'J2': Qt.red,
    'J3': Qt.yellow,
    'J4':Qt.green,
    'J5':Qt.black,
    }

# # Définition des zones avec leurs caractéristiques
ZHs = {
    "marais doux": {##
        "sequestration": 0.25,
        "couleur": QColor(173, 216, 230, 120),
        "taille plateau":(2,2),
        "capacite accueil actions1":7,
        "cases actions2": [
            {"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1},
            {"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 2},
            {"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 2},
        ]
    },
    "marais saumatre": {##
        "sequestration": 1.51,
        "couleur": QColor(147, 112, 219, 120),
        "taille plateau":(2,3),
        "capacite accueil actions1":15,
        "cases actions2": [
            {"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1},
            {"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 2},
            {"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 2},
            *({"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 6 else {})
        ]
    },
    "marais salee": {##
        "sequestration": 1.51,
        "couleur": QColor(0, 255, 0, 120),
        "taille plateau":(2,2),
        "capacite accueil actions1": 10 if nbJoueurs <= 6 else (11 if nbJoueurs == 7 else 13),
        "cases actions2": [
            {"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1},
            *({"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 6 else {})
        ]
    },
    "oestricole": {##
        "sequestration": 1,
        "couleur": QColor(128, 128, 128, 120),
        "taille plateau":(2,3),
        "capacite accueil actions1":4,
        "cases actions2": [
            {"type_action2": "economie conchylicole", "effet sequestration": -1, "effet economie": 2},
            {"type_action2": "economie conchylicole", "effet sequestration": -1, "effet economie": 2},
            {"type_action2": "economie conchylicole", "effet sequestration": -1, "effet economie": 2},
            *({"type_action2": "economie conchylicole", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 6 else {}),
            *({"type_action2": "economie conchylicole", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 8 else {})
        ]
    },
    "vasiere nue": {##
        "sequestration": 0.4,
        "couleur": QColor(210, 180, 140, 120),
        "taille plateau":(2,4),
        "capacite accueil actions1":10,
        "cases actions2": [
            {"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1},
            {"type_action2": "navire", "effet sequestration": -1, "effet economie": 2},
            {"type_action2": "coquillage", "effet sequestration": 0, "effet economie": 2},
            *({"type_action2": "navire", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 6 else {}),
            *({"type_action2": "tourisme", "effet sequestration": -2, "effet economie": 2} if nbJoueurs >= 7 else {}),
            *({"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1} if nbJoueurs >= 8 else {})
        ]
    },
    "demi-herbier": {##
        "sequestration": 0.9,
        "couleur": QColor(130, 180, 100, 120)
    },
    "herbier": {##
        "sequestration": 1.4,
        "couleur": QColor(0, 128, 0, 120),
        "taille plateau":(2,4),
        "capacite accueil actions1":10,
        "cases actions2": [
            {"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1},
            {"type_action2": "coquillage", "effet sequestration": 0, "effet economie": 2},
            {"type_action2": "navire", "effet sequestration": -1, "effet economie": 2},
            *({"type_action2": "navire", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 6 else {}),
            *({"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 7 else {}),
            *({"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1} if nbJoueurs >= 8 else {})
        ]
    },
    "champs agricoles": { ##
        "sequestration": 0.05,
        "couleur": QColor(255, 0, 0, 120),
        "taille plateau":(2,3),
        "capacite accueil actions1":None,
        "cases actions2": [
            {"type_action2": "agri intensive", "effet sequestration": -1, "effet economie": 3},
            {"type_action2": "agri bio", "effet sequestration": 1, "effet economie": 1},
            {"type_action2": "grande culture", "effet sequestration": 0, "effet economie": 1},
            {"type_action2": "apiculture", "effet sequestration": 0, "effet economie": 1},
            {"type_action2": "bovin", "effet sequestration": -1, "effet economie": 2},
            {"type_action2": "ovin", "effet sequestration": -1, "effet economie": 2}
        ]
    },
  
    "plage": {##
        "sequestration": 0,
        "couleur": QColor(255, 218, 185, 120),
        "taille plateau":(2,3),
        "capacite accueil actions1":13,
        "cases actions2": [
            {"type_action2": "toursime", "effet sequestration": -1, "effet economie": 3},
            {"type_action2": "toursime", "effet sequestration": -1, "effet economie": 3},
            {"type_action2": "toursime", "effet sequestration": -1, "effet economie": 3},
            *({"type_action2": "toursime", "effet sequestration": -1, "effet economie": 3} if nbJoueurs >= 6 else {}),
            *({"type_action2": "toursime", "effet sequestration": -1, "effet economie": 3} if nbJoueurs >= 7 else {})
        ]
    },
    "port industriel": {##
        "sequestration": 0,
        "couleur": QColor(0, 100, 0, 120),
        "taille plateau":(2,3),
        "capacite accueil actions1":None,
        "cases actions2": [
            {"type_action2": "industrie portuaire", "effet sequestration": -1, "effet economie": 3},
            {"type_action2": "industrie portuaire", "effet sequestration": -1, "effet economie": 3},
            {"type_action2": "industrie portuaire", "effet sequestration": -1, "effet economie": 3},
            {"type_action2": "industrie portuaire", "effet sequestration": -1, "effet economie": 3},
            *({"type_action2": "industrie portuaire", "effet sequestration": -1, "effet economie": 3} if nbJoueurs >= 7 else {}),
            *({"type_action2": "industrie portuaire", "effet sequestration": -1, "effet economie": 3} if nbJoueurs >= 8 else {})
        ]
    },
    "pres sales": {##
        "sequestration": 2.4,
        "couleur": QColor(70, 110, 70, 120),
        "taille plateau":(2,4),
        "capacite accueil actions1":5,
        "cases actions2": [
           {"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1},
           {"type_action2": "grande culture", "effet sequestration": -1, "effet economie": 1},
           {"type_action2": "ovin", "effet sequestration": 1, "effet economie": 1},
           *({"type_action2": "ovin", "effet sequestration": 1, "effet economie": 1} if nbJoueurs >= 6 else {}),
           *({"type_action2": "ovin", "effet sequestration": 1, "effet economie": 1} if nbJoueurs >= 7 else {}),
           *({"type_action2": "tourisme", "effet sequestration": -2, "effet economie": 2} if nbJoueurs >= 8 else {})
        ]
    },
    "marais doux agricole": {##
        "sequestration": 0.1,
        "couleur": QColor(139, 69, 19, 120),
        "taille plateau":(2,4),
        "capacite accueil actions1":9,
        "cases actions2": [
            {"type_action2": "agri intensive", "effet sequestration": -1, "effet economie": 3},
            {"type_action2": "agri bio", "effet sequestration": 0, "effet economie": 1},
            {"type_action2": "grande culture", "effet sequestration": 0, "effet economie": 0},
            {"type_action2": "apiculture", "effet sequestration": 0, "effet economie": 1},
            {"type_action2": "bovin", "effet sequestration": -1, "effet economie": 2},
            {"type_action2": "ovin", "effet sequestration": -1, "effet economie": 2}
        ]
    },
    "port plaisance": {##
        "sequestration": 0,
        "couleur": QColor(0, 100, 0, 120),
        "taille plateau":(2,5),
        "capacite accueil actions1":16,
        "cases actions2": [
            {"type_action2": "economie portuaire", "effet sequestration": -1, "effet economie": 2},
            {"type_action2": "plaisance", "effet sequestration": -1, "effet economie": 1},
            {"type_action2": "plaisance", "effet sequestration": -1, "effet economie": 1},
            {"type_action2": "plaisance", "effet sequestration": -1, "effet economie": 1},
            {"type_action2": "plaisance", "effet sequestration": -1, "effet economie": 1},
            {"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 3},
            {"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 3},
            *({"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 3} if nbJoueurs >= 7 else {}),
            *({"type_action2": "plaisance", "effet sequestration": -1, "effet economie": 1} if nbJoueurs >= 8 else {})
        ]
    },
     "foret": {##
        "sequestration": 0,
        "couleur": QColor(0, 100, 0, 120),
        "taille plateau":(2,2),
        "capacite accueil actions1":15,
        "cases actions2": [
            {"type_action2": "coupe arbres", "effet sequestration": -1, "effet economie": 1},
            {"type_action2": "coupe arbres", "effet sequestration": -1, "effet economie": 1},
            *({"type_action2": "coupe arbres", "effet sequestration": -1, "effet economie": 1} if nbJoueurs >= 7 else {})
        ]
    },    
    "mer": {##
        "sequestration": 0.004,
        "couleur": QColor(0, 0, 255, 120)
    },
    "vide": {##
        "sequestration": 0,
        "couleur": QColor(0, 0, 0, 0)
    }
}

# Dictionnaire des images d'actions2
images_action2 = {
    "recherche": 'loupe.png',
    "tourisme": 'valise.png',
    "economie conchylicole": 'huitre.png',
    "navire": 'porte-conteneur.png',
    "coquillage": 'huitre.png',
    "agri intensive": 'tracteur.png',
    "agri bio": 'agribio.png',
    "grande culture": 'grande-culture.png',
    "apiculture": 'apiculture.png',
    "bovin": 'bovin.png',
    "ovin": 'ovin.png',
    "toursime": 'valise.png',
    "industrie portuaire": 'porte-conteneur.png',
    "coupe arbres": 'coupe-arbres.png',
    "plaisance":'voilier.png',
    "economie portuaire":'porte-conteneur.png',
}

# Accès aux valeurs
t0 = "vide"
tD = "marais doux"
tDA = "marais doux agricole"
tSAU = "marais saumatre"
tSAL = "marais salee"
tO = "oestricole"
tPS = "pres sales"
tV = "vasiere nue"
tH2 = "demi-herbier"
tH = "herbier"
tA = "champs agricoles"
tM = "mer"
tP = "plage"

# Exemple d'accès aux valeurs
sequestration_vide = ZHs[t0]["sequestration"]
couleur_vide = ZHs[t0]["couleur"]
sequestration_marais_doux = ZHs[tD]["sequestration"]
couleur_marais_doux = ZHs[tD]["couleur"]

#********************************************************************
# surface  des petites cases sPC ett des grandes cases SGC
sPC = 2
sGC = 4

# construction du plateau
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

dicoCouleurs = {zh: infos["couleur"] for zh, infos in ZHs.items()}
cases.newPov("vue normale","typeZH",dicoCouleurs)
cases.newBorderPovColorAndWidth("bords","surface", {2: [Qt.black,1], 4: [Qt.black,4]})
cases.displayBorderPov("bords")


#********************************************************************
# construct plateaux des zones humides 


# Construction automatique du nouveau dictionnaire avec QPixmap
images_action2_qpixmap = {key: QPixmap(f"./icon/MTZC/{value}") for key, value in images_action2.items()}
dictSymbology = {
    "action1": Qt.gray,
    "action2": QColor(255, 165, 0, 250),
    "vide": Qt.transparent,
    **images_action2_qpixmap  
}
# méthode générique pour la construction d'un plateau ZH
casesAction1 =[]
def constructZH(typeZH, coords=None): #typeZH est le nom de la ZH (ex. vasiere ou marais doux)
    pZH[typeZH]=myModel.newCellsOnGrid(ZHs[typeZH]["taille plateau"][0],ZHs[typeZH]["taille plateau"][1],"square",size=40,gap=2,name="typeZH",color=ZHs[typeZH]["couleur"])
    pZH[typeZH].setEntities('capacite accueil',0)
    pZH[typeZH].setEntities('type',"vide")
    pZH[typeZH].setEntities('vue normale',"vide")
    if ZHs[typeZH]["capacite accueil actions1"] is None:
        startCasesActions2 = 1
    else:
        startCasesActions2 = 2
        case1= pZH[typeZH].getEntity(1,1)
        casesAction1.append(case1)
        case1.setValue('type','action1')
        case1.setValue('vue normale',"action1")
        case1.setValue('capacite accueil',ZHs[typeZH]["capacite accueil actions1"])

    for i, paramCaseAction2 in enumerate(ZHs[typeZH]["cases actions2"], start=startCasesActions2):
        caseX = pZH[typeZH].getEntity(i)
        caseX.setValue("type", "action2")
        caseX.setValue("vue normale", "action2")
        for aParam, aValue in paramCaseAction2.items():
            caseX.setValue(aParam, aValue)
            if aParam == "type_action2":
                caseX.setValue("vue normale", aValue)
    
    pZH[typeZH].newPov("vue normale", "vue normale", dictSymbology)  
    pZH[typeZH].newBorderPovColorAndWidth("bords", "type", {"action1": [Qt.black,1], "action2": [Qt.black,1], "vide": [Qt.transparent,0]})
    pZH[typeZH].displayBorderPov("bords")
  

    if coords != None : pZH[typeZH].grid.moveToCoords(coords)

    return pZH[typeZH]

# les plateaux des ZH sont stockés dans le dico pZH{)
pZH={}
posX = 1150
posY = 30
for i, aZHtype in enumerate(ZHs.keys()):
    if aZHtype in ["vide", "mer", "demi-herbier"]: continue
    if i in [7,13]: posY +=40 # permet de prendre en compte la taille plus grande des plateaux de la ligne précédente    
    myModel.newLabel_stylised(aZHtype,(posX+5,posY-2), size=10)
    constructZH(aZHtype, (posX, posY))
    posX += 100  # Incrémentation de posX
    # Vérification si posX dépasse 1450
    if posX > 1400:
        posX = 1150  # Réinitialisation de posX
        posY += 150  # Incrémentation de posY

#********************************************************************
# variables de simulation

sequestration=myModel.newSimVariable("Sequestration",0)
economie=myModel.newSimVariable("Economie",0)

#********************************************************************
# Definiion des actions de jeu

Player = myModel.newPlayer("Player")

for aZH in ZHs.keys():
    Player.addGameAction(myModel.newModifyAction(cases, {"typeZH":aZH},feedbacks=[lambda : updateJauges()]))

nbPionActions1_parJoueur=20
pionAction1=myModel.newAgentSpecies("Action1","circleAgent",defaultSize=5,)
pionAction1.newPov("joueur","joueur",listeJoueurs)

for jX in list(listeJoueurs.keys()):
    nomJ =""+jX
    Player.addGameAction(myModel.newCreateAction(pionAction1, {"joueur":nomJ},nbPionActions1_parJoueur,
                            conditions=[
                                    lambda aCell: aCell.classDef != cases and aCell.value('type') == 'action1',
                                    lambda aCell: aCell.nbAgents() < aCell.value('capacite accueil'),
                                    ],
                            feedbacks=[lambda : updateActions1()]))


nbPionActions2_parJoueur=6
pionAction2=myModel.newAgentSpecies("Action2","squareAgent",defaultSize=20,locationInEntity='center')
pionAction2.newPov("joueur","joueur",listeJoueurs)

for jX in list(listeJoueurs.keys()):
    nomJ =""+jX
    Player.addGameAction(myModel.newCreateAction(pionAction2, {"joueur":nomJ},nbPionActions2_parJoueur,
                            conditions=[
                                    lambda aCell: aCell.classDef != cases and aCell.value('type') == 'action2',
                                    lambda aCell: aCell.isEmpty(),
                                    ],
                            feedbacks=[lambda : updateActions2()]))

#********************************************************************
def updateJauges():
    totSequest = 0
    for aCase in cases.getEntities():
        valeur = ZHs[aCase.getValue('typeZH')]["sequestration"]  # 0 si la clé n'est pas trouvée
        sequestCase  = valeur * aCase.getValue('surface')
        totSequest += sequestCase
    sequestration.setValue(round(totSequest,1))  # Arrondi à l'unité

def updateActions1():
    ### ATTENTION pour l'instant c'est execute à chaque pose de pion, alors que ca doit ettre executé uniquement a fin de la phase de jeu
    for aCase in casesAction1:
        if aCase.nbAgents() > aCase.value('capacite accueil'):
            effetSequestration = random.randint(10, 20)
            sequestration.decValue(effetSequestration)

def updateActions2():
    ### ATTENTION pour l'instant c'est execute à chaque pose de pion, alors que ca doit ettre executé uniquement a fin de la phase de jeu
    totSequ = 0
    totEco = 0
    for aPion in pionAction2.getEntities():
        totSequ += aPion.cell.value("effet sequestration")
        totEco += aPion.cell.value("effet economie")
    sequestration.incValue(round(totSequ))
    economie.incValue(round(totEco))

#********************************************************************

PlayerControlPanel = Player.newControlPanel("Actions")
PlayerControlPanel.moveToCoords(882,30)

myModel.setCurrentPlayer("Player")

#********************************************************************

GamePhase=myModel.timeManager.newGamePhase("Jouer",[Player])
myModel.displayTimeInWindowTitle()

#********************************************************************

# userSelector=myModel.newUserSelector()
# Legend=myModel.newLegend(grid="combined")

#********************************************************************
DashBoardInd=myModel.newDashBoard("Suivi des indicateurs")
DashBoardInd.moveToCoords(882,715)
indSequestration=DashBoardInd.addIndicatorOnSimVariable(sequestration)
indEconomie=DashBoardInd.addIndicatorOnSimVariable(economie)

#********************************************************************
updateJauges()


#********************************************************************
myModel.launch()
# myModel.launch_withMQTT("Instantaneous")
sys.exit(monApp.exec_())