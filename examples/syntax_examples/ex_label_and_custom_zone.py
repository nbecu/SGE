import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

from mainClasses.SGCustomZone import*
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

# Style 2
myModel.newLabel(text, (30, 30), textStyle_specs2, borderStyle_specs2, backgroundColor_specs2,
                  fixedWidth=fixed_width,
                  alignement="Right")  

# Création d'une instance de CustomZone
zone = SGCustomZone(myModel,background_color="lightblue", border_color="darkblue", border_size=8, text_style="Arial")
zone.setGeometry(350, 80, 300, 200)

# Ajout d'éléments à la zone
zone.add_text("Hello, World!", (10, 30))
zone.add_text("Colored text", (10, 50),Qt.green)

zone.add_image("icon/MTZC/bovin.png", (10, 60))
zone.add_shape("rectangle", (10, 130), (100, 50))  # (x, y, width, height)
zone.add_shape("triangle", (150, 100), (100, 50))  # (x, y, size)



myModel.launch()
sys.exit(monApp.exec_())

