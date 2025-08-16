import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="How to use modelAction - example 7")

Cell=myModel.newCellsOnGrid(10,10,"square",size=40, gap=2,name='mygrid')
Cell.setEntities("landUse","grass")
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)
Cell.newPov("mainPov","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})


phase1 = myModel.timeManager.newModelPhase()
phase1.addAction([lambda: Cell.setRandomEntities("landUse","shrub",3),lambda: Cell.setRandomEntities("landUse","forest")])

myModel.timeManager.newModelPhase([lambda: Cell.setRandomEntities("landUse","forest"),lambda: Cell.setRandomEntities("landUse","shrub",3)])

aModelAction2 =myModel.newModelAction(lambda: Cell.setRandomEntities("landUse","grass",2))
myModel.timeManager.newModelPhase(aModelAction2)
aModelAction2.addCondition(lambda: Cell.nb_withValue("landUse","forest") >10) 

myModel.newTimeLabel()

myModel.launch() 

sys.exit(monApp.exec_())
