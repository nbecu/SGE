import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Simple example
#Declaration du model
myModel=SGModel(1080,960)

#Declaration de la grille
theFirstGrid=myModel.createGrid("basicGrid")

#Declaration d'une POV ( FORESTER ) et assignation d'une valeur par default a toute les cellule
myModel.setUpCellValueAndPov("Forester",{"Forest":{"Niv1":Qt.yellow,"Niv2":Qt.blue,"Niv3":Qt.green}},[theFirstGrid])

#On initie la POV au lancement a FORESTER
myModel.setInitialPovGlobal("Forester")

#On assign une autre valeur a 30 cellule aléatoirement
theFirstGrid.setForRandom({"Forest":"Niv3"},38)

#On ajoute une Legend ADMIN genere automatiquement
myModel.createLegendAdmin()

#On ouvre le model
myModel.show() 

sys.exit(monApp.exec_())