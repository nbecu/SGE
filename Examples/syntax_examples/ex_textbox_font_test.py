import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(1000, 800, windowTitle="TextBox Font Size Test")

# Create a simple grid for reference
squareCell = myModel.newCellsOnGrid(3, 3, "square", name="TestGrid", size=40, gap=5)
squareCell.setEntities("terrain", "grass")
squareCell.newPov("base", "terrain", {
    "grass": Qt.green
})

# Test text content
testText = "Font Style Test:\nLine 1\nLine 2\nLine 3\nLine 4\nLine 5"

# Create TextBox with Arial font size 12
textBox1 = myModel.newTextBox(
    testText,
    title="1. Arial 12"
)
textBox1.setTextFormat(fontName="Arial", size=12)

# Create TextBox with Times New Roman font size 12
textBox2 = myModel.newTextBox(
    testText,
    title="2. Times New Roman 12"
)
textBox2.setTextFormat(fontName="Times New Roman", size=12)

# Create TextBox with Verdana font size 12
textBox3 = myModel.newTextBox(
    testText,
    title="3. Verdana 12"
)
textBox3.setTextFormat(fontName="Verdana", size=12)

# Create TextBox with different sizes of same font
textBox4 = myModel.newTextBox(
    testText,
    title="4. Arial 10"
)
textBox4.setTextFormat(fontName="Arial", size=10)

textBox5 = myModel.newTextBox(
    testText,
    title="5. Arial 16"
)
textBox5.setTextFormat(fontName="Arial", size=16)

textBox6 = myModel.newTextBox(
    testText,
    title="6. Arial 20"
)
textBox6.setTextFormat(fontName="Arial", size=20)

# Test with long text that causes automatic line wrapping
longText1 = "This is a very long text that should cause automatic line wrapping when the TextBox width is not sufficient to display all the text on a single line. This text is much longer than the previous test text and should trigger word wrapping behavior in the TextBox widget."

textBox7 = myModel.newTextBox(
    longText1,
    title="7. Long Text Arial 12",
    sizeY=150
)
textBox7.setTextFormat(fontName="Arial", size=12)

longText2 = "Another extremely long text example with different content that will definitely cause automatic line wrapping. This text contains multiple sentences and should demonstrate how the height calculation handles text that wraps to multiple lines automatically due to width constraints."

textBox8 = myModel.newTextBox(
    longText2,
    title="8. Long Text Arial 14"
)
textBox8.setTextFormat(fontName="Arial", size=14)

longText3 = "This is the third long text example with even more content to test the word wrapping behavior. The text is intentionally very long to force automatic line breaks and see if the height calculation accounts for these wrapped lines properly."

textBox9 = myModel.newTextBox(
    longText3,
    title="9. Long Text Arial 16"
)
textBox9.setTextFormat(fontName="Arial", size=16)

# Create a legend
aLegend = myModel.newLegend()

# Create instructions
instructions = myModel.newTextBox(
    "TextBox Height Test - Report format:\n"
    "Use: 'Box X: OK' or 'Box X: rogné haut' or 'Box X: rogné bas' or 'Box X: rogné haut+bas'\n"
    "Example: 'Box 1: OK, Box 2: rogné bas, Box 3: rogné haut+bas'\n"
    "Test Box 7-9 for long text wrapping behavior.",
    title="Instructions"
)
instructions.setTextFormat(fontName="Arial", size=12)

myModel.launch()
sys.exit(monApp.exec_())
