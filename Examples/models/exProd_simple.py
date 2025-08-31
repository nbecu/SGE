import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from mainClasses.SGTestGetData import SGTestGetData
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="Simplistic Production")
myModel.displayTimeInWindowTitle()



## Define Production Units
ProductionUnits=myModel.newCellsOnGrid(1,2,"square",size=45, gap=2, name="Production Unit")
ProductionUnits.setEntities("energy",lambda: random.randint(2,4)*10)

    # Define pov 
aDict = generate_color_gradient(
    QColor.fromRgb(239, 255, 232),QColor.fromRgb(1,50,32),
    mapping={"values": list(range(0, 100, 10)), "value_min": 0, "value_max": 100},
    as_dict=True
)
ProductionUnits.newPov("energy","energy",aDict)


    # Define methods
def produce(aPU):
    if aPU.value('energy') == 100:
        aPU.setValue("energy",20)
    else:
        aPU.incValue("energy",(lambda: random.randint(-1,2)*10),100)
        


## Model actions 

modelAction1=myModel.newModelAction_onCells(lambda aPU: produce(aPU))

myModel.newModelPhase([modelAction1])



## Define other interface widgets
# myModel.newLegend()
# myModel.newTimeLabel("Time", Qt.white, Qt.black, Qt.black)
DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.black)
DashBoard.addIndicator(ProductionUnits,"avgAtt", attribute='energy',color=Qt.black)



DashBoard.showIndicators()



## open the simulation

# dataTest = SGTestGetData(myModel)
# myModel.newModelPhase(lambda:dataTest.getAllDataSinceInitialization())
myModel.launch()
sys.exit(monApp.exec_())