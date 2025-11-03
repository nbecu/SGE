"""
Test example for SGTextBoxLargeShrinkable - demonstrates compatibility methods.
This example shows how to use addText, setNewText, deleteTitle, and eraseText methods
through interactive buttons.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp = QtWidgets.QApplication([])

# Create model
myModel = SGModel(name="TextBox Update Test", windowTitle="SGTextBoxLargeShrinkable - Update Methods Test")

# Initial test text
initialText = """This is the initial text in the text box.
You can interact with the buttons below to test different update methods.

Try clicking the buttons to see how the text box content changes."""

# Create a text box to test update methods
testTextBox = myModel.newTextBoxLargeShrinkable(
    initialText,
    title="Test TextBox - Click buttons to update",
    width=600,
    height=400,
    titleAlignment='center',
    shrinked=True
)
testTextBox.moveToCoords(10, 30)

# Callback functions for buttons
def addTextSimple():
    """Add text without line break"""
    testTextBox.addText(" [Text added!]")
    print("Added text without line break")

def addTextWithLine():
    """Add text with line break"""
    testTextBox.addText("New paragraph added via addText!", toTheLine=True)
    print("Added text with line break")

def setNewText():
    """Replace all text with new text"""
    newContent = """This is completely new content!
The previous text has been replaced using setNewText().

You can see that all the original content is gone."""
    testTextBox.setNewText(newContent)
    print("Text replaced using setNewText()")

def deleteTitle():
    """Delete the title"""
    testTextBox.deleteTitle()
    print("Title deleted")

def eraseText():
    """Erase the text content"""
    testTextBox.eraseText()
    print("Text content erased")

def resetTextBox():
    """Reset text box to initial state"""
    # Recreate title if deleted
    if not hasattr(testTextBox, 'labelTitle') or testTextBox.labelTitle is None:
        from PyQt5.QtWidgets import QLabel
        testTextBox.labelTitle = QLabel("Test TextBox - Click buttons to update", testTextBox)
        testTextBox.labelTitle.setAlignment(Qt.AlignCenter)
        testTextBox.textLayout.insertWidget(0, testTextBox.labelTitle)
        testTextBox.title = "Test TextBox - Click buttons to update"
    
    # Reset text (widget should still exist since eraseText() doesn't delete it)
    testTextBox.setText(initialText)
    testTextBox.onTextAspectsChanged()
    print("Text box reset to initial state")

# Create buttons to test the methods
myModel.newButton(
    lambda: addTextSimple(),
    "Add Text",
    (650, 30),
    background_color='lightblue',
    border_size=2,
    border_color='blue',
    border_radius=5
)

myModel.newButton(
    lambda: addTextWithLine(),
    "Add Text (New Line)",
    (650, 80),
    background_color='lightgreen',
    border_size=2,
    border_color='green',
    border_radius=5
)

myModel.newButton(
    lambda: setNewText(),
    "Replace Text",
    (650, 130),
    background_color='lightyellow',
    border_size=2,
    border_color='orange',
    border_radius=5
)

myModel.newButton(
    lambda: deleteTitle(),
    "Delete Title",
    (650, 180),
    background_color='lightcoral',
    border_size=2,
    border_color='red',
    border_radius=5
)

myModel.newButton(
    lambda: eraseText(),
    "Erase Text",
    (650, 230),
    background_color='lightpink',
    border_size=2,
    border_color='darkred',
    border_radius=5
)

myModel.newButton(
    lambda: resetTextBox(),
    "Reset",
    (650, 280),
    background_color='lightgray',
    border_size=2,
    border_color='gray',
    border_radius=5
)

# Launch the model
myModel.launch()
sys.exit(monApp.exec_())

