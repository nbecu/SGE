import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from mainClasses.SGTestGetData import SGTestGetData
monApp=QtWidgets.QApplication([])

myModel=SGModel(860,700, windowTitle="Simplistic Production")



## Define Production Units
ProductionUnits=myModel.newCellsOnGrid(1,2,"square",size=45, gap=2, name="Production Unit")
ProductionUnits.setEntities("energy",lambda: random.randint(2,4)*10)

    # Define pov 
def interpolate_color(value_min, value_max, color_min, color_max, a_value):
    # Assurez-vous que la valeur intermédiaire se trouve entre les valeurs min et max
    a_value = max(min(a_value, value_max), value_min)
    # convertir les color_min et color_max en  un format rgb 
    color_min_rgb = QColor(color_min).getRgb()
    color_max_rgb = QColor(color_max).getRgb()
    # Interpoler les composantes RGB
    proportion = (a_value - value_min) / (value_max - value_min)
    aList=[]
    for i in range(0,3):
        aList.append(int(color_min_rgb[i] + proportion * (color_max_rgb[i] - color_min_rgb[i])))
    return QColor(*aList)
aDict={}
for aVal in list(range(0,110,10)):
    aDict[aVal]=interpolate_color(0,100,QColor.fromRgb(239, 255, 232),QColor.fromRgb(1,50,32),aVal) 
ProductionUnits.newPov("energy","energy",aDict)


    # Define methods
def produce(aPU):
    if aPU.value('energy') == 100:
        aPU.setValue("energy",20)
    else:
        aPU.incValue("energy",(lambda: random.randint(-1,2)*10),100)
        


## Model actions 

modelAction1=myModel.newModelAction_onCells(lambda aPU: produce(aPU))

myModel.timeManager.newModelPhase([modelAction1])



## Define other interface widgets
# myModel.newLegend()
# myModel.newTimeLabel("Time", Qt.white, Qt.black, Qt.black)
DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.black)
DashBoard.addIndicator("avgAtt", 'Cell', attribute='energy',color=Qt.black)

DashBoard.showIndicators()



## open the simulation

# dataTest = SGTestGetData(myModel)
# myModel.timeManager.newModelPhase(lambda:dataTest.getAllDataSinceInitialization())
myModel.launch()
sys.exit(monApp.exec_())