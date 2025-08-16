import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
import random

monApp = QtWidgets.QApplication([])


myModel = SGModel(750, 350)



textStyle_specs1 = "font-family: Papyrus; font-size: 26px; color: blue; text-decoration: blink; font-weight: 300; font-style: normal;"
borderStyle_specs1 = "border: 4px inset magenta;"
backgroundColor_specs1 = "background-color: cyan;"

textStyle_specs2 = "font-family: Comic Sans MS; font-size: 33px; color: yellow; text-decoration: line-through; font-weight: lighter; font-style: normal;"
borderStyle_specs2 = "border: 5px dashed gold;"
backgroundColor_specs2 = "background-color: teal;"

textStyle_specs3 = "font-family: Papyrus; font-size: 16px; color: rgb(0, 255, 0); text-decoration: blink; font-weight: lighter; font-style: oblique;"
borderStyle_specs3 = "border: 5px inset orange;"
backgroundColor_specs3 = "background-color: black;"

textStyle_specs4 = 'font-family: Comic Sans MS; font-size: 17px; color: brown; text-decoration: none; font-weight: normal; font-style: italic;'
borderStyle_specs4 = 'border: 4px double rgba(154, 20, 8, 0.5);'
backgroundColor_specs4 = 'background-color: pink;'

text = 'This is a text in a label'
fixed_width = 300
# Application des styles et positions différents pour chaque label
# Style 1
myModel.newLabel(text, (30, 30), textStyle_specs1, borderStyle_specs1, backgroundColor_specs1,
                  fixedWidth=fixed_width)  
# Style 2
myModel.newLabel(text, (300, 30), textStyle_specs2, borderStyle_specs2, backgroundColor_specs2,
                  alignement="Right",
                  fixedWidth=fixed_width)  
# Style 3
myModel.newLabel(text, (30, 200), textStyle_specs3, borderStyle_specs3, backgroundColor_specs3,
                 alignement="Center",
                 fixedWidth=fixed_width,
                 fixedHeight=50)  
# Style 4
myModel.newLabel(text, (300, 200), textStyle_specs4, borderStyle_specs4, backgroundColor_specs4,
                 alignement="VCenter",
                 fixedWidth=fixed_width)  



myModel.launch()
sys.exit(monApp.exec_())

