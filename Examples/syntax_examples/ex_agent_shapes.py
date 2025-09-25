import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGModel import SGModel
from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *

monApp=QtWidgets.QApplication([])
#Example of forms available for agent

myModel=SGModel(1080,960,"Agent examples")

Cells=myModel.newCellsOnGrid(5,2,"square",size=50,color=Qt.gray)

CircleAgent=myModel.newAgentType("Circle","circleAgent")
CircleAgent.newAgentAtCoords(Cells,1,1)

SquareAgent=myModel.newAgentType("Square","squareAgent")
SquareAgent.newAgentAtCoords(Cells,1,2)

Ellipse1Agent=myModel.newAgentType("Ellipse1","ellipseAgent1")
Ellipse1Agent.newAgentAtCoords(Cells,2,1)

Ellipse2Agent=myModel.newAgentType("Ellipse2","ellipseAgent2")
Ellipse2Agent.newAgentAtCoords(Cells,2,2)

Rectangle1Agent=myModel.newAgentType("Rectangle1","rectAgent1")
Rectangle1Agent.newAgentAtCoords(Cells,3,1)

Rectangle2Agent=myModel.newAgentType("Rectangle2","rectAgent2")
Rectangle2Agent.newAgentAtCoords(Cells,3,2)

Triangle1Agent=myModel.newAgentType("Triangle1","triangleAgent1")
Triangle1Agent.newAgentAtCoords(Cells,4,1)

Triangle2Agent=myModel.newAgentType("Triangle2","triangleAgent2")
Triangle2Agent.newAgentAtCoords(Cells,4,2)

Arrow1Agent=myModel.newAgentType("Arrow1","arrowAgent1")
Arrow1Agent.newAgentAtCoords(Cells,5,1)

Arrow2Agent=myModel.newAgentType("Arrow2","arrowAgent2")
Arrow2Agent.newAgentAtCoords(Cells,5,2)

myModel.launch() 

sys.exit(monApp.exec_())
