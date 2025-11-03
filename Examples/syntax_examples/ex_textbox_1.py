import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(1000, 800, windowTitle="Shrinkable TextBox")


# Test text content
testText = "Font Style Test:\nLine 1\nLine 2\nLine 3\nLine 4\nLine 5"
longText = "This is a very long text that should exceed the maximum height and trigger a scrollbar.\n" * 10


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
    longText,
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

# Test with width specified (shrinked=True)
textBox7 = myModel.newTextBox(
    testText,
    title="7. Width 200",
    titleAlignment='left',
    width=200
)
textBox7.setTextFormat(fontName="Arial", size=12)
textBox7.moveToCoords(10, 330)

# Test with height specified (shrinked=True, height becomes max)
textBox8 = myModel.newTextBox(
    testText,
    title="8. Height 300 Max",
    titleAlignment='center',
    height=300
)
textBox8.setTextFormat(fontName="Arial", size=12)
textBox8.moveToCoords(250, 330)

# Test with both width and height specified (shrinked=True)
textBox9 = myModel.newTextBox(
    testText,
    title="9. Width 180 Height 250",
    titleAlignment='right',
    width=180,
    height=250
)
textBox9.setTextFormat(fontName="Arial", size=12)
textBox9.moveToCoords(490, 330)

# Test with very long text to test scrollbar when exceeding max height
textBox10 = myModel.newTextBox(
    longText,
    title="10. Long Text Height 200",
    titleAlignment='left',
    height=200
)
textBox10.setTextFormat(fontName="Arial", size=12)
textBox10.moveToCoords(10, 480)

# Test with wide title that will be cropped (width specified)
textBox11 = myModel.newTextBox(
    testText,
    title="11. Very Long Title That Will Be Cropped",
    titleAlignment='center',
    width=150
)
textBox11.setTextFormat(fontName="Arial", size=12)
textBox11.moveToCoords(250, 480)

# Test with wide title that will be cropped (width specified, default alignment)
textBox12 = myModel.newTextBox(
    testText,
    title="12. Very Long Title That Will Be Cropped",
    width=150
)
textBox12.setTextFormat(fontName="Arial", size=12)
textBox12.moveToCoords(490, 480)


myModel.launch()
sys.exit(monApp.exec_())
