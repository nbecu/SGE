import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGCircularDiagram import SGCircularDiagram

# Initialisation des données
data = [0.2, 0.8]  # Pourcentage de chaque section
colors = ['green', 'orange']  # Couleurs des sections
labels = ['Model 1', 'Model 2']  # Libellés des sections

monApp = SGCircularDiagram(data, labels, colors)
monApp.display()


# Très bien egalement.

# Après réflexion, j'ai pensé également à un quatrième type de Graphique qui est le Stackplots (c'est dispo dans la librairie matplotlib)
# Le type de graphique Stackplots serai utile dans le cas d'attributs au format 'string' dont on voudrait montrer l'évolution de la répartition au sein de la population d'un type d'entitié
# Dans l'exemple 8 (exStep8.py) ca permettrait de faire un graphique qui montre l'évolution au cours des tours de la proportiopn  de cells dont l'attribut landUse est égal à 'shrub', à 'grass' ou à 'forest' (un peu comme sur la page de démo de matplotlib avec oceanie, europe, asia, americs et africa  : https://matplotlib.org/stable/gallery/lines_bars_and_markers/stackplot_demo.html#sphx-glr-gallery-lines-bars-and-markers-stackplot-demo-py)