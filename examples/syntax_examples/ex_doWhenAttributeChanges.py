import sys
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtGui import QColor

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])
myModel = SGModel(600, 350, windowTitle="doWhenAttributeChanges Example")
myModel.displayTimeInWindowTitle()

# ============================================================================
# Create a simple grid
# ============================================================================
Grid = myModel.newCellsOnGrid(3, 3, "square", size=80, gap=5, name="Grid")
Grid.setEntities("count", 0)

# ============================================================================
# Create a text box to display attribute changes
# ============================================================================
textBox = myModel.newTextBox(width=250, height=200, chronologicalOrder=False, title="Count Changes")
textBox.addText("Click on the cells to increment the count.\nA watcher has been added on the changes of the 'count' attribute.\nWhen the attribute changes, the watcher activates and call the method set by the modeler which adds a text in the text box.")

# ============================================================================
# Example: doWhenAttributeChanges on entity type
# When count attribute changes, add text to textBox
# ============================================================================
def informTextBoxAboutAttributeChanges(cell, attribute):
    """Automatically add text when count changes"""
    count = cell.value('count')
    textBox.addText(f"'count' of cell{cell.getCoords()} has changed.\nNew value is {count}")

Grid.doWhenAttributeChanges("count", informTextBoxAboutAttributeChanges)

# ============================================================================
# Simple action to increment count
# ============================================================================


incrementAction = myModel.newActivateAction(
    Grid, 
    method=lambda cell: cell.incValue("count", 1), 
    label="Increment", 
    action_controler={"directClick": True,"contextMenu": True}
)

Player1 = myModel.newPlayer("Player 1")
Player1.addGameAction(incrementAction)

myModel.newPlayPhase("Turn", [Player1])
myModel.setCurrentPlayer("Player 1")

myModel.launch()
sys.exit(monApp.exec_())
