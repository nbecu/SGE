import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(700,600, windowTitle="Multiple symbologies - Background and border styling")

Cell = myModel.newCellsOnGrid(10, 10, "square", size=50)
Cell.setEntities("landUse", "grass")
Cell.setEntities_withColumn("landUse", "forest", 1)
Cell.setEntities_withColumn("landUse", "forest", 2)
Cell.setRandomEntities("landUse", "shrub", 10)

    
#adds a new attribute to the cells
Cell.setEntities("ProtectionLevel", "Free")
Cell.setRandomEntities("ProtectionLevel", "Reserve", 1)


# Symbology allows to specify the visual representation (color, shape, etc.) of cells based on attribute values
# In this example there are two symbologies for the same attribute:
# The first can see the difference between grass and shrub, the second cannot
Cell.newSymbology("landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen}, name="ICanSeeShrub")
Cell.newSymbology("landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen}, name="ICantSeeShrub")

# Symbology for border visualization: first symbology shows only border color
Cell.newSymbology("ProtectionLevel", {
    "Reserve": SGAspect(border_color=Qt.magenta),
    "Free": SGAspect(border_color=Qt.transparent)
}, name="ProtectionLevel_1")

# Second symbology shows both border color and width
Cell.newSymbology("ProtectionLevel", {
    "Reserve": SGAspect(border_color=Qt.magenta, border_size=5),
    "Free": SGAspect(border_color=Qt.black, border_size=1)
}, name="ProtectionLevel_2")

# Display the second symbology (with color and width)
Cell.displaySymbology("ProtectionLevel_2")

myModel.launch() 

sys.exit(monApp.exec())
