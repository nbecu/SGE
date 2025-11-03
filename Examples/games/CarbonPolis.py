import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from PyQt5.QtWidgets import QInputDialog
from PyQt5.QtCore import QPoint
import random
monApp=QtWidgets.QApplication([])

#********************************************************************
# Initialisation de l'application

myModel=SGModel(1700,1020, name="CarbonPolis", nb_columns=7)
    
#********************************************************************

nbJoueurs = 8 #Entre 5 et 8

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
ordreZHs = ['champs agricoles','marais doux agricole', 'marais doux', 'marais saumatre', 'marais salee', 'oestricole', 'marais salant', 'pres sales', 'herbier', "demi-herbier", 'vasiere nue', 'plage', 'port plaisance', 'port industriel', 'foret', 'vasiere nue Diop', 'marais saumatre d''Huyez', "mer", "vide"]

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
            {"type_action2": "ovin", "effet economie": 1, "effet sequestration": 1},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "recherche", "effet economie": 1, "effet sequestration": 1},
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
    'marais saumatre d''Huyez': {##
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
        "potentiel accueil actions1": {5: 8, 6: 10, 7: 13, 8: 15}[nbJoueurs],   # VALEURS Identiques à Pré salés
        "cases actions2": [
            # Vide car les premieres actions 2 sauf dans les cases en plus
        ],
        "cases actions2 en plus": [
            {"type_action2": "coquillage", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "recherche", "effet economie": 1, "effet sequestration": 1},
            
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
            {"type_action2": "economie conchylicole", "effet economie": 2, "effet sequestration": -1},
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
        "potentiel accueil actions1": {5: 4, 6: 5, 7: 6, 8: 7}[nbJoueurs], # VALEURS Identiques à Marais Oestréicoles
        "cases actions2": [
            # Vide car les premieres actions 2 sauf dans les cases en plus
        ],
        "cases actions2 en plus": [
            {"type_action2": "saliculture", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "saliculture", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "saliculture", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1},

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
            {"type_action2": "ovin", "effet economie": 1, "effet sequestration": 0},
            {"type_action2": "fauchage", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "recherche", "effet economie": 1, "effet sequestration": 1},
            *([{"type_action2": "ovin", "effet economie": 2, "effet sequestration": 0} if nbJoueurs >= 7 else None])
        ],
        "cases actions2 en plus": [
            {"type_action2": "recherche", "effet economie": 1, "effet sequestration": 1},
            {"type_action2": "fauchage", "effet economie": 1, "effet sequestration": -1},
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
            {"type_action2": "coquillage", "effet economie": 2, "effet sequestration": 0},
            {"type_action2": "navire", "effet economie": 2, "effet sequestration": -2},
            {"type_action2": "recherche", "effet economie": 1, "effet sequestration": 1},            
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
        "sequestration": 3.5, #environ la moitié de la  vasière nue Diop,
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
            {"type_action2": "tourisme", "effet economie": 2, "effet sequestration": -1},
            {"type_action2": "plaisance", "effet economie": 1, "effet sequestration": -1},
            {"type_action2": "recherche", "effet economie": 1, "effet sequestration": 1},
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
        "seuil variation actions2": 2 #seuil de variation de la surface en hectare, déclenchant une augmentation ou une dimunition des cases actions
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

def updateSurfaceZH(typeZH):
    """
    Met à jour la surface actuelle d'un type de ZH.
    
    Args:
        typeZH (str): Le type de zone humide à mettre à jour
    """
    pZH[typeZH].setValue("surface actuelle",cases.metricOnEntitiesWithValue('typeZH', typeZH, 'sumAtt', 'surface'))
    if typeZH in ['herbier','vasiere nue']:
        surface_demi_herbier = cases.metricOnEntitiesWithValue('typeZH','demi-herbier','sumAtt', 'surface')
        pZH[typeZH].incValue("surface actuelle",int(surface_demi_herbier / 2))      
    if typeZH in ['herbier','vasiere nue Diop']:
        surface_demi_herbier_diop = cases.metricOnEntitiesWithValue('typeZH','demi-herbier Diop','sumAtt', 'surface')
        pZH[typeZH].incValue("surface actuelle",int(surface_demi_herbier_diop / 2))    

def updateSurfaceAllZH():
    """Met à jour la surface de toutes les ZH."""
    for typeZH in ZHs.keys():
            if typeZH in ['demi-herbier', 'mer', 'vide','pres sales Diop','demi-herbier Diop']: continue
            updateSurfaceZH(typeZH)


# construction du plateau
cases=myModel.newCellsOnGrid(21,21,"square",size=40,gap=0,backGroundImage=QPixmap("./icon/MTZC/plateau-jeu.jpg"))
# Liste des coordonnées spécifiques à préserver avec leur valeur de surface
cases_preservees = {
                                                         (10,2): [sPC, tH2], (11,2): [sGC, tPS], (13,2): [sGC, tA],
                                        (9,3): [sPC, tH2], (10,3): [sGC, tV], (11,3): [sPC, tPS], (13,3): [sGC, tA], (14,3): [sGC, tA],          (18,3): [sPC, tA],
                                         (9,4): [sPC, tPS], (10,4): [sPC, tPS],                                          (18,4): [sGC, tA], (19,4): [sGC, tA],
                       (8,5): [sPC, tO],                   (10,5): [sGC, tSAU],        (12,5): [sPC, tSAU], (13,5): [sGC, tSAU], (14,5): [sPC, tSAU],                                                                                                                           (21,5): [sPC, tA],
    (7,6): [sPC, tP], (8,6): [sGC, tO],                    (10,6): [sPC, tSAU],         (12,7): [sPC, tDA], (13,7): [sPC, tDA],                                                                                           (18,6): [sGC, tA], (19,6): [sPC, tA], (20,6): [sGC, tA], (21,6): [sPC, tA],        
    (7,7): [sPC, tP],                                     (10,7): [sPC, tSAU], (11,8): [sPC, tDA], (12,8): [sPC, tDA], 
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
    if (aCase.xCoord,aCase.yCoord) in cases_preservees:
        aCase.setValue("surface", cases_preservees[(aCase.xCoord, aCase.yCoord)][0])  # Définir la valeur de surface
        aCase.setValue("typeZH", cases_preservees[(aCase.xCoord, aCase.yCoord)][1])  # Définir la valeur de TYPEzh
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

surfaceCorrespondantAuPotentielAccueilInitial ={
    'marais salee' : 6,
    'marais salant' : 4,    
    'marais saumatre d''Huyez' : 8 ,  
    # 'herbier' : 2,
    'vasiere nue Diop' : 18
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
    pZH[typeZH]=myModel.newCellsOnGrid(nbCols,nbLines,"square",size=30,gap=2,name=typeZH,backgroundColor=ZHs[typeZH]["couleur"])
    pZH[typeZH].setEntities('potentiel accueil',0)
    pZH[typeZH].setEntities('frequentation',0) 
    pZH[typeZH].setEntities('surfrequentation',0) #0 si la cpacité d'accueil n'est passé  / 1 si la cpacité d'accueil est dépassé
    pZH[typeZH].setEntities('type',"vide")
    pZH[typeZH].setEntities('vue normale',"vide")
    pZH[typeZH].setEntities('effet sequestration',0)
    pZH[typeZH].setEntities('effet economie',0)
    updateSurfaceZH(typeZH) #permet de calculer la surface actuelle en prenant en compte le cas des demi-herbier et autre cas particuliers
    if typeZH in surfaceCorrespondantAuPotentielAccueilInitial:  
        surfaceInitialeDeReferencePourPotentielAccueil = surfaceCorrespondantAuPotentielAccueilInitial[typeZH]
    else:
        surfaceInitialeDeReferencePourPotentielAccueil = pZH[typeZH].value('surface actuelle')
    pZH[typeZH].setValue('surfaceInitialeDeReferencePourPotentielAccueil', surfaceInitialeDeReferencePourPotentielAccueil)
    pZH[typeZH].setValue('surfaceDuSeuilPrécédent_action2',pZH[typeZH].value('surface actuelle'))
    


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
    # print(f"{typeZH}: {i if 'i' in locals() else 0}, startCasesActions2: {startCasesActions2}")
    
    #Ajout des actions2 en plus
    ZHs[typeZH]['Actions2 en plus']=[]
    if ZHs[typeZH].get("cases actions2 en plus") is not None:
        for j, paramCaseAction2 in enumerate(ZHs[typeZH]["cases actions2 en plus"], start=(i if 'i' in locals() else (startCasesActions2 -1))+1):
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
    
    #TEST AJOUT VALUER DS LES PLATEAUX
    if aPZH.getEntity(1,1).value('type') == 'action1':
        # aMonitorOnPotAC = myModel.newDashBoard(backgroundColor=ZHs[aZHtype]["couleur"]) #, borderColor='transparent'
        aMonitorOnPotAC = myModel.newDashBoard(borderSize=0, borderColor= Qt.transparent, backgroundColor=Qt.transparent) #, borderColor='transparent'
        aMonitorOnPotAC.addIndicatorOnEntity(aPZH.getEntity(1,1),'potentiel accueil', displayName=False)
        aMonitorOnPotAC.rightMargin = aMonitorOnPotAC.rightMargin + 5
        aMonitorOnPotAC.moveToCoords(
            aPZH.grid.mapToParent(QPoint(0, 0)).x()+aPZH.grid.size+5,
            aPZH.grid.mapToParent(QPoint(0, 0)).y()+5
            )


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
pionAction1=myModel.newAgentType("Action1","circleAgent",defaultSize=5,)
pionAction1.newPov("joueur","joueur",joueurs_potentiels)

for jX in list(joueurs_actifs.keys()):
    nomJ =""+jX
    Player.addGameAction(myModel.newCreateAction(pionAction1, {"joueur":nomJ},nbPionActions1_parJoueur,
                            conditions=[
                                    lambda aCell: aCell.type != cases and aCell.value('type') == 'action1',
                                        ],
                            create_several_at_each_click = True
                            ))
Player.addGameAction(myModel.newDeleteAction(pionAction1))

nbPionActions2_parJoueur='infinite' #6
pionAction2=myModel.newAgentType("Action2","squareAgent",defaultSize=20,locationInEntity='center')
pionAction2.newPov("joueur","joueur",joueurs_actifs)

for jX in list(joueurs_actifs.keys()):
    nomJ =""+jX
    Player.addGameAction(myModel.newCreateAction(pionAction2, {"joueur":nomJ},nbPionActions2_parJoueur,
                            conditions=[
                                    lambda aCell: aCell.type != cases and aCell.value('type') == 'action2',
                                    lambda aCell: aCell.isEmpty(),
                                    ],
                            feedbacks=[lambda : updateActions2()]))
Player.addGameAction(myModel.newDeleteAction(pionAction2,feedbacks=[lambda : updateActions2()]))


#********************************************************************

def updateActions1():
    for aCase in casesAction1:
        aCase.setValue('frequentation',aCase.nbAgents()) 
        if aCase.nbAgents() > (aCase.value('potentiel accueil') * 1.25):
            aCase.setValue('surfrequentation',1) #0 si la capacité d'accueil n'est pas dépassé  / 1 si la capacité d'accueil est dépassé de plus de 25%
            aCase.grid.gs_aspect.border_color='red'
            aCase.grid.gs_aspect.border_size=6
            aCase.grid.update()

        elif aCase.nbAgents() > aCase.value('potentiel accueil'):
            aCase.setValue('surfrequentation',0.5) #0 si la capacité d'accueil n'est pas dépassé  / 0.5 si la capacité d'accueil est dépassé de moins de 25%
            aCase.grid.gs_aspect.border_color='dark orange'
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
    """Met à jour les actions pour la troisième phase."""
    updateSurfaceAllZH()
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
    """Initialise le début du tour en réinitialisant les entités et en mettant à jour les surfaces."""
    pionAction1.deleteAllEntities()
    pionAction2.deleteAllEntities()
    # Calcul des surfaces actuelles
    updateSurfaceAllZH()
    # Mise à jour des cases Actions1 et des potentiels d'accueil
    for aCase in casesAction1:
            aCase.setValue('surfrequentation',0) #0 si la potentiel d'accueil n'est pas dépassé  / 1 si la potentiel d'accueil est dépassé
            aCase.grid.gs_aspect.border_color='black'
            aCase.grid.gs_aspect.border_size=1
            aCase.grid.update()

            # updatePotentielAccueil
            aTypeZH = aCase.type.name
            
            surfaceInitialeDeReference = aCase.type.value('surfaceInitialeDeReferencePourPotentielAccueil')

            # updateSurfaceZH(aTypeZH)  # Mise à jour de la surface actuelle avec la fonction dédiée #INUTILE ,c'est fait au dessus
            surfaceActuelle = aCase.type.value('surface actuelle')

            if aTypeZH ==  'vasiere nue Diop':
                surfaceActuelle = (surfaceActuelle
                                    + (cases.metricOnEntitiesWithValue('typeZH','demi-herbier Diop','sumAtt', 'surface') / 2)
                                    + cases.metricOnEntitiesWithValue('typeZH','pres sales Diop','sumAtt', 'surface')   ) 

            # Si la surface est 0, le potentiel d'accueil est 0
            if surfaceActuelle == 0:
                aCase.setValue('potentiel accueil', 0)
            else:
                # print(f"{aTypeZH}: potentielAccueil={aCase.value('potentiel accueil')}")
                # print(f"{aTypeZH}: InitialValue={aCase.getInitialValue('potentiel accueil')}")
                aCase.setValue('potentiel accueil',
                           round(aCase.getInitialValue('potentiel accueil') * surfaceActuelle / surfaceInitialeDeReference))                
                # print(f"{aTypeZH}: surfaceInitialeDeReference={surfaceInitialeDeReference}, surfaceActuelle={surfaceActuelle}, potentielAccueil={aCase.value('potentiel accueil')}")

    # Mise à jour des actions2
    for typeZH, zhData in ZHs.items():
        if typeZH in ['demi-herbier', 'mer', 'vide','pres sales Diop','demi-herbier Diop']: continue
        surfaceActuelle = pZH[typeZH].value('surface actuelle')
        seuilVariation = zhData.get("seuil variation actions2", float('inf'))
        
        # Première boucle pour gérer l'ajout de Cases Action 2. Cas où surfaceActuelle >= surfaceDuSeuilPrécédent_action2 + seuilVariation
        while surfaceActuelle >= pZH[typeZH].value("surfaceDuSeuilPrécédent_action2") + seuilVariation:
            pZH[typeZH].incValue("surfaceDuSeuilPrécédent_action2", seuilVariation)
            if ZHs[typeZH]['Actions2 en plus'] == []: break # sort de la boucle, si il n'y a plus de case actions2 en plus
            casesEnPlus = ZHs[typeZH]['Actions2 en plus'][0]
            pZH[typeZH].reviveThisCell(casesEnPlus)
            ZHs[typeZH]['Actions2 en plus'].remove(casesEnPlus)
            # casesEnPlus.gs_aspect.border_color='red'
            # casesEnPlus.gs_aspect.border_size=4
                 
        # Deuxième boucle while pour gérer la suppression de Cases Action 2. Cas où surfaceActuelle <= (surfaceDuSeuilPrécédent_action2 + seuilVariation)
        while (pZH[typeZH].value("surfaceDuSeuilPrécédent_action2") - surfaceActuelle) >= seuilVariation:
            pZH[typeZH].decValue("surfaceDuSeuilPrécédent_action2", seuilVariation)
            casesActions2_actives = pZH[typeZH].getEntities_withValue("type", "action2")
            if surfaceActuelle == 0 and casesActions2_actives == []:  break # sort de la boucle, si il n'y a plus de case actions2 à enlever
            if surfaceActuelle > 0 and len(casesActions2_actives) == 1: break # sort de la boucle si il reste de la superficie et que la liste contient un élément 
            # Récupérer la dernière case à enlever
            caseX = casesActions2_actives[-1] #récupère la dernière case action2 active
            pZH[typeZH].deleteEntity(caseX)
            ZHs[typeZH]['Actions2 en plus'].insert(0, caseX)  # Ajoute caseX au début de la liste


        # Mise à jour des plateaux inactifs
        if pZH[typeZH].value('surface actuelle') == 0:
            pZH[typeZH].grid.isActive = False
        else:
            pZH[typeZH].grid.isActive = True
        
    # Réinitialisation des variables de simulation
    ptCB.setValue(0)
    ptDE.setValue(0)
    perc_ptCB_sequestrationZH.setValue(0)
    sequestrationTot.setValue(sequestrationZH.getValue())

#********************************************************************

PlayerControlPanel = Player.newControlPanel("Actions")
PlayerControlPanel.moveToCoords(1340,30)

myModel.setCurrentPlayer("Player")

#********************************************************************

myModel.displayTimeInWindowTitle()
modelPhase1=myModel.newModelPhase([lambda: initDebutTour()],auto_forward=True,message_auto_forward=False)
PlayPhase2=myModel.newPlayPhase("Jouer",[Player],show_message_box_at_start=False)
modelPhase3=myModel.newModelPhase([lambda: updateActions1(),lambda: updateActions3(),lambda: calcSequestrationTot(),lambda: calcCumulDE()],name='Bilan du tour')


#********************************************************************
# Dashboard des scores obtenus
DashBoardInd=myModel.newDashBoard("Suivi d'indicateurs ")
DashBoardInd.addIndicatorOnSimVariable(sequestrationZH)
DashBoardInd.addSeparator()                                  
DashBoardInd.addIndicatorOnSimVariable(ptCB)
DashBoardInd.addIndicatorOnSimVariable(perc_ptCB_sequestrationZH)
DashBoardInd.addSeparator()
DashBoardInd.addIndicatorOnSimVariable(sequestrationTot)
DashBoardInd.addSeparator()
DashBoardInd.addIndicatorOnSimVariable(ptDE)
DashBoardInd.addIndicatorOnSimVariable(cumulDE)
DashBoardInd.moveToCoords(1175,705)

#********************************************************************

# Dashboard des surfaces des ZH
DashBoardSurfaces = myModel.newDashBoard("Surfaces")

for typeZH in ZHs.keys():
        if typeZH in ['demi-herbier', 'demi-herbier Diop', 'mer', 'vide']: continue
        if typeZH in ['pres sales Diop']:
            aMetricIndicator = DashBoardSurfaces.addIndicator_Sum(cases, "surface", typeZH, conditionsOnEntities=[(lambda case, typeZH=typeZH: case.value("typeZH") == typeZH)])
        else:
            aMetricIndicator = DashBoardSurfaces.addIndicatorOnEntity(pZH[typeZH],'surface actuelle',title=typeZH)

DashBoardSurfaces.moveToCoords(1520,30)

#********************************************************************
# Dashboard des potentiel d'accueil des ZH
# DashBoardPotAccueil = myModel.newDashBoard("Potentiel accueil")
# for aCaseAction in casesAction1:
#     aTypeZH = aCaseAction.type.name
#     aInd = DashBoardPotAccueil.addIndicatorOnEntity(aCaseAction,'potentiel accueil',title=aCaseAction.type.name)

#     if surfaceInitiales[aTypeZH] == 0 and aTypeZH not in ['port plaisance','foret','herbier']:
#          aInd.setResult(0)
# DashBoardPotAccueil.moveToCoords(1510,400)


#********************************************************************
#BUTTON POUR LES CARTES DE CHGT DE LAND USE
nbBonusAmenage = myModel.newSimVariable(' Bonus déjà utilisés   ',0)
dashBonus = myModel.newDashBoard(backgroundColor='#afe3d7', borderColor='transparent')
dashBonus.addIndicatorOnSimVariable(nbBonusAmenage)
dashBonus.moveToCoords(1000,802)
myModel.newButton(
    (lambda: bonusAmenagemet()),
    f"Bonus 10ha \nd'aménagement ({coutBonusAmenage} DE)",
    (1000,750),
    padding=10,
    background_color='#afe3d7'
)
def bonusAmenagemet():
    cumulDE.decValue(coutBonusAmenage)
    nbBonusAmenage.incValue()

def ajoutDE():
    number, ok = QInputDialog.getInt(None, 'Points DE',f"Nb de pts DE à ajouter (à retrancher si nombre négatif)", 0)
    if ok:
        cumulDE.incValue(number)
        
myModel.newButton(
    (lambda: ajoutDE()),
    f"Ajout/Retrait des points DE)",
    (1000,832),
    padding=8,
    background_color='#afe3d7'
)


#********************************************************************
 #TEST AJOUT VALUER DS LES PLATEAUX
 
# for i, aZHtype in enumerate(ordreZHs):
#     if aPZH.getEntity(1,1).value('type') == 'action1':
#         print('ici')
#         # aMonitorOnPotAC = myModel.newDashBoard(backgroundColor=ZHs[aZHtype]["couleur"]) #, borderColor='transparent'
#         aMonitorOnPotAC = myModel.newDashBoard(borderSize=0, borderColor= Qt.transparent, backgroundColor=Qt.transparent) #, borderColor='transparent'
#         aMonitorOnPotAC.addIndicatorOnEntity(aPZH.getEntity(1,1),'potentiel accueil', displayName=False)

# # dashboardSOLO = myModel.newDashBoard(borderSize=0, borderColor= Qt.transparent, backgroundColor=Qt.transparent)
# # dashboardSOLO.addIndicatorOnEntity(casesAction1[0],'potentiel accueil', displayName=False)
# # dashboardSOLO.moveToCoords(1080,145)



#         # aMonitorOnPotAC.addSeparator()                               
#         # aMonitorOnPotAC.addIndicatorOnEntity(aPZH.getEntity(1,1),'potentiel accueil')
#         # aMonitorOnPotAC.addSeparator()
#         #         aMonitorOnPotAC.moveToCoords((posX+5,listPosY[num_col]+10))                            
#         # aMonitorOnPotAC.moveToCoords((aPZH.grid.size + 10, aPZH.grid.size))
#         # aMonitorOnPotAC.moveToCoords(posX+30,listPosY[num_col]+10)
#         aMonitorOnPotAC.moveToCoords(aPZH.getEntity(1,1).mapToGlobal(QPoint(0, 0)).x()+30,aPZH.getEntity(1,1).mapToGlobal(QPoint(0, 0)).y()+10)

# Dashboard SOLO - TEST -->  IL FAUDRAIT AFFFICHER PLUTOT LE NOMBRE D'AGENTS (et pas le potentiel d'accueil), 
#           Et donc créé un attribut 'nbPions' qui est mis à jour à chaque pose de pion
# dashboardSOLO = myModel.newDashBoard(borderSize=0, borderColor= Qt.transparent, backgroundColor=Qt.transparent)
# dashboardSOLO.addIndicatorOnEntity(casesAction1[0],'potentiel accueil', displayName=False)
# dashboardSOLO.moveToCoords(1080,145)

#### Autre tentative###

        #ajout d'un dashbord sur le potentiel accueil'
        # aMonitorOnPotAC = myModel.newDashBoard(backgroundColor=ZHs[typeZH]["couleur"], borderColor='transparent')
        # aMonitorOnPotAC.addIndicatorOnEntity(case1,'potentiel accueil')
        # aMonitorOnPotAC.moveToCoords(1070,852)


#********************************************************************
# lancement de méthodes de mise à jour à l'ouverture de l'application

# updateSurfaceAllZH()
updateActions3()
# initDebutTour()
calcSequestrationTot()


#********************************************************************
# lancement de l'application

myModel.launch()
# myModel.launch_withMQTT("Instantaneous")
sys.exit(monApp.exec_())