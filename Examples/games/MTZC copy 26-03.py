import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
import random

monApp=QtWidgets.QApplication([])

myModel=SGModel(1700,1020, name="MTZC", typeOfLayout ="grid", x=5,y=5)
    
#********************************************************************

# Def des joueurs
joueurs_potentiels = {
    'J1': Qt.blue,
    'J2': Qt.red,
    'J3': Qt.yellow,
    'J4': Qt.green,
    'J5': Qt.white,
    'J6': Qt.black,    
    'J7': Qt.magenta,  
    'J8': Qt.gray      
    }
nbJoueurs = 8 #Entre 5 et 8
# Créer le dictionnaire joueurs_actifs avec les N (N= nbJoueurs) premiers éléments de joueurs_poentiels
joueurs_actifs = {key: joueurs_potentiels[key] for key in list(joueurs_potentiels.keys())[:nbJoueurs]}
# Définir le coût du bonus aménagé en fonction du nombre de joueurs
coutBonusAmenage = {
    5: 70,
    6: 84,
    7: 98,
    8: 112
}[nbJoueurs]

#OLD(initial)  ordreZHs = ['marais doux', 'marais saumatre', 'marais salee', 'oestricole', 'vasiere nue',  'herbier', 'champs agricoles', 'plage', 'port industriel', 'pres sales', 'marais doux agricole', 'port plaisance', 'foret', 'marais salant',]
ordreZHs = ['champs agricoles','marais doux agricole', 'marais doux', 'marais saumatre', 'marais saumatre protege', 'marais salee', 'oestricole', 'marais salant', 'pres sales', 'vasiere nue', 'herbier', "demi-herbier", 'plage', 'port plaisance', 'port industriel', 'foret', "mer", "vide"]

