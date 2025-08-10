import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
from mainClasses.SGLabel import *
import random
import string

monApp = QtWidgets.QApplication([])


# myModel = SGModel(400, 400)
myModel = QtWidgets.QMainWindow()

myModel.setFixedHeight(100)
# Exemple d'utilisation
# myModel.newLabel_stylised("This is a test", (50, 50),
#                           font="Courier New", size=22, color="red", text_decoration="none", font_weight="normal", font_style="normal",
#                           border_style="dotted", border_size=4, border_color="rgba(154, 20, 8, 0.5)",
#                           background_color="#8A2BE2")


# myModel.newLabel2("This is a second test", (50, 100),
#                           size=12,
#                           background_color="yellow")
# aLabel = SGLabel3(myModel,'bonjour',border_color="red", border_size=2, border_style='dotted',color="blue")





# aLabel = SGLabel3(aWidg,'bonjour', border_style='dotted',color='blue') #, border_style='dotted', border_color="red", border_style='dotted' )#, )
# aLabel2 = SGLabel3(aWidg,'monsieur', color='red') 
aLabel = QtWidgets.QLabel('bonjour')
aLabel2 = QtWidgets.QLabel('monsieur')


# Ajuster la taille des labels pour qu'ils ne prennent pas trop d'espace
aLabel.setFixedHeight(aLabel.sizeHint().height())
aLabel2.setFixedHeight(aLabel2.sizeHint().height())

layout = QtWidgets.QVBoxLayout()  # Créer un layout vertical
layout.setContentsMargins(0, 0, 0, 0)  # Supprimer les marges autour du layout
layout.setSpacing(-10)  # Définir l'espacement entre les widgets à 0
layout.addWidget(aLabel)   # Ajouter aLabel au layout
layout.addWidget(aLabel2)  # Ajouter aLabel2 au layout


aWidg = QtWidgets.QWidget()
aWidg.setLayout(layout)  # Définir le layout pour aWidg

myModel.setCentralWidget(aWidg)
# aWidg.setParent(myModel)

# aLabel.move(80, 40)

# aWidg.move(10,80)


# launch()

myModel.show()
sys.exit(monApp.exec_())

