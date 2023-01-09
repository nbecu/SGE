import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Simple example

myModel=SGModel(1080,960,"grid")

theFirstGrid=myModel.createGrid(10,10,"hexagonal",Qt.gray, name="basicGrid")

theSecondGrid=myModel.createGrid(4,4,"square",Qt.gray)

myModel.setUpEntityValueAndPov("Forester",{"Forest":{"Niv1":Qt.yellow,"Niv2":Qt.red,"Niv3":Qt.green},"sea":{"deep sea":Qt.blue,"reasonable":Qt.cyan}},[theFirstGrid,theSecondGrid],"sea","reasonable")

myModel.setInitialPov("Forester")

theFirstGrid.setForRandom({"Forest":"Niv1"},30)

theFirstGrid.setForRandom({"Forest":"Niv2"},4)

anAgentLac=myModel.newAgent("lac","circleAgent",[theFirstGrid,theSecondGrid])

myModel.setUpEntityValueAndPov("Forester",{"boat":{"new":Qt.blue,"old":Qt.cyan}},"lac","boat","old",[theFirstGrid,theSecondGrid])


theFirstLegend=myModel.createLegendAdmin()

thePlayer=myModel.createPlayer("Gertrude")
"""thePlayer.addGameAction(myModel.createCreateAction(anAgentLac,2,{"boat":["old"]},[lambda aCell: aCell.checkValue({"sea":"reasonable"})]  ,  [lambda aCell: aCell.parent.addOnXandY("lac",1,1) ] ,[lambda aCell: aCell.parent.getCellFromCoordonate(1,1).checkValue({"sea":"reasonable"}) ]  ))"""
thePlayer.addGameAction(myModel.createCreateAction(anAgentLac,2,{"boat":["old"]},[lambda aCell: aCell.checkValue({"sea":"reasonable"})]  ,  [lambda aCell: aCell.changeValue({"sea": "deep sea"})]  , [lambda aCell: aCell.parent.getCellFromCoordonate(1,1).checkValue({"sea":"reasonable"}) ]))
thePlayer.addGameAction(myModel.createCreateAction(theFirstGrid.getACell(),2,{"sea":["reasonable"]}))

thePlayer.addGameAction(myModel.createUpdateAction(theFirstGrid.getACell(),3,{"sea":["deep sea","reasonable"]},[],[lambda aCell: aCell.deleteAgent("lac",1)],[lambda aCell: aCell.checkValue({"Forest":"Niv2"}) ]))

#thePlayer.addGameAction(myModel.createUpdateAction(theFirstGrid.getACell(),3,{"sea":["deep sea","reasonable"]},[],[lambda aCell: aCell.deleteAgent("lac",1)]))
thePlayer.addGameAction(myModel.createUpdateAction(anAgentLac,2,{"boat":["new"]}))

thePlayer.addGameAction(myModel.createDeleteAction(theFirstGrid.getACell(),2,{"sea":["reasonable","deep sea"]}))

myModel.timeManager.addGamePhase("theFirstPhase",0,thePlayer,[lambda: myModel.getGameSpace("basicGrid").setForRandom({"Forest":"Niv1"},3)])

myModel.timeManager.addGamePhase("theSecondPhase",1,None,[lambda: myModel.getGameSpace("basicGrid").setForRandom({"Forest":"Niv2"},3)],[lambda: myModel.getTimeManager().verifNumberOfRound(3)])

myModel.timeManager.addGamePhase("theThirdPhase",2,None,[lambda: myModel.getGameSpace("basicGrid").setForRandom({"Forest":"Niv3"},10)],[lambda: myModel.getTimeManager().actualRound ==1])

# myModel.timeManager.addGamePhase("theFourthPhase",4,None,[lambda: myModel.getGameSpace("basicGrid").makeEvolve(["Forest"]),lambda: myModel.getGameSpace("basicGrid").makeDecrease(["sea"])])

myModel.timeManager.addGamePhase("the5Phase",5,None,[lambda: myModel.getGameSpace("basicGrid").addAgentOnValue('lac',{"Forest":"Niv2"})])

myModel.timeManager.addGamePhase("the6Phase",6,None,[lambda: myModel.getGameSpace("basicGrid").moveRadomlyAgent("lac")])

myModel.timeManager.addGamePhase("the7Phase",7,None,[lambda: myModel.getGameSpace("basicGrid").deleteAgent("lac")])

myModel.iAm("Gertrude")
myModel.show() 

sys.exit(monApp.exec_())
