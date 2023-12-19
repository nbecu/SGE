import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGLinearDiagram import SGLinearDiagram
import numpy as np

# Initialisation des données
x = np.arange(0, 10, 0.1)
y1 = np.sin(x)
y2 = np.sin(x)
title = "Exemple de simulation avec un diagramme d'évolution des données"
label1 = "Fréquence : Model 1"
label2 = "Fréquence : Model 2"

monApp = SGLinearDiagram(x, y1, y2, label1, label2, title)
monApp.display()