import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
import random

monApp = QtWidgets.QApplication([])

myModel = SGModel(600, 400)

# Button with short text (reference)
myModel.newButton((lambda: buttonClicked()), 'Short text', (50, 50),
                  background_color='lightblue',
                  border_size=2,
                  border_color='blue',
                  border_radius=5)

# Button with long text without size constraints
myModel.newButton((lambda: buttonClicked()), 'This is a very long text that will exceed the normal button limits', (50, 100),
                  background_color='lightgreen',
                  border_size=2,
                  border_color='green',
                  border_radius=5)

# Button with long text and word wrapping enabled
myModel.newButton((lambda: buttonClicked()), 'This is a very long text that will wrap to multiple lines when word_wrap is enabled', (50, 150),
                  background_color='lightcyan',
                  border_size=2,
                  border_color='teal',
                  border_radius=5,
                  word_wrap=True,
                  min_width=200)

# Button with long text, word wrapping and fixed width
myModel.newButton((lambda: buttonClicked()), 'This text will wrap within a fixed width of 150 pixels', (50, 250),
                  background_color='lightgoldenrodyellow',
                  border_size=2,
                  border_color='gold',
                  border_radius=5,
                  word_wrap=True,
                  fixed_width=150)

def buttonClicked():
    print("Button clicked!")

myModel.launch()
sys.exit(monApp.exec_())
