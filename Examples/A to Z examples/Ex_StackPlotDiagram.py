import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
import numpy as np
from mainClasses.SGStackPlotDiagram import SGStackPlotDiagram

# Initialisation des données

xlabel = "Temps"
ylabel = "Valeurs"
nb_data = 5
ymax = 2
data = [np.zeros(10) for _ in range(nb_data)]
labels = [f'Model {i+1}' for i in range(nb_data)]

title = "Visualisation des données en temps réelle avec un diagramme Stackplot"
monApp = SGStackPlotDiagram(data, labels, xlabel, ylabel, nb_data, ymax, title)
monApp.display()