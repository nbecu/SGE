import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
import random

monApp=QtWidgets.QApplication([])

myModel=SGModel(1700,910, name="MTZC", typeOfLayout ="grid", x=5,y=4)
    
#********************************************************************

nbJoueurs = 5
listeJoueurs = {
    'J1': Qt.blue,
    'J2': Qt.red,
    'J3': Qt.yellow,
    'J4':Qt.green,
    'J5':Qt.white,
    }

#OLD(initial)  ordreZHs = ['marais doux', 'marais saumatre', 'marais salee', 'oestricole', 'vasiere nue',  'herbier', 'champs agricoles', 'plage', 'port industriel', 'pres sales', 'marais doux agricole', 'port plaisance', 'foret', 'marais salant',]
ordreZHs = ['champs agricoles','marais doux agricole', 'marais doux', 'marais saumatre', 'marais salee', 'oestricole', 'marais salant', 'pres sales', 'vasiere nue', 'herbier', "demi-herbier", 'plage', 'port plaisance', 'port industriel', 'foret', "mer", "vide"]

# # Définition des zones avec leurs caractéristiques
ZHs = {
    'champs agricoles': {##
        "sequestration": 0,
        "couleur": QColor(255, 0, 0, 120),
        "potentiel accueil actions1": None,
        "cases actions2": [
            {"type_action2": "agri intensive", "effet sequestration": -1, "effet economie": 3},
            {"type_action2": "agri intensive", "effet sequestration": -1, "effet economie": 3},
            {"type_action2": "agri extensive", "effet sequestration": 1, "effet economie": 1},
            {"type_action2": "agri extensive", "effet sequestration": 1, "effet economie": 1},
            {"type_action2": "fauchage", "effet sequestration": 0, "effet economie": 1},
            {"type_action2": "bovin", "effet sequestration": -1, "effet economie": 2},
            {"type_action2": "ovin", "effet sequestration": -1, "effet economie": 2},
            {"type_action2": "apiculture", "effet sequestration": 0, "effet economie": 1},
            *({"type_action2": "bovin", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 7 else {}),
            *({"type_action2": "ovin", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 8 else {})
        ]
    },
    'marais doux agricole': {##
        "sequestration": 0.1,
        "couleur": QColor(139, 69, 19, 120),
        "potentiel accueil actions1": {5: 7, 6: 8, 7: 9, 8: 10}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "agri intensive", "effet sequestration": -1, "effet economie": 3},
            {"type_action2": "agri intensive", "effet sequestration": -1, "effet economie": 3},
            {"type_action2": "agri extensive", "effet sequestration": 0, "effet economie": 1},
            {"type_action2": "agri extensive", "effet sequestration": 0, "effet economie": 1},
            {"type_action2": "fauchage", "effet sequestration": 0, "effet economie": 0},
            {"type_action2": "bovin", "effet sequestration": -1, "effet economie": 2},
            {"type_action2": "ovin", "effet sequestration": -1, "effet economie": 2},
            *({"type_action2": "apiculture", "effet sequestration": 0, "effet economie": 1} if nbJoueurs >= 6 else {}),
            *({"type_action2": "bovin", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 7 else {}),
            *({"type_action2": "ovin", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 8 else {})
        ]
    },
    'marais doux': {##
        "sequestration": 0.25,
        "couleur": QColor(100, 149, 237, 120), 
        "potentiel accueil actions1": {5: 15, 6: 18, 7: 21, 8: 24}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1},
            {"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 2},
            {"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 2},
        ]
    },
    'marais saumatre': {##
        "sequestration": 1.51,
        "couleur": QColor(137, 56, 173, 150), # QColor(128, 0, 128, 150),#QColor(147, 112, 219, 150),
        "potentiel accueil actions1": {5: 15, 6: 17, 7: 19, 8: 21}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1},
            {"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 2},
            {"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 2},
            *({"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 6 else {})
        ]
    },
    'marais salee': {##
        "sequestration": 1.75,
        "couleur": QColor(100, 200, 180, 150), #QColor(0, 255, 0, 120),
        "potentiel accueil actions1": 5 if nbJoueurs <= 6 else (6 if nbJoueurs == 7 else 7),  # TODO PROBLEME. Y' a pas de valeurs.
        "cases actions2": [
            {"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1},
            *({"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 6 else {})
        ]
    },
    'oestricole': {##
        "sequestration": 1,
        "couleur": QColor(192, 192, 192, 120), #QColor(128, 128, 128, 120),
        "potentiel accueil actions1": {5: 4, 6: 5, 7: 6, 8: 7}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "economie conchylicole", "effet sequestration": -1, "effet economie": 2},
            {"type_action2": "economie conchylicole", "effet sequestration": -1, "effet economie": 2},
            {"type_action2": "economie conchylicole", "effet sequestration": -1, "effet economie": 2},
            *({"type_action2": "economie conchylicole", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 6 else {}),
            *({"type_action2": "economie conchylicole", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 8 else {})
        ]
    },
    'marais salant': {##
        "sequestration": 1.2,  # moins que maree salée (1.75), mais plus que oestricole (1)
        "couleur": QColor(255, 255, 255, 200),
        "potentiel accueil actions1": 5 if nbJoueurs <= 6 else (6 if nbJoueurs == 7 else 7),  # TODO PROBLEME. Y' a pas de valeurs
        "cases actions2": [
            {"type_action2": "saliculture", "effet sequestration": 0, "effet economie": 1},
            {"type_action2": "saliculture", "effet sequestration": 0, "effet economie": 1},
            {"type_action2": "saliculture", "effet sequestration": 0, "effet economie": 1},
            {"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 2},
            *({"type_action2": "saliculture", "effet sequestration": 0, "effet economie": 1} if nbJoueurs >= 6 else {}),
        ]
    },
    'pres sales': {##
        "sequestration": 2.4,
        "couleur":QColor(0, 128, 0, 140), #QColor(70, 110, 70, 120),
        "potentiel accueil actions1": {5: 8, 6: 10, 7: 13, 8: 15}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1},
            {"type_action2": "fauchage", "effet sequestration": -1, "effet economie": 1},
            {"type_action2": "ovin", "effet sequestration": 1, "effet economie": 1},
            *({"type_action2": "ovin", "effet sequestration": 1, "effet economie": 1} if nbJoueurs >= 6 else {}),
            *({"type_action2": "ovin", "effet sequestration": 1, "effet economie": 1} if nbJoueurs >= 7 else {}),
            *({"type_action2": "tourisme", "effet sequestration": -2, "effet economie": 2} if nbJoueurs >= 8 else {})
        ]
    },
    'vasiere nue': {##
        "sequestration": 0.25,
        "couleur":  QColor(180, 150, 100, 140), #QColor(210, 180, 140, 120),
        "potentiel accueil actions1": {5: 14, 6: 17, 7: 20, 8: 23}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1},
            {"type_action2": "navire", "effet sequestration": -1, "effet economie": 2},
            {"type_action2": "coquillage", "effet sequestration": 0, "effet economie": 2},
            *({"type_action2": "navire", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 6 else {}),
            *({"type_action2": "tourisme", "effet sequestration": -2, "effet economie": 2} if nbJoueurs >= 7 else {}),
            *({"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1} if nbJoueurs >= 8 else {})
        ]
    },
    # "vasiere nue bai de diop": {##
    #     "sequestration": 7,9,
    #     "couleur": QColor(210, 180, 140, 120),
    #     "potentiel accueil actions1":10,
    #     "cases actions2": [
    #         {"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1},
    #         {"type_action2": "navire", "effet sequestration": -1, "effet economie": 2},
    #         {"type_action2": "coquillage", "effet sequestration": 0, "effet economie": 2},
    #         *({"type_action2": "navire", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 6 else {}),
    #         *({"type_action2": "tourisme", "effet sequestration": -2, "effet economie": 2} if nbJoueurs >= 7 else {}),
    #         *({"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1} if nbJoueurs >= 8 else {})
    #     ]
    # },
    "demi-herbier": {##
        "sequestration": 0.83, #moitié herbier, moitié vasière nue,
        "couleur": QColor(0, 255, 0, 50), #QColor(130, 180, 100, 120)
    },
    'herbier': {##
        "sequestration": 1.4,
        "couleur": QColor(0, 255, 0, 150), #QColor(0, 128, 0, 120),
        "potentiel accueil actions1": {5: 9, 6: 11, 7: 13, 8: 15}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1},
            {"type_action2": "coquillage", "effet sequestration": 0, "effet economie": 2},
            {"type_action2": "navire", "effet sequestration": -1, "effet economie": 2},
            *({"type_action2": "navire", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 6 else {}),
            *({"type_action2": "tourisme", "effet sequestration": -1, "effet economie": 2} if nbJoueurs >= 7 else {}),
            *({"type_action2": "recherche", "effet sequestration": 1, "effet economie": 1} if nbJoueurs >= 8 else {})
        ]
    },
    'plage': {##
        "sequestration": 0,
        "couleur": QColor(255, 255, 130, 180), # QColor(255, 240, 200, 170), # QColor(255, 218, 185, 120),
        "potentiel accueil actions1": {5: 14, 6: 16, 7: 18, 8: 20}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "toursime", "effet sequestration": -1, "effet economie": 3},
            {"type_action2": "toursime", "effet sequestration": -1, "effet economie": 3},
            {"type_action2": "toursime", "effet sequestration": -1, "effet economie": 3},
            *({"type_action2": "toursime", "effet sequestration": -1, "effet economie": 3} if nbJoueurs >= 6 else {}),
            *({"type_action2": "toursime", "effet sequestration": -1, "effet economie": 3} if nbJoueurs >= 7 else {})
        ]
    },
    'port plaisance': {##
        "sequestration": 0,
        "couleur": QColor(30, 30, 90, 120), # QColor(50, 50, 130, 120), 
        "potentiel accueil actions1": {5: 11, 6: 13, 7: 15, 8: 17}[nbJoueurs],
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
    'port industriel': {##
        "sequestration": 0,
        "couleur": QColor(40, 40, 40, 180),  
        "potentiel accueil actions1": None,
        "cases actions2": [
            {"type_action2": "industrie portuaire", "effet sequestration": -2, "effet economie": 6},
            {"type_action2": "industrie portuaire", "effet sequestration": -2, "effet economie": 6},
            {"type_action2": "industrie portuaire", "effet sequestration": -2, "effet economie": 6},
            {"type_action2": "industrie portuaire", "effet sequestration": -2, "effet economie": 6},
            *({"type_action2": "industrie portuaire", "effet sequestration": -2, "effet economie": 6} if nbJoueurs >= 7 else {}),
            *({"type_action2": "industrie portuaire", "effet sequestration": -2, "effet economie": 6} if nbJoueurs >= 8 else {})
        ]
    },
    'foret': {##
        "sequestration": 0,
        "couleur": QColor(0, 100, 0, 200), #QColor(0, 100, 0, 120),
        "potentiel accueil actions1": {5: 13, 6: 15, 7: 17, 8: 19}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "coupe arbres", "effet sequestration": -1, "effet economie": 1},
            {"type_action2": "coupe arbres", "effet sequestration": -1, "effet economie": 1},
            *({"type_action2": "coupe arbres", "effet sequestration": -1, "effet economie": 1} if nbJoueurs >= 7 else {})
        ]
    },
    'mer': {##
        "sequestration": 0.004,
        "couleur": QColor(0, 0, 255, 120)
    },
    'vide': {##
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
    "agri extensive": 'agribio.png',
    "fauchage": 'grande-culture.png',
    "apiculture": 'apiculture.png',
    "bovin": 'bovin.png',
    "ovin": 'ovin.png',
    "toursime": 'valise.png',
    "industrie portuaire": 'porte-conteneur.png',
    "coupe arbres": 'coupe-arbres.png',
    "plaisance":'voilier.png',
    "economie portuaire":'porte-conteneur.png',
    "saliculture":'etelle.png'
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
                       (8,5): [sPC, tO],                   (10,5): [sGC, tSAU],        (12,5): [sPC, tSAU], (13,5): [sGC, tSAU], (14,5): [sPC, tSAU],                                                                                                                           (21,5): [sPC, tA],
    (7,6): [sPC, tP], (8,6): [sGC, tO],                    (10,6): [sPC, tSAU],         (12,6): [sPC, tA], (13,6): [sPC, tA],                                                                                           (18,6): [sGC, tA], (19,6): [sPC, tA], (20,6): [sGC, tA], (21,6): [sPC, tA],        
    (7,7): [sPC, tP],                                     (10,7): [sPC, tSAU], (11,7): [sPC, tA], (12,7): [sPC, tA], 
  (3,8): [sPC, tH2], (4,8): [sPC, tV], (5,8): [sPC, tV],   (8,8): [sPC, tDA],
(2,9): [sPC, tV],    (4,9): [sPC, t0], (5,9): [sPC, t0],(6,9): [sPC, t0], (7,9): [sPC, tDA], (8,9): [sPC, tDA],  (9,9): [sGC, tDA], (10,9): [sGC, tDA], (11,9): [sGC, tDA],                                                     (19,9): [sPC, tA], (20,9): [sPC, tA],  
(2,10): [sPC, tV],                                                        (7,10): [sPC, tDA], (8,10): [sPC, tDA], (9,10): [sGC, tDA], (10,10): [sGC, tDA], (11,10): [sGC, tDA],                                       (18,10): [sPC, tA], (19,10): [sPC, tA], (20,10): [sGC, tA],  
                     (4,11): [sPC, t0], (5,11): [sGC, t0],                                   (8,11): [sPC, tDA], (9,11): [sGC, tDA], (10,11): [sGC, tDA], (11,11): [sGC, tDA], (12,11): [sGC, tDA], (13,11): [sGC, tDA],         (16,11): [sPC, tA], (17,11): [sGC, tA], (18,11): [sGC, tA], (19,11): [sGC, tA], (20,11): [sGC, tA],  
(2,12): [sPC, t0], (3,12): [sPC, t0],                                                                                                (10,12): [sPC, tDA], (11,12): [sPC, tDA], (12,12): [sPC, tDA],                    (16,12): [sPC, tA], (17,12): [sPC, tA], (18,12): [sGC, tA], (19,12): [sGC, tA], (20,12): [sGC, tA],  
                   (3,13): [sPC, t0],                                                                                                                                                                                                                                             (19,13): [sGC, tA], 
                   (3,14): [sPC, t0],(4,14): [sPC, t0],
                                   (4,15): [sPC, tO], (5,15): [sPC, tO],                                                                                                                                                                                                                                 (20,15): [sPC, t0], (21,15): [sGC, t0], 
                                                                                                                                                                                                                                                                                     (19,16): [sGC, t0], (20,16): [sGC, t0], (21,16): [sGC, t0], 
    (3,18): [sPC, tP], 
    (3,19): [sGC, tP],                                                                                   (10,19): [sGC, t0], 
                        (4,20): [sPC, tSAU], (5,20): [sGC, tSAU],                                 (9,20): [sGC, t0],       (12,20): [sPC, tD], (13,20): [sPC, tD],    (16,20): [sPC, tD], (17,20): [sPC, tD],
    (3,21): [sGC, tSAU], (4,21): [sGC, tSAU], (5,21): [sGC, tSAU], (6,21): [sGC, tSAU],                                                                                                 (17,21): [sPC, tD], (18,21): [sGC, tD], (19,21): [sGC, tD],

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


############################ Gestion des types d'occupation du sol special (qui ne sont pas indiqué sur la carte au début mais qui ont une surface initiale)

surfaceCorrespondantAuPotentielAcceilInitial ={
    'marais salee' : 2,
    'marais salant' : 2,
    'port plaisance' : 4 ,
    'foret' : 80,
    'herbier' : 3
    }

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
    nbCases = (0 if ZHs[typeZH]["potentiel accueil actions1"] is None else 1) + len(ZHs[typeZH]["cases actions2"])
    nbCols = 2
    nbLines = -(-nbCases // nbCols)  # Arrondir au nombre entier supérieur
    pZH[typeZH]=myModel.newCellsOnGrid(nbCols,nbLines,"square",size=40,gap=2,name=typeZH,color=ZHs[typeZH]["couleur"])
    pZH[typeZH].setEntities('potentiel accueil',0)
    pZH[typeZH].setEntities('frequentation',0) 
    pZH[typeZH].setEntities('surfrequentation',0) #0 si la cpacité d'accueil n'est passé  / 1 si la cpacité d'accueil est dépassé
    pZH[typeZH].setEntities('type',"vide")
    pZH[typeZH].setEntities('vue normale',"vide")
    if ZHs[typeZH]["potentiel accueil actions1"] is None:
        startCasesActions2 = 1
    else:
        startCasesActions2 = 2
        case1= pZH[typeZH].getEntity(1,1)
        casesAction1.append(case1)
        case1.setValue('type','action1')
        case1.setValue('vue normale',"action1")
        case1.setValue('potentiel accueil',ZHs[typeZH]["potentiel accueil actions1"])

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
posXinit = 870
posX = posXinit
posY = 30
maxHeightPlateauxPrecedents = 0
for i, aZHtype in enumerate(ordreZHs):
    if aZHtype in ["vide", "mer", "demi-herbier"]: continue
    # if i in [7,13]: posY +=40 # permet de prendre en compte la taille plus grande des plateaux de la ligne précédente    
    myModel.newLabel_stylised(aZHtype,(posX+5,posY-2), size=10)
    aPZH = constructZH(aZHtype, (posX, posY))
    aPZH_height = (aPZH.grid.rows * (aPZH.defaultsize + aPZH.grid.gap)) + aPZH.grid.frameMargin  +10
    # print(aPZH_height)
    maxHeightPlateauxPrecedents = max([maxHeightPlateauxPrecedents , aPZH_height])
    posX += 102  # Incrémentation de posX
    # Vérification si posX dépasse la largeur souhauté
    if posX > 1100:
        posX = posXinit  # Réinitialisation de posX
        # posY += 150  # Incrémentation de posY
        posY += maxHeightPlateauxPrecedents
        maxHeightPlateauxPrecedents =0

#********************************************************************
# variables de simulation

sequestrationZH=myModel.newSimVariable("Sequestration ZH",0)
ptCB=myModel.newSimVariable("CB",0)
valeurPtCB = 0.75 #Taux de conversion entre le point CB et la valeur de sequestration (en T/ha/an)
ptDE=myModel.newSimVariable("DE",0)
cumulDE=myModel.newSimVariable("réserve DE",0)
perc_ptCB_sequestrationZH = myModel.newSimVariable("part CB / sequestration ZH",0)
sequestrationTot=myModel.newSimVariable("Bilan Sequestration",0)

#********************************************************************
# Definiion des actions de jeu

Player = myModel.newPlayer("Player")

for aZH in ZHs.keys():
    Player.addGameAction(myModel.newModifyAction(cases, {"typeZH":aZH},feedbacks=[lambda : updateActions3()]))

nbPionActions1_parJoueur='infinite' #20
pionAction1=myModel.newAgentSpecies("Action1","circleAgent",defaultSize=5,)
pionAction1.newPov("joueur","joueur",listeJoueurs)

for jX in list(listeJoueurs.keys()):
    nomJ =""+jX
    Player.addGameAction(myModel.newCreateAction(pionAction1, {"joueur":nomJ},nbPionActions1_parJoueur,
                            conditions=[
                                    lambda aCell: aCell.classDef != cases and aCell.value('type') == 'action1',
                                        ]
                            ))
Player.addGameAction(myModel.newDeleteAction(pionAction1))

nbPionActions2_parJoueur='infinite' #6
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
Player.addGameAction(myModel.newDeleteAction(pionAction2))


#********************************************************************

def updateActions1():
    for aCase in casesAction1:
        aCase.setValue('frequentation',aCase.nbAgents()) 
        if aCase.nbAgents() > aCase.value('potentiel accueil'):
            aCase.setValue('surfrequentation',1) #0 si la cpacité d'accueil n'est passé  / 1 si la cpacité d'accueil est dépassé
            aCase.grid.gs_aspect.border_color='red'
            aCase.grid.gs_aspect.border_size=4
            aCase.grid.update()
            

def updateActions2():
    totCB = 0
    totDE = 0
    for aPion in pionAction2.getEntities():
        totCB += aPion.cell.value("effet sequestration")
        totDE += aPion.cell.value("effet economie")
    ptCB.setValue(totCB)
    ptDE.setValue(totDE)

def updateActions3():
    totSequest = 0
    for aCase in cases.getEntities():
        valeur = ZHs[aCase.getValue('typeZH')]["sequestration"]  # 0 si la clé n'est pas trouvée
        sequestCase  = valeur * aCase.getValue('surface')
        totSequest += sequestCase
    sequestrationZH.setValue(round(totSequest,1))  # Arrondi à l'unité

def calcSequestrationTot():
    sequestrationTot.setValue(round(sequestrationZH.value + (ptCB.value * valeurPtCB),1))
    perc_ptCB_sequestrationZH.setValue(round(abs((ptCB.value * valeurPtCB) / sequestrationZH.value) * 100, 1))
    
def calcCumulDE():
    cumulDE.incValue(ptDE.value)



def initDebutTour():
    pionAction1.deleteAllEntities()
    pionAction2.deleteAllEntities()
    for aCase in casesAction1:
            aCase.setValue('surfrequentation',0) #0 si la potentiel d'accueil n'est passé  / 1 si la potentiel d'accueil est dépassé
            aCase.grid.gs_aspect.border_color='black'
            aCase.grid.gs_aspect.border_size=1
            aCase.grid.update()
            # updatePotentielAccueil
            aTypeZH = aCase.entDef().entityName
            if surfaceInitiales[aTypeZH] == 0 :
                # surfaceInitialeDeReference = 2  # TODO  Valeur ajouté  AJOUTE A CAUSE DE MARAIS SALEE / HERBIER / MARAIS SALANT, QUI N'ONT PAS DE SURFACE AU DEBUT
                surfaceInitialeDeReference = surfaceCorrespondantAuPotentielAcceilInitial[aTypeZH]
            else:
                surfaceInitialeDeReference = surfaceInitiales[aTypeZH]

            # TODO  Probleème car Foret et Port de plaisance n'ont pas de surface init mais ont pourtant un potentiel d'accueil dès le départ
            surfaceAcutuelle = cases.metricOnEntitiesWithValue('typeZH',aTypeZH,'sumAtt', 'surface')
            if aTypeZH in ['port plaisance','foret'] : surfaceAcutuelle += surfaceCorrespondantAuPotentielAcceilInitial[aTypeZH]
            if aTypeZH in ['herbier'] : surfaceAcutuelle += (cases.metricOnEntitiesWithValue('typeZH','demi-herbier','sumAtt', 'surface') / 2)
            aCase.setValue('potentiel accueil',
                       round(aCase.getInitialValue('potentiel accueil') * surfaceAcutuelle / surfaceInitialeDeReference) 
                                )
            # aCase.setValue('potentiel accueil',
            #            round(aCase.getInitialValue('potentiel accueil') * cases.metricOnEntitiesWithValue('typeZH',aTypeZH,'sumAtt', 'surface') / surfaceInitialeDeReference) 
            #                     )


#********************************************************************

PlayerControlPanel = Player.newControlPanel("Actions")
PlayerControlPanel.moveToCoords(1182,30)

myModel.setCurrentPlayer("Player")

#********************************************************************


myModel.displayTimeInWindowTitle()
modelPhase1=myModel.timeManager.newModelPhase([lambda: initDebutTour()],autoForwardOn=True,messageAutoForward=False)
gamePhase1=myModel.timeManager.newGamePhase("Jouer",[Player],showMessageBoxAtStart=False)
modelPhase1=myModel.timeManager.newModelPhase([lambda: updateActions1(),lambda: updateActions3(),lambda: calcSequestrationTot(),lambda: calcCumulDE()],name='Bilan du tour')

#********************************************************************

# userSelector=myModel.newUserSelector()
# Legend=myModel.newLegend(grid="combined")

#********************************************************************
# Dashboard des scores obtenus
DashBoardInd=myModel.newDashBoard("Suivi des indicateurs")
DashBoardInd.addIndicatorOnSimVariable(sequestrationTot)
DashBoardInd.addSeparator                                      # TODO AddSeperator ne marche pas
DashBoardInd.addIndicatorOnSimVariable(sequestrationZH)
DashBoardInd.addIndicatorOnSimVariable(ptCB)
DashBoardInd.addIndicatorOnSimVariable(perc_ptCB_sequestrationZH)
DashBoardInd.addSeparator
DashBoardInd.addIndicatorOnSimVariable(ptDE)
DashBoardInd.addIndicatorOnSimVariable(cumulDE)
DashBoardInd.moveToCoords(882,750)
#********************************************************************

# Dashboard des surfaces des ZH
DashBoardSurfaces = myModel.newDashBoard("Surfaces")
# dict pour sauvegarder les surfaces initiales
surfaceInitiales = {}
for aZHtype in ordreZHs:
    aMetricIndicator = DashBoardSurfaces.addIndicator_Sum(cases, "surface", aZHtype, 
        conditionsOnEntities=[(lambda case, typeZH=aZHtype: case.value("typeZH") == typeZH)])
    surfaceInitiales[aZHtype] = aMetricIndicator.result
# Ces méthodes ont été remplacé par la méthode générique ci-dessus
# DashBoardSurfaces.addIndicator_Sum(cases,"surface",'champs agricoles', conditionsOnEntities=[lambda case: case.value("typeZH")=='champs agricoles'])
# DashBoardSurfaces.addIndicator_Sum(cases,"surface",'marais doux agricole', conditionsOnEntities=[lambda case: case.value("typeZH")=='marais doux agricole'])
# DashBoardSurfaces.addIndicator_Sum(cases,"surface",'marais doux', conditionsOnEntities=[lambda case: case.value("typeZH")=='marais doux'])
# DashBoardSurfaces.addIndicator_Sum(cases,"surface",'marais saumatre', conditionsOnEntities=[lambda case: case.value("typeZH")=='marais saumatre'])
# DashBoardSurfaces.addIndicator_Sum(cases,"surface",'marais salee', conditionsOnEntities=[lambda case: case.value("typeZH")=='marais salee'])
# DashBoardSurfaces.addIndicator_Sum(cases,"surface",'oestricole', conditionsOnEntities=[lambda case: case.value("typeZH")=='oestricole'])
# DashBoardSurfaces.addIndicator_Sum(cases,"surface",'marais salant', conditionsOnEntities=[lambda case: case.value("typeZH")=='marais salant'])
# DashBoardSurfaces.addIndicator_Sum(cases,"surface",'pres sales', conditionsOnEntities=[lambda case: case.value("typeZH")=='pres sales'])
# DashBoardSurfaces.addIndicator_Sum(cases,"surface",'vasiere nue', conditionsOnEntities=[lambda case: case.value("typeZH")=='vasiere nue'])
# DashBoardSurfaces.addIndicator_Sum(cases,"surface",'herbier', conditionsOnEntities=[lambda case: case.value("typeZH")=='herbier'])
# DashBoardSurfaces.addIndicator_Sum(cases,"surface",'demi-herbier', conditionsOnEntities=[lambda case: case.value("typeZH")=='demi-herbier'])
# DashBoardSurfaces.addIndicator_Sum(cases,"surface",'plage', conditionsOnEntities=[lambda case: case.value("typeZH")=='plage'])
DashBoardSurfaces.moveToCoords(1480,30)

#********************************************************************
# Dashboard des potentiel d'accueil des ZH
DashBoardPotAccueil = myModel.newDashBoard("Potentiel accueil")
for aCaseAction in casesAction1:
    aTypeZH = aCaseAction.entDef().entityName
    aInd = DashBoardPotAccueil.addIndicatorOnEntity(aCaseAction,'potentiel accueil',title=aCaseAction.entDef().entityName)

    if surfaceInitiales[aTypeZH] == 0 and aTypeZH not in ['port plaisance','foret','herbier']:
         aInd.setResult(0)
DashBoardPotAccueil.moveToCoords(1480,500)

#********************************************************************
# Dashboard SOLO - TEST -->  IL FAUDRAIT AFFFICHER PLUTOT LE NOMBRE D'AGENTS (et pas le potentiel d'accueil), 
#           Et donc créé un attribut 'nbPions' qui est mis à jour à chaque pose de pion
dashboardSOLO = myModel.newDashBoard(borderSize=0, borderColor= Qt.transparent, backgroundColor=Qt.transparent)
dashboardSOLO.addIndicatorOnEntity(casesAction1[0],'potentiel accueil', displayName=False)
dashboardSOLO.moveToCoords(1080,145)

#********************************************************************

# first calc of sequestration
updateActions3()
calcSequestrationTot()

#********************************************************************
myModel.launch()
# myModel.launch_withMQTT("Instantaneous")
sys.exit(monApp.exec_())