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

# Très bien également cet exemple mais par contre faudrait trouvr le moyen pour que le Y-max ne soit pas actualisé tout le temps.
# Par exemple il pourrait soit ettre fixé par une valeur donné par l'utilisateur, soit être fixé automatiquement  à 150% de la valeur maximum atteinte,, puis reactualisé que si cette valeur est dépassé
