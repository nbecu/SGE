import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(1000, 800, windowTitle="TextBox Font Size Test")


# Test text content
testText = "Font Style Test:\nLine 1\nLine 2\nLine 3\nLine 4\nLine 5"

# Create TextBox with Arial font size 12 - Title left aligned (default)
textBox1 = myModel.newTextBox(
    testText,
    title="1. Arial 12 Left",
    titleAlignment='left'
)
textBox1.setTextFormat(fontName="Arial", size=12)
textBox1.moveToCoords(10, 30)

# Create TextBox with Times New Roman font size 12 - Title centered
textBox2 = myModel.newTextBox(
    testText,
    title="2. Times New Roman 12 Center",
    titleAlignment='center'
)
textBox2.setTextFormat(fontName="Times New Roman", size=12)
textBox2.moveToCoords(250, 30)

# Create TextBox with Verdana font size 12 - Title right aligned
textBox3 = myModel.newTextBox(
    testText,
    title="3. Verdana 12 Right",
    titleAlignment='right'
)
textBox3.setTextFormat(fontName="Verdana", size=12)
textBox3.moveToCoords(490, 30)

# Create TextBox with different sizes of same font - All centered for comparison
textBox4 = myModel.newTextBox(
    testText,
    title="4. Arial 10 Center",
    titleAlignment='center'
)
textBox4.setTextFormat(fontName="Arial", size=10)
textBox4.moveToCoords(10, 180)

textBox5 = myModel.newTextBox(
    testText,
    title="5. Arial 16 Center",
    titleAlignment='center'
)
textBox5.setTextFormat(fontName="Arial", size=16)
textBox5.moveToCoords(250, 180)

textBox6 = myModel.newTextBox(
    testText,
    title="6. Arial 20 Center",
    titleAlignment='center'
)
textBox6.setTextFormat(fontName="Arial", size=20)
textBox6.moveToCoords(490, 180)


myModel.launch()
sys.exit(monApp.exec_())
