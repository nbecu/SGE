import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(1000, 800, windowTitle="TextBox Font Size Test")


# Test text content
testText = "Font Style Test:\nLine 1\nLine 2\nLine 3\nLine 4\nLine 5"

# Create TextBox with Arial font size 12 - Title left aligned (default)
textBox1 = myModel.newTextBoxLarge(
    testText,
    title="1. Arial 12 Left",
    titleAlignment='left'
)
textBox1.setTextFormat(fontName="Arial", size=12)
textBox1.setTitleFormat(fontName="Arial", size=14)  # Title: Arial 14
textBox1.text1_aspect.color = Qt.darkBlue  # Text: dark blue
textBox1.onTextAspectsChanged()
textBox1.moveToCoords(10, 30)

# Create TextBox with Times New Roman font size 12 - Title centered
textBox2 = myModel.newTextBoxLarge(
    testText,
    title="2. Times New Roman 12 Center",
    titleAlignment='center'
)
textBox2.setTextFormat(fontName="Times New Roman", size=12)
textBox2.setTitleFormat(fontName="Georgia", size=16)  # Title: Georgia 16 bold
textBox2.title1_aspect.font_weight = "bold"
textBox2.title1_aspect.color = Qt.darkBlue
textBox2.onTextAspectsChanged()
textBox2.moveToCoords(250, 30)

# Create TextBox with Verdana font size 12 - Title right aligned
textBox3 = myModel.newTextBoxLarge(
    testText,
    title="3. Verdana 12 Right",
    titleAlignment='right'
)
textBox3.setTextFormat(fontName="Verdana", size=12)
textBox3.setTitleFormat(fontName="Verdana", size=18)  # Title: Verdana 18 italic
textBox3.title1_aspect.font_style = "italic"
textBox3.title1_aspect.color = Qt.darkGreen
textBox3.text1_aspect.color = Qt.darkGreen  # Text: dark green
textBox3.onTextAspectsChanged()
textBox3.moveToCoords(490, 30)

# Create TextBox with different sizes of same font - All centered for comparison
textBox4 = myModel.newTextBoxLarge(
    testText,
    title="4. Arial 10 Center",
    titleAlignment='center'
)
textBox4.setTextFormat(fontName="Arial", size=10)
textBox4.setTitleFormat(fontName="Arial", size=12)  # Title: Arial 12
textBox4.moveToCoords(10, 180)

textBox5 = myModel.newTextBoxLarge(
    testText,
    title="5. Arial 16 Center",
    titleAlignment='center'
)
textBox5.setTextFormat(fontName="Arial", size=16)
textBox5.setTitleFormat(fontName="Times New Roman", size=18)  # Title: Times New Roman 18 bold
textBox5.title1_aspect.font_weight = "bold"
textBox5.title1_aspect.text_decoration = "underline"
textBox5.title1_aspect.color = Qt.darkRed
textBox5.text1_aspect.color = Qt.darkRed  # Text: dark red
textBox5.onTextAspectsChanged()
textBox5.moveToCoords(250, 180)

textBox6 = myModel.newTextBoxLarge(
    testText,
    title="6. Arial 20 Center",
    titleAlignment='center'
)
textBox6.setTextFormat(fontName="Arial", size=20)
textBox6.setTitleFormat(fontName="Impact", size=20)  # Title: Impact 20 bold
textBox6.title1_aspect.font_weight = "bold"
textBox6.title1_aspect.color = Qt.darkMagenta
textBox6.onTextAspectsChanged()
textBox6.moveToCoords(490, 180)

# Test with long text that causes automatic line wrapping
longText1 = "This is a very long text that should cause automatic line wrapping when the TextBox width is not sufficient to display all the text on a single line. This text is much longer than the previous test text and should trigger word wrapping behavior in the TextBox widget."

textBox7 = myModel.newTextBoxLarge(
    longText1,
    title="7. Long Text Arial 12 Left",
    height=150,
    titleAlignment='left'
)
textBox7.setTextFormat(fontName="Arial", size=12)
textBox7.setTitleFormat(fontName="Arial", size=14)  # Title: Arial 14 bold
textBox7.title1_aspect.font_weight = "bold"
textBox7.text1_aspect.color = Qt.blue  # Text: blue
textBox7.onTextAspectsChanged()
textBox7.moveToCoords(10, 330)

longText2 = "Another extremely long text example with different content that will definitely cause automatic line wrapping. This text contains multiple sentences and should demonstrate how the height calculation handles text that wraps to multiple lines automatically due to width constraints."

textBox8 = myModel.newTextBoxLarge(
    longText2,
    title="8. Long Text Arial 14 Center",
    titleAlignment='center'
)
textBox8.setTextFormat(fontName="Arial", size=14)
textBox8.setTitleFormat(fontName="Georgia", size=16)  # Title: Georgia 16
textBox8.title1_aspect.color = Qt.blue
textBox8.onTextAspectsChanged()
textBox8.moveToCoords(250, 330)

longText3 = "This is the third long text example with even more content to test the word wrapping behavior. The text is intentionally very long to force automatic line breaks and see if the height calculation accounts for these wrapped lines properly."

textBox9 = myModel.newTextBoxLarge(
    longText3,
    title="9. Long Text Arial 16 Right",
    titleAlignment='right'
)
textBox9.setTextFormat(fontName="Arial", size=16)
textBox9.setTitleFormat(fontName="Courier New", size=14)  # Title: Courier New 14 bold italic
textBox9.title1_aspect.font_weight = "bold"
textBox9.title1_aspect.font_style = "italic"
textBox9.title1_aspect.text_decoration = "underline"
textBox9.title1_aspect.color = Qt.darkCyan
textBox9.text1_aspect.color = Qt.darkMagenta  # Text: dark magenta
textBox9.onTextAspectsChanged()
textBox9.moveToCoords(490, 330)



myModel.launch()
sys.exit(monApp.exec_())
