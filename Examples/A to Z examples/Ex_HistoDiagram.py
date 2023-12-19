import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGHistogramDiagram import SGHistogramDiagram
import numpy as np

# Initialisation des données

dataModel1 = np.random.rand(100)
dataModel2 = np.random.rand(100)
dataModel3 = np.random.rand(100)

arr_dataModel = [dataModel1, dataModel2, dataModel3]
arr_labels = ['Model 1', 'Model 2', 'Model 3']
title = "Exemple de simulation avec un Histogramme"
xLabel = "Valeurs"
yLabel = "Fréquences"

monApp = SGHistogramDiagram(arr_dataModel, arr_labels, title, xLabel, yLabel)
monApp.display()
