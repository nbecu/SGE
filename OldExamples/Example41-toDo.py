import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of rework POVS CEll


myModel=SGModel(1080,960,"grid")

theFirstGrid=myModel.createGrid("basicGrid",10,10,"square")
theFirstGrid.setColor(Qt.gray) 

myModel.setUpPovOn("Forester",{"Forest":{"Niv3":Qt.green,"Niv2":Qt.red,"Niv1":Qt.yellow},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},[theFirstGrid],"sea","reasonable")
# Par ailleurs, il me semble que ce setUpCellValueAndPovce devrait s'appliquer sur une grid , et pas sur le modèle, non ?
# Enfaite c'est deja le cas ( je l'applique sur le model afin de pouvoir appliquer une pov sur plusieurs grille )
# Et je pense qu'il est important d'avoir aussi la possibilité de décomposer la méthode setUpCellValueAndPov  en 2 étapes, d'abord setUpCellValu (juste pour définir les attribuuts ett leurs valeurs), puis setUpPov pour définir  les couleurs associés aux valeurs des attributs 
theFirstGrid.setCellsValue("landUse",{"Forest":{"Niv3":Qt.green,"Niv2":Qt.red,"Niv1":Qt.yellow},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},[theFirstGrid],"sea","reasonable")


myModel.setUpPovOn("Fireman",{"FireRisk":{"Niv2":Qt.black,"Niv1":Qt.gray}},[theFirstGrid])



myModel.setInitialPovGlobal("Forester")

theFirstGrid.setForRandom({"Forest":"Niv3"},30)
theFirstGrid.setForXandY({"Forest":"Niv3"},1,1)





myModel.newAgent("lac","circleAgent",[theFirstGrid])

myModel.setUpPovOn("Forester",{"Forest":{"Niv3":Qt.green,"Niv2":Qt.red,"Niv1":Qt.yellow},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},"lac","sea","reasonable",[theFirstGrid])
## meme remarque que pour attribut et pov des cellule

theFirstLegend=myModel.createLegendAdmin()
theFirstLegend.addDeleteButton()



theSecondLegend=myModel.createLegendForPlayer("theTestLegend",{"basicGrid":{"Forester":{"Forest":{"Niv3":Qt.green}}}})
#faudrait ajouteer un initulé en haut de la légende (par défaut ce serai Forester ou admin, mais le modeler pourrait aussi spécifier un intitulé custom )
theSecondLegend.addToTheLegend({"basicGrid":{"Forester":{"Forest":{"Niv2":Qt.red}}}})
theSecondLegend.addAgentToTheLegend("lac")


theFirstGrid.addOnXandY("lac",1,1)
theFirstGrid.addOnXandY("lac",2,2)
theFirstGrid.addOnXandY("lac",7,7)
theFirstGrid.addOnXandY("lac",4,2)
theFirstGrid.addOnXandY("lac",10,9)
theFirstGrid.addOnXandY("lac",1,8)



myModel.show() 

sys.exit(monApp.exec_())
