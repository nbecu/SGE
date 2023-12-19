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
