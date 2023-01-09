import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Simple example of suppr agent and placing 

myModel=SGModel(1080,960,"grid")

#On declare deux grilles
theFirstGrid=myModel.createGrid(10,10,"hexagonal",Qt.gray)

theSecondGrid=myModel.createGrid(8,10,"square",Qt.gray)

#Declare une POV Applique aux deux grille 
myModel.setUpEntityValueAndPov("Forester",{"Forest":{"Niv1":Qt.yellow,"Niv2":Qt.red,"Niv3":Qt.green},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},[theFirstGrid,theSecondGrid],"sea","reasonable")
#Initie la pov par default
myModel.setInitialPov("Forester")

#Applique certaine valeur a des case de la premiere grille
theFirstGrid.setForRandom({"Forest":"Niv1"},30)

theFirstGrid.setForRandom({"Forest":"Niv2"},4)

#On declare un nouveau model d'agent/ pion positionable sur les deux grilles
anAgentLac=myModel.newAgent("lac","circleAgent",[theFirstGrid,theSecondGrid])
#On initie une pov pour ce dit agent
myModel.setUpEntityValueAndPov("Forester",{"boat":{"new":Qt.blue,"old":Qt.cyan}},"lac","boat","old",[theFirstGrid,theSecondGrid])

#on genere la Legend admin qui a tout les droits 
theFirstLegend=myModel.createLegendAdmin()

#On declare une joueuse qui possederas des GM et cela genereras sa Legend en consequence 
thePlayer=myModel.createPlayer("Gertrude")

#On declare les mecha du joueur

thePlayer.addGameAction(myModel.createCreateAction(theFirstGrid.getACell(),2,{"sea":["reasonable"]}))

thePlayer.addGameAction(myModel.createUpdateAction(theFirstGrid.getACell(),3,{"sea":["deep sea","reasonable"]},[],[lambda aCell: aCell.deleteAgent("lac",1)],[lambda aCell: aCell.checkValue({"Forest":"Niv2"}) ]))

thePlayer.addGameAction(myModel.createDeleteAction(theFirstGrid.getACell(),2,{"sea":["reasonable","deep sea"]}))

#Example plus poussé  de GM
thePlayer.addGameAction(myModel.createCreateAction(anAgentLac,2,{"boat":["old"]},[lambda aCell: aCell.checkValue({"sea":"reasonable"})]  ,  [lambda aCell: aCell.changeValue({"sea": "deep sea"})]  , [lambda aCell: aCell.parent.getCellFromCoordonate(1,1).checkValue({"sea":"reasonable"}) ]))

#On Declare les differentes phase de jeu  
#Phase du jeu du joueur + passage de 3 case en NIV1
myModel.timeManager.addGamePhase("theFirstPhase",0,thePlayer,[lambda: myModel.getGameSpace("basicGrid").setForRandom({"Forest":"Niv1"},3)])
#Seconde phase ( applique uniquement round 2) passage de 3 case en NIV2
myModel.timeManager.addGamePhase("theSecondPhase",1,None,[lambda: myModel.getGameSpace("basicGrid").setForRandom({"Forest":"Niv2"},3)],[lambda: myModel.getTimeManager().isPeer()])
#On fait evoluer la foret et la mer 
myModel.timeManager.addGamePhase("the3hase",2,None,[lambda: myModel.getGameSpace("basicGrid").makeEvolve(["Forest"]),lambda: myModel.getGameSpace("basicGrid").makeDecrease(["sea"])])
#On ajoute des pions lac sur les case de valeur NIV2
myModel.timeManager.addGamePhase("the4Phase",3,None,[lambda: myModel.getGameSpace("basicGrid").addAgentOnValue('lac',{"Forest":"Niv2"})])
#On bouge au hasard les agent lac 
myModel.timeManager.addGamePhase("the5Phase",4,None,[lambda: myModel.getGameSpace("basicGrid").moveRadomlyAgent("lac")])


myModel.show() 

sys.exit(monApp.exec_())