# # Définition des zones avec leurs caractéristiques
ZHs = {
    'champs agricoles': {##
        "sequestration": 0,
        "couleur": QColor(255, 0, 0, 120),
        "potentiel accueil actions1": None,
        "cases actions2": [
            {"type_action2": "agri intensive", "effet economie": 3, "effet sequestration": -1},
            {"type_action2": "agri intensive", "effet economie": 3, "effet sequestration": -1},
            {"type_action2": "agri extensive", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "agri extensive", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "fauchage", "effet economie": 0, "effet sequestration": 0},
            {"type_action2": "bovin", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "ovin", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "apiculture", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "fauchage", "effet economie": 0, "effet sequestration": 0},
            *([{"type_action2": "bovin", "effet economie": 2, "effet sequestration": -1} if nbJoueurs >= 6 else None]),
            *([{"type_action2": "ovin", "effet economie": 2, "effet sequestration": -1} if nbJoueurs >= 7 else None]),
            *([{"type_action2": "apiculture", "effet economie": 1, "effet sequestration": 0} if nbJoueurs >= 8 else None])
        ],
        "cases actions2 en plus": [
            {"type_action2": "agri intensive", "effet economie": 3, "effet sequestration": -1},
            {"type_action2": "agri extensive", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "fauchage", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "bovin", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "ovin", "effet economie": 2, "effet sequestration": -1}
        ],
        "seuil variation actions2":14 #seuil de variation de la surface en hectare, déclenchant une augmentation ou une dimunition des cases actions2
    },
    'marais doux agricole': {##
        "sequestration": 0.1,
        "couleur": QColor(139, 69, 19, 120),
        "potentiel accueil actions1": {5: 7, 6: 8, 7: 9, 8: 10}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "agri intensive", "effet economie": 3, "effet sequestration": -1},
            {"type_action2": "agri intensive", "effet economie": 3, "effet sequestration": -1},
            {"type_action2": "agri extensive", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "agri extensive", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "fauchage", "effet economie": 0, "effet sequestration": 0},
            {"type_action2": "bovin", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "ovin", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "apiculture", "effet economie": 1, "effet sequestration": 0},
            *([{"type_action2": "bovin", "effet economie": 2, "effet sequestration": -1} if nbJoueurs >= 6 else None]),
            *([{"type_action2": "ovin", "effet economie": 4, "effet sequestration": -2} if nbJoueurs >= 8 else None])
        ],
        "cases actions2 en plus": [
            {"type_action2": "agri intensive", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "agri extensive", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "fauchage", "effet economie": 0, "effet sequestration": 0},
            {"type_action2": "bovin", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "ovin", "effet economie": 2, "effet sequestration": -1}
        ],
        "seuil variation actions2":10 #seuil de variation de la surface en hectare, déclenchant une augmentation ou une dimunition des cases actions2
    },
    'marais doux': {##
        "sequestration": 0.25,
        "couleur": QColor(100, 149, 237, 120), 
        "potentiel accueil actions1": {5: 15, 6: 18, 7: 21, 8: 24}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "recherche", "effet economie": 1, "effet sequestration": 1},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1},
            *([{"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1} if nbJoueurs >= 6 else None])
        ],
        "cases actions2 en plus": [
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "tourisme", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "tourisme", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "tourisme", "effet economie": 0, "effet sequestration": -1}
        ],
        "seuil variation actions2":4 #seuil de variation de la surface en hectare, déclenchant une augmentation ou une dimunition des cases actions2
    },
    'marais saumatre': {##
        "sequestration": 1.51,
        "couleur": QColor(137, 56, 173, 150),
        "potentiel accueil actions1": {5: 15, 6: 17, 7: 19, 8: 21}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "recherche", "effet economie": 1, "effet sequestration": 1},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "ovin", "effet economie": 1, "effet sequestration": 1},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1},
            *([{"type_action2": "tourisme", "effet economie": 4, "effet sequestration": -2} if nbJoueurs >= 8 else None])
        ],
        "cases actions2 en plus": [
            {"type_action2": "ovin", "effet economie": 1, "effet sequestration": 1},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "ovin", "effet economie": 1, "effet sequestration": 1},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1}
        ],
        "seuil variation actions2":8 #seuil de variation de la surface en hectare, déclenchant une augmentation ou une dimunition des cases actions
    },
    'marais saumatre protege': {##
        "sequestration": 1.51,
        "couleur": QColor(67, 16, 103, 150), # QColor(128, 0, 128, 150),#QColor(147, 112, 219, 150),
        "potentiel accueil actions1": {5: 5, 6: 6, 7: 7, 8: 8}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "recherche", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "tourisme", "effet economie": 5, "effet sequestration": -3},
            {"type_action2": "ovin", "effet economie": 3, "effet sequestration": -1}
        ]
    },
    'marais salee': {##
        "sequestration": 1.75,
        "couleur": QColor(100, 200, 180, 150), #QColor(0, 255, 0, 120),
        "potentiel accueil actions1": 5 if nbJoueurs <= 6 else (6 if nbJoueurs == 7 else 7),   # TODO PROBLEME. Y' a pas de valeurs dans la regle.
        "cases actions2": [
            {"type_action2": "recherche", "effet economie": 1, "effet sequestration": 1},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "coquillage", "effet economie": 1, "effet sequestration": 0} 
        ],
        "cases actions2 en plus": [
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "tourisme", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "coquillage", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "coquillage", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "tourisme", "effet economie": 1, "effet sequestration": 0}
        ],
        "seuil variation actions2": 6 #seuil de variation de la surface en hectare, déclenchant une augmentation ou une dimunition des cases actions
    },
    'oestricole': {##
        "sequestration": 1,
        "couleur": QColor(192, 192, 192, 120), #QColor(128, 128, 128, 120),
        "potentiel accueil actions1": {5: 4, 6: 5, 7: 6, 8: 7}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "economie conchylicole", "effet economie": 2, "effet sequestration": -1}, # TODO coquillage et economie conchylicole ont la meme illustration.
            {"type_action2": "economie conchylicole", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "economie conchylicole", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "economie conchylicole", "effet economie": 2, "effet sequestration": -1},
            *([{"type_action2": "economie conchylicole", "effet economie": 4, "effet sequestration": -2} if nbJoueurs >= 8 else None])
        ],
        "cases actions2 en plus": [
            {"type_action2": "economie conchylicole", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "economie conchylicole", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "economie conchylicole", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "economie conchylicole", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "economie conchylicole", "effet economie": 2, "effet sequestration": -1}
        ],
        "seuil variation actions2": 4 #seuil de variation de la surface en hectare, déclenchant une augmentation ou une dimunition des cases actions
    },
    'marais salant': {##
        "sequestration": 1.2, # moins que maree salée (1.75), mais plus que oestricole (1)
        "couleur": QColor(255, 255, 255, 200),
        "potentiel accueil actions1": 5 if nbJoueurs <= 6 else (6 if nbJoueurs == 7 else 7), # TODO PROBLEME. Y' a pas de valeurs
        "cases actions2": [
            {"type_action2": "saliculture", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "saliculture", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "saliculture", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1}
        ],
        "cases actions2 en plus": [
            {"type_action2": "saliculture", "effet economie": 2, "effet sequestration": 0},
            {"type_action2": "saliculture", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "saliculture", "effet economie": 3, "effet sequestration": -2},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1}
        ],
        "seuil variation actions2": 4 #seuil de variation de la surface en hectare, déclenchant une augmentation ou une dimunition des cases actions
    },
    'pres sales': {##
        "sequestration": 2.4,
        "couleur": QColor(0, 128, 0, 140),
        "potentiel accueil actions1": {5: 8, 6: 10, 7: 13, 8: 15}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "recherche", "effet economie": 1, "effet sequestration": 1},
            {"type_action2": "fauchage", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "ovin", "effet economie": 1, "effet sequestration": 0},
            *([{"type_action2": "ovin", "effet economie": 2, "effet sequestration": 0} if nbJoueurs >= 7 else None])
        ],
        "cases actions2 en plus": [
            {"type_action2": "recherche", "effet economie": 1, "effet sequestration": 1},
            {"type_action2": "fauchage", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "ovin", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "fauchage", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "ovin", "effet economie": 1, "effet sequestration": 0}
        ],
        "seuil variation actions2": 2 #seuil de variation de la surface en hectare, déclenchant une augmentation ou une dimunition des cases actions
    },
    'vasiere nue': {##
        "sequestration": 0.25,
        "couleur": QColor(180, 150, 100, 140),
        "potentiel accueil actions1": {5: 14, 6: 17, 7: 20, 8: 23}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "recherche", "effet economie": 1, "effet sequestration": 1},
            {"type_action2": "navire", "effet economie": 2, "effet sequestration": -2},
            {"type_action2": "coquillage", "effet economie": 2, "effet sequestration": 0},
            *([{"type_action2": "plaisance", "effet economie": 1, "effet sequestration": -1} if nbJoueurs >= 6 else None])
        ],
        "cases actions2 en plus": [
            {"type_action2": "plaisance", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -2},
            {"type_action2": "navire", "effet economie": 2, "effet sequestration": -2},
            {"type_action2": "coquillage", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "coquillage", "effet economie": 1, "effet sequestration": 0}
        ],
        "seuil variation actions2": 2 #seuil de variation de la surface en hectare, déclenchant une augmentation ou une dimunition des cases actions
    },
    "vasiere nue Diop": {##
        "sequestration": 7.9,
        "couleur": QColor(210, 180, 140, 120),
        "potentiel accueil actions1": {5: 8, 6: 9, 7: 11, 8: 12}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "recherche", "effet sequestration": 1, "effet economie": 0},
            {"type_action2": "recherche", "effet sequestration": 1, "effet economie": 0},
            {"type_action2": "ovin", "effet sequestration": 3, "effet economie": -1},
            {"type_action2": "tourisme", "effet sequestration": 5, "effet economie": -3}
        ]
    },
   "pres sales Diop": {##
        "sequestration": 8.8,
        "couleur": QColor(0, 108, 10, 120),
    },
   "demi-herbier Diop": {##
        "sequestration": 3.5, #environ la moitiéde la  vasière nue Diop,
        "couleur": QColor(0, 245, 20, 40), 
    },
   "demi-herbier": {##
        "sequestration": 0.83, #moitié herbier, moitié vasière nue,
        "couleur": QColor(0, 255, 0, 50), #QColor(130, 180, 100, 120)
    },
   'herbier': {##
        "sequestration": 1.4,
        "couleur": QColor(0, 255, 0, 150),  #QColor(0, 128, 0, 120),
        "potentiel accueil actions1": {5: 9, 6: 11, 7: 13, 8: 15}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "recherche", "effet economie": 1, "effet sequestration": 1},
            {"type_action2": "plaisance", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "navire", "effet economie": 2, "effet sequestration": -1},
            *([{"type_action2": "tourisme", "effet economie": 3, "effet sequestration": -3} if nbJoueurs >= 6 else None])
        ],
        "cases actions2 en plus": [
            {"type_action2": "recherche", "effet economie": 1, "effet sequestration": 1},
            {"type_action2": "navire", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "plaisance", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "tourisme", "effet economie": 3, "effet sequestration": -2},
            {"type_action2": "plaisance", "effet economie": 1, "effet sequestration": -1}
        ],
        "seuil variation actions2": 2 #seuil de variation de la surface en hectare, déclenchant une augmentation ou une dimunition des cases actions
    },
    'plage': {##
        "sequestration": 0,
        "couleur": QColor(255, 255, 130, 180),
        "potentiel accueil actions1": {5: 14, 6: 16, 7: 18, 8: 20}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "toursime", "effet economie": 3, "effet sequestration": -1},
            {"type_action2": "toursime", "effet economie": 3, "effet sequestration": -1},
            {"type_action2": "toursime", "effet economie": 3, "effet sequestration": -1},
            {"type_action2": "toursime", "effet economie": 3, "effet sequestration": -1},
            {"type_action2": "toursime", "effet economie": 3, "effet sequestration": -1},
            *([{"type_action2": "toursime", "effet economie": 4, "effet sequestration": -2} if nbJoueurs >= 7 else None])
        ],
        "cases actions2 en plus": [
            {"type_action2": "toursime", "effet economie": 3, "effet sequestration": -1},
            {"type_action2": "toursime", "effet economie": 3, "effet sequestration": -1},
            {"type_action2": "toursime", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "toursime", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "toursime", "effet economie": -1, "effet sequestration": -1}
        ],
        "seuil variation actions2": 4 #seuil de variation de la surface en hectare, déclenchant une augmentation ou une dimunition des cases actions
    },
    'port plaisance': {##
        "sequestration": 0,
        "couleur": QColor(30, 30, 90, 120),
        "potentiel accueil actions1": {5: 11, 6: 13, 7: 15, 8: 17}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "plaisance", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "plaisance", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "plaisance", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "plaisance", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "tourisme", "effet economie": 3, "effet sequestration": -1}
        ],
        "cases actions2 en plus": [
            {"type_action2": "toursime", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "toursime", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "plaisance", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "plaisance", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "plaisance", "effet economie": 1, "effet sequestration": -1}
        ],
        "seuil variation actions2": 2 #seuil de variation de la surface en hectare, déclenchant une augmentation ou une dimunition des cases actions
    },
    'port industriel': {##
        "sequestration": 0,
        "couleur": QColor(40, 40, 40, 180),
        "potentiel accueil actions1": None,
        "cases actions2": [
            {"type_action2": "industrie portuaire", "effet economie": 6, "effet sequestration": -2},
            {"type_action2": "industrie portuaire", "effet economie": 6, "effet sequestration": -2},
            {"type_action2": "industrie portuaire", "effet economie": 6, "effet sequestration": -2},
            {"type_action2": "industrie portuaire", "effet economie": 6, "effet sequestration": -2},
            {"type_action2": "industrie portuaire", "effet economie": 6, "effet sequestration": -2},
            *([{"type_action2": "industrie portuaire", "effet economie": 7, "effet sequestration": -3} if nbJoueurs >= 7 else None]),
            *([{"type_action2": "industrie portuaire", "effet economie": 8, "effet sequestration": -4} if nbJoueurs >= 8 else None])
        ],
        "cases actions2 en plus": [
            {"type_action2": "industrie portuaire", "effet economie": 6, "effet sequestration": -2},
            {"type_action2": "industrie portuaire", "effet economie": 6, "effet sequestration": -2},
            {"type_action2": "industrie portuaire", "effet economie": 6, "effet sequestration": -2},
            {"type_action2": "industrie portuaire", "effet economie": 6, "effet sequestration": -2},
            {"type_action2": "industrie portuaire", "effet economie": 6, "effet sequestration": -2}
        ],
        "seuil variation actions2": 2 #seuil de variation de la surface en hectare, déclenchant une augmentation ou une dimunition des cases actions
    },
    'foret': {##
        "sequestration": 0,
        "couleur": QColor(0, 100, 0, 200),
        "potentiel accueil actions1": {5: 13, 6: 15, 7: 17, 8: 19}[nbJoueurs],
        "cases actions2": [
            {"type_action2": "coupe arbres", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "coupe arbres", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "coupe arbres", "effet economie": 1, "effet sequestration": -1},
            *([{"type_action2": "coupe arbres", "effet economie": 3, "effet sequestration": -2} if nbJoueurs >= 7 else None])
        ],
        "cases actions2 en plus": [
            {"type_action2": "coupe arbres", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "coupe arbres", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "coupe arbres", "effet economie": 3, "effet sequestration": -1},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1}
        ],
        "seuil variation actions2": 8 #seuil de variation de la surface en hectare, déclenchant une augmentation ou une dimunition des cases actions
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

