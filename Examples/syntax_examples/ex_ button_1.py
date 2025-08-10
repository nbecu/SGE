import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])


myModel = SGModel(350, 250)

myModel.newButton(lambda:print(10),'Click me',(70,80))


def button2Clicked():
    print(20)
myModel.newButton(button2Clicked,'Click me 2',(70,140))



myModel.launch()
sys.exit(monApp.exec_())

