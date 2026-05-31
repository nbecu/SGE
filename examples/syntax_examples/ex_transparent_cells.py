"""
Diagnostic example: transparent cells over a background image.

Grid 6x6 with backgroundImage.
- "terrain" cells  → Qt.green   (opaque)
- "vide" cells     → Qt.transparent

Expected behaviour: "vide" cells should show the board image underneath.
Click a "vide" cell to turn it into "terrain" (and vice-versa) to verify
that the CellView is still present and interactive when transparent.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(600, 500,
    windowTitle="Transparent cells diagnostic — green=terrain, transparent=vide")

Cell = myModel.newCellsOnGrid(16, 16, "square", size=60, gap=20,
                              backgroundImage="./icon/MTZC/plateau-jeu.jpg")

# Set all cells to "terrain" first, then override a checkerboard pattern to "vide"
Cell.setEntities("type", "terrain")
for x in range(1, 7):
    for y in range(1, 7):
        if (x + y) % 2 == 0:
            Cell.getEntity(x, y).setValue("type", "vide")

# POV: terrain → green, vide → transparent
Cell.newPov("vue", "type", {
    "terrain":  Qt.green,
    "vide":     Qt.transparent,
})

# Click a "vide" cell to turn it into "terrain" — tests that transparent cells
# remain interactive even when hidden.
Player = myModel.newPlayer("Player")
Player.addGameAction(myModel.newModifyAction(Cell, {"type": "terrain"}))
Player.addGameAction(myModel.newModifyAction(Cell, {"type": "vide"}))

Player.newControlPanel()

myModel.launch()
sys.exit(monApp.exec())