# Parcourir le dictionnaire ZHs
for key, value in ZHs.items():
    # Vérifier si 'cases actions2' est dans les valeurs
    if "cases actions2" in value:
        # Filtrer les éléments de 'cases actions2' pour enlever ceux qui sont None
        value["cases actions2"] = [action for action in value["cases actions2"] if action is not None]


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
tPP = 'port plaisance'
tPI = 'port industriel'
tF = 'foret'


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
    (7,6): [sPC, tP], (8,6): [sGC, tO],                    (10,6): [sPC, tSAU],         (12,6): [sPC, tDA], (13,6): [sPC, tDA],                                                                                           (18,6): [sGC, tA], (19,6): [sPC, tA], (20,6): [sGC, tA], (21,16): [sPC, tA],        
    (7,7): [sPC, tP],                                     (10,7): [sPC, tSAU], (11,7): [sPC, tDA], (12,7): [sPC, tDA], 
  (3,8): [sPC, tV], (4,8): [sPC, tV], (5,8): [sPC, tV],   (8,8): [sPC, tDA],
(2,9): [sPC, tV],    (4,9): [sPC, t0], (5,9): [sPC, t0],(6,9): [sPC, t0], (7,9): [sPC, tDA], (8,9): [sPC, tDA],  (9,9): [sGC, tDA], (10,9): [sGC, tDA], (11,9): [sGC, tDA],                                                     (19,9): [sPC, t0], (20,9): [sPC, t0],  
(2,10): [sPC, tV],                                                        (7,10): [sPC, tDA], (8,10): [sPC, tDA], (9,10): [sGC, tDA], (10,10): [sGC, tDA], (11,10): [sGC, tDA],                                       (18,10): [sPC, tA], (19,10): [sPC, tA], (20,10): [sGC, t0],  
                     (4,11): [sPC, t0], (5,11): [sGC, t0],                                   (8,11): [sPC, tDA], (9,11): [sGC, tDA], (10,11): [sGC, tDA], (11,11): [sGC, tDA], (12,11): [sGC, tDA], (13,11): [sGC, tDA],         (16,11): [sPC, tA], (17,11): [sGC, tA], (18,11): [sGC, tA], (19,11): [sGC, tA], (20,11): [sGC, tA],  
