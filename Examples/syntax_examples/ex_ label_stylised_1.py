import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
import random
import string

monApp = QtWidgets.QApplication([])


myModel = SGModel(350, 150)


# Exemple d'utilisation
myModel.newLabel_stylised("This is a test", (50, 50),
                          font="Courier New", size=22, color="red", text_decoration="none", font_weight="normal", font_style="normal",
                          border_style="dotted", border_size=4, border_color="rgba(154, 20, 8, 0.5)",
                          background_color="#8A2BE2")


myModel.newLabel_stylised("This is a second test", (50, 100),
                          size=12,
                          background_color="yellow")


myModel.launch()
sys.exit(monApp.exec_())