(2,12): [sPC, tPI], (3,12): [sPC, tPI],                                                                                                (10,12): [sPC, tDA], (11,12): [sPC, tDA], (12,12): [sPC, tDA],                    (16,12): [sPC, tA], (17,12): [sPC, tA], (18,12): [sGC, tA], (19,12): [sGC, tA], (20,12): [sGC, tA],  
                   (3,13): [sPC, tPP],                                                                                                                                                                                                                                             (19,13): [sGC, tA], 
                   (3,14): [sPC, tPP],(4,14): [sPC, tPP],
                                   (4,15): [sPC, tO], (5,15): [sPC, tO],                                                                                                                                                                                                                                 (20,15): [sPC, tF], (21,15): [sGC, tF], 
                                                                                                                                                                                                                                                                                     (19,16): [sGC, tF], (20,16): [sGC, tF], (21,16): [sGC, tF], 
    (3,18): [sPC, tP], 
    (3,19): [sGC, tP],                                                                                    
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
    # 'port plaisance' : 4 ,
    'marais saumatre protege' : 8 ,
    # 'foret' : 80,
    'herbier' : 2,
    'vasiere nue' : 16
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
    nbCases = (0 if ZHs[typeZH]["potentiel accueil actions1"] is None else 4) + len(ZHs[typeZH]["cases actions2"]) + len(ZHs[typeZH].get("cases actions2 en plus", []))
    nbCols = 4
    nbLines = -(-nbCases // nbCols)  # Arrondir au nombre entier supérieur
    pZH[typeZH]=myModel.newCellsOnGrid(nbCols,nbLines,"square",size=30,gap=2,name=typeZH,color=ZHs[typeZH]["couleur"])
    pZH[typeZH].setEntities('potentiel accueil',0)
    pZH[typeZH].setEntities('frequentation',0) 
    pZH[typeZH].setEntities('surfrequentation',0) #0 si la cpacité d'accueil n'est passé  / 1 si la cpacité d'accueil est dépassé
    pZH[typeZH].setEntities('type',"vide")
    pZH[typeZH].setEntities('vue normale',"vide")
    pZH[typeZH].setEntities('effet sequestration',0)
    pZH[typeZH].setEntities('effet economie',0)
    pZH[typeZH].setValue('surface initiale',cases.metricOnEntitiesWithValue('typeZH',typeZH,'sumAtt', 'surface'))
    pZH[typeZH].setValue('surfaceDuSeuilPrécédent',pZH[typeZH].value('surface initiale'))
    pZH[typeZH].setValue("surface actuelle",cases.metricOnEntitiesWithValue('typeZH',typeZH,'sumAtt', 'surface'))      



    if ZHs[typeZH]["potentiel accueil actions1"] is None:
        startCasesActions2 = 1
    else:
        startCasesActions2 = nbCols +1
        case1= pZH[typeZH].getEntity(1,1)
        casesAction1.append(case1)
        case1.setValue('type','action1')
        case1.setValue('vue normale',"action1")
        case1.setValue('potentiel accueil',ZHs[typeZH]["potentiel accueil actions1"])
        #supprimer les cases de la première ligne sauf la première
        for aCaseInutile in pZH[typeZH].getEntities_withRow(1)[1:]:
            pZH[typeZH].deleteEntity(aCaseInutile)

    #Ajout des actions2 de base
    for i, paramCaseAction2 in enumerate(ZHs[typeZH]["cases actions2"], start=startCasesActions2):
        caseX = pZH[typeZH].getEntity(i)
        caseX.setValue("type", "action2")
        caseX.setValue("vue normale", "action2")
        for aParam, aValue in paramCaseAction2.items():
            caseX.setValue(aParam, aValue)
            if aParam == "type_action2":
                caseX.setValue("vue normale", aValue)

    #Ajout des actions2 en plus
    ZHs[typeZH]['Actions2 en plus']=[]
    if ZHs[typeZH].get("cases actions2 en plus") is not None:
        for j, paramCaseAction2 in enumerate(ZHs[typeZH]["cases actions2 en plus"], start=i+1):
            caseX = pZH[typeZH].getEntity(j)
            caseX.setValue("type", "action2")
            caseX.setValue("vue normale", "action2")
            for aParam, aValue in paramCaseAction2.items():
                caseX.setValue(aParam, aValue)
                if aParam == "type_action2":
                    caseX.setValue("vue normale", aValue)
            ZHs[typeZH]['Actions2 en plus'].append(caseX)
            pZH[typeZH].deleteEntity(caseX)


    pZH[typeZH].newPov("vue normale", "vue normale", dictSymbology)  
    pZH[typeZH].newBorderPovColorAndWidth("bords", "type", {"action1": [Qt.black,1], "action2": [Qt.black,1], "vide": [Qt.transparent,0]})
    pZH[typeZH].displayBorderPov("bords")
  

    if coords != None : pZH[typeZH].grid.moveToCoords(coords)

    return pZH[typeZH]

# les plateaux des ZH sont stockés dans le dico pZH{)
pZH={}
posXinit = 870
incPosX = 150
posX = posXinit
# posY = 30
nbColumns_plateauxZH = 3 
maxPosX = 1300 # A faire varier en fonctio du nb de colonnes
listPosY = [30,30,30]
# maxHeightPlateauxPrecedents = 0
num_col = 0
for i, aZHtype in enumerate(ordreZHs):
    if aZHtype in ["vide", "mer", "demi-herbier"]: continue
    num_col = (num_col + 1) % nbColumns_plateauxZH  # ajouter 1 à num_col et réinitialise sa valeur à 1 si le résultat est supérieur à 3 
    # if i in [7,13]: posY +=40 # permet de prendre en compte la taille plus grande des plateaux de la ligne précédente    
    myModel.newLabel_stylised(aZHtype,(posX+5,listPosY[num_col]-2), size=10)
    aPZH = constructZH(aZHtype, (posX, listPosY[num_col]))
    aPZH_height = (aPZH.grid.rows * (aPZH.defaultsize + aPZH.grid.gap)) + aPZH.grid.frameMargin  +10
    # print(aPZH_height)
    listPosY[num_col] = listPosY[num_col] + aPZH_height
    posX += incPosX  # Incrémentation de posX
    # Vérification si posX dépasse la largeur souhauté
    if posX > maxPosX:
        posX = posXinit  # Réinitialisation de posX
        # posY += 150  # Incrémentation de posY
        # posY += maxHeightPlateauxPrecedents
        # maxHeightPlateauxPrecedents =0

#********************************************************************
# variables de simulation

sequestrationZH=myModel.newSimVariable("Sequestration ZH",0)
ptCB=myModel.newSimVariable("CB",0)
valeurPtCB = 0.75 #Taux de conversion entre le point CB et la valeur de sequestration (en T/ha/an)
ptDE=myModel.newSimVariable("DE",0)
cumulDE=myModel.newSimVariable("réserve DE",0)
perc_ptCB_sequestrationZH = myModel.newSimVariable("part CB / sequest ZH",0.00)
sequestrationTot=myModel.newSimVariable("Bilan Sequestration",0)

#********************************************************************
# Definition des actions de jeu

Player = myModel.newPlayer("Player")

for aZH in ZHs.keys():
    Player.addGameAction(myModel.newModifyAction(cases, {"typeZH":aZH},feedbacks=[lambda : updateActions3()]))

nbPionActions1_parJoueur='infinite' #20
pionAction1=myModel.newAgentSpecies("Action1","circleAgent",defaultSize=5,)
pionAction1.newPov("joueur","joueur",joueurs_potentiels)

for jX in list(joueurs_actifs.keys()):
    nomJ =""+jX
    Player.addGameAction(myModel.newCreateAction(pionAction1, {"joueur":nomJ},nbPionActions1_parJoueur,
                            conditions=[
                                    lambda aCell: aCell.classDef != cases and aCell.value('type') == 'action1',
                                        ],
                            create_several_at_each_click = True
                            ))
Player.addGameAction(myModel.newDeleteAction(pionAction1))

nbPionActions2_parJoueur='infinite' #6
pionAction2=myModel.newAgentSpecies("Action2","squareAgent",defaultSize=20,locationInEntity='center')
pionAction2.newPov("joueur","joueur",joueurs_actifs)

for jX in list(joueurs_actifs.keys()):
    nomJ =""+jX
    Player.addGameAction(myModel.newCreateAction(pionAction2, {"joueur":nomJ},nbPionActions2_parJoueur,
                            conditions=[
                                    lambda aCell: aCell.classDef != cases and aCell.value('type') == 'action2',
                                    lambda aCell: aCell.isEmpty(),
                                    ],
                            feedbacks=[lambda : updateActions2()]))
Player.addGameAction(myModel.newDeleteAction(pionAction2,feedbacks=[lambda : updateActions2()]))


#********************************************************************

def updateActions1():
    for aCase in casesAction1:
        aCase.setValue('frequentation',aCase.nbAgents()) 
        if aCase.nbAgents() > aCase.value('potentiel accueil'):
            aCase.setValue('surfrequentation',1) #0 si la capacité d'accueil n'est pas dépassé  / 1 si la cpacité d'accueil est dépassé
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
    #Calcul des surfaces actuelles
    surface_demi_herbier = cases.metricOnEntitiesWithValue('typeZH','demi-herbier','sumAtt', 'surface')
    for typeZH in ZHs.keys():
        if typeZH in ['demi-herbier', 'mer', 'vide','vasiere nue Diop','pres sales Diop','demi-herbier Diop']: continue
        pZH[typeZH].setValue("surface actuelle",cases.metricOnEntitiesWithValue('typeZH',typeZH,'sumAtt', 'surface'))      
        if typeZH in ['herbier','vasiere nue'] : pZH[typeZH].incValue("surface actuelle",(surface_demi_herbier / 2))        
    #maj des cases Actions1 et des potentiels d'accueil
    for aCase in casesAction1:
            aCase.setValue('surfrequentation',0) #0 si la potentiel d'accueil n'est pas dépassé  / 1 si la potentiel d'accueil est dépassé
            aCase.grid.gs_aspect.border_color='black'
            aCase.grid.gs_aspect.border_size=1
            aCase.grid.update()
            # updatePotentielAccueil
            aTypeZH = aCase.entDef().entityName
            if aTypeZH in surfaceCorrespondantAuPotentielAcceilInitial:    #  AJOUT A CAUSE DE MARAIS SALEE / HERBIER / MARAIS SALANT, QUI N'ONT PAS DE SURFACE AU DEBUT
                surfaceInitialeDeReference = surfaceCorrespondantAuPotentielAcceilInitial[aTypeZH]
            else:
                surfaceInitialeDeReference = surfaceInitiales[aTypeZH]

            surfaceActuelle = aCase.entDef().value('surface actuelle')
            aCase.setValue('potentiel accueil',
                       round(aCase.getInitialValue('potentiel accueil') * surfaceActuelle / surfaceInitialeDeReference) )

    # maj des actions2
    for typeZH, zhData in ZHs.items():
        if typeZH in ['demi-herbier', 'mer', 'vide','vasiere nue Diop','pres sales Diop','demi-herbier Diop']: continue
        surfaceActuelle = pZH[typeZH].value('surface actuelle')
        seuilVariation = zhData.get("seuil variation actions2", float('inf'))
        # surfaceInitiale = pZH[typeZH].value("surface initiale")
        # nombreDeTranchesDeSeuil_ParRapport_a_Initial = abs(surfaceActuelle - surfaceInitiale) // seuilVariation
        # print(f"Type ZH: {typeZH}, Surface Actuelle: {surfaceActuelle}, Surface Initiale: {surfaceInitiale}, Seuil Variation: {seuilVariation}, Nombre de Tranches du Seuil: {nombreDeTranchesDeSeuil_ParRapport_a_Initial}")
        # if typeZH in['marais doux', 'marais doux agricole']:
        #     print(f"Type ZH: {typeZH}, Surface Actuelle: {surfaceActuelle}")
        #     print(f"AVANT Surface seuil précédent: {pZH[typeZH].value('surfaceDuSeuilPrécédent')}")
        
        while surfaceActuelle >= pZH[typeZH].value("surfaceDuSeuilPrécédent"):
            # Si surfaceActuelle >= surfaceDuSeuilPrécédent
            # alors on ajoute des actions
            pZH[typeZH].incValue("surfaceDuSeuilPrécédent", seuilVariation)
            if ZHs[typeZH]['Actions2 en plus'] == []: break # sort de la boucle, si il n'y a plus de case actions2 en plus
            casesEnPlus = ZHs[typeZH]['Actions2 en plus'][0]
            pZH[typeZH].reviveThisCell(casesEnPlus)
            ZHs[typeZH]['Actions2 en plus'].remove(casesEnPlus)
            # casesEnPlus.gs_aspect.border_color='red'
            # casesEnPlus.gs_aspect.border_size=4
                 
        # Deuxième boucle while pour gérer le cas où surfaceActuelle <= (surfaceDuSeuilPrécédent + seuilVariation)
        while (pZH[typeZH].value("surfaceDuSeuilPrécédent") - surfaceActuelle) >= seuilVariation:
            pZH[typeZH].decValue("surfaceDuSeuilPrécédent", seuilVariation)
            casesActions2_actives = pZH[typeZH].getEntities_withValue("type", "action2")
            if casesActions2_actives == []: break # sort de la boucle, si il n'y a plus de case actions2 à enlever
            # Récupérer la dernière case à enlever
            caseX = casesActions2_actives[-1] #récupère la dernière case action2 active
            pZH[typeZH].deleteEntity(caseX)
            ZHs[typeZH]['Actions2 en plus'].insert(0, caseX)  # Ajoute caseX au début de la liste

        # if typeZH in['marais doux', 'marais doux agricole']:
        #     print(f"APRES Surface seuil précédent: {pZH[typeZH].value('surfaceDuSeuilPrécédent')}")

        
    ptCB.setValue(0)
    ptDE.setValue(0)
    perc_ptCB_sequestrationZH.setValue(0)
    sequestrationTot.setValue(sequestrationZH.getValue())
    
#********************************************************************

PlayerControlPanel = Player.newControlPanel("Actions")
PlayerControlPanel.moveToCoords(1320,30)

myModel.setCurrentPlayer("Player")

#********************************************************************


myModel.displayTimeInWindowTitle()
modelPhase1=myModel.timeManager.newModelPhase([lambda: initDebutTour()],auto_forward=True,message_auto_forward=False)
gamePhase1=myModel.timeManager.newGamePhase("Jouer",[Player],show_message_box_at_start=False)
modelPhase1=myModel.timeManager.newModelPhase([lambda: updateActions1(),lambda: updateActions3(),lambda: calcSequestrationTot(),lambda: calcCumulDE()],name='Bilan du tour')

#********************************************************************

# userSelector=myModel.newUserSelector()
# Legend=myModel.newLegend(grid="combined")

#********************************************************************
# Dashboard des scores obtenus
DashBoardInd=myModel.newDashBoard("Suivi des indicateurs")
DashBoardInd.addIndicatorOnSimVariable(sequestrationZH)
DashBoardInd.addSeparator()                                  
DashBoardInd.addIndicatorOnSimVariable(ptCB)
DashBoardInd.addIndicatorOnSimVariable(perc_ptCB_sequestrationZH)
DashBoardInd.addSeparator()
DashBoardInd.addIndicatorOnSimVariable(sequestrationTot)
DashBoardInd.addSeparator()
DashBoardInd.addIndicatorOnSimVariable(ptDE)
DashBoardInd.addIndicatorOnSimVariable(cumulDE)
DashBoardInd.moveToCoords(1510,725)
#********************************************************************

# Dashboard des surfaces des ZH
DashBoardSurfaces = myModel.newDashBoard("Surfaces")
# dict pour sauvegarder les surfaces initiales
surfaceInitiales = {}
for aZHtype in ordreZHs:
    aMetricIndicator = DashBoardSurfaces.addIndicator_Sum(cases, "surface", aZHtype, 
        conditionsOnEntities=[(lambda case, typeZH=aZHtype: case.value("typeZH") == typeZH)])
    surfaceInitiales[aZHtype] = aMetricIndicator.result
DashBoardSurfaces.moveToCoords(1510,30)

#********************************************************************
# Dashboard des potentiel d'accueil des ZH
DashBoardPotAccueil = myModel.newDashBoard("Potentiel accueil")
for aCaseAction in casesAction1:
    aTypeZH = aCaseAction.entDef().entityName
    aInd = DashBoardPotAccueil.addIndicatorOnEntity(aCaseAction,'potentiel accueil',title=aCaseAction.entDef().entityName)

    if surfaceInitiales[aTypeZH] == 0 and aTypeZH not in ['port plaisance','foret','herbier']:
         aInd.setResult(0)
DashBoardPotAccueil.moveToCoords(1510,430)


#********************************************************************
#BUTTON POUR LES CARTES DE CHGT DE LAND USE
nbBonusAmenage = myModel.newSimVariable(' Bonus déjà utilisés   ',0)
dashBonus = myModel.newDashBoard(backgroundColor='#afe3d7', borderColor='transparent')
dashBonus.addIndicatorOnSimVariable(nbBonusAmenage)
dashBonus.moveToCoords(870,852)
myModel.newButton(
    (lambda: bonusAmenagemet()),
    f"Bonus 10ha \nd'aménagement ({coutBonusAmenage} DE)",
    (870,800),
    padding=10,
    background_color='#afe3d7'
)
def bonusAmenagemet():
    cumulDE.decValue(coutBonusAmenage)
    nbBonusAmenage.incValue()

#********************************************************************
# Dashboard SOLO - TEST -->  IL FAUDRAIT AFFFICHER PLUTOT LE NOMBRE D'AGENTS (et pas le potentiel d'accueil), 
#           Et donc créé un attribut 'nbPions' qui est mis à jour à chaque pose de pion
# dashboardSOLO = myModel.newDashBoard(borderSize=0, borderColor= Qt.transparent, backgroundColor=Qt.transparent)
# dashboardSOLO.addIndicatorOnEntity(casesAction1[0],'potentiel accueil', displayName=False)
# dashboardSOLO.moveToCoords(1080,145)

#********************************************************************

# first calc of sequestration
updateActions3()
calcSequestrationTot()

#********************************************************************
myModel.launch()
# myModel.launch_withMQTT("Instantaneous")
sys.exit(monApp.exec_())