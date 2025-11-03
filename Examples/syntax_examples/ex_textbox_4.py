import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
monApp = QtWidgets.QApplication([])

# Create model
myModel = SGModel(name="TextBox Test", windowTitle="SGTextBox Test")

# Test text - long text that requires scrolling
longText = """This is a very long text that demonstrates how textBox display long texts with automatic
word-wrapping and vertical scrolling when the content exceeds the widget height.

Key features:
- Default width and height (400x300 pixels)
- Automatic width adjustment if title is wider than default width
- Automatic word-wrapping for text content
- Vertical scrolling when text exceeds height (via mouse wheel and scrollbar)
- User-configurable width and height

You can scroll this text using the mouse wheel or the scrollbar on the right side.
The text will automatically wrap to fit the width of the text box.

This is the end of the test text. If you can see this line, scrolling is working correctly!"""

# Create a large text box with default dimensions
textBox1 = myModel.newTextBox(
    longText,
    title="1. Default Size (400x300)",
    titleAlignment='left'
)
textBox1.moveToCoords(10, 30)

# Create a large text box with custom width (wider)
textBox2 = myModel.newTextBox(
    longText,
    title="2. Custom Width (600x300)",
    width=600,
    titleAlignment='center'
)
textBox2.moveToCoords(280, 30)

# Create a large text box with custom height (taller)
textBox3 = myModel.newTextBox(
    longText,
    title="3. Custom Height (400x400)",
    height=400,
    titleAlignment='right'
)
textBox3.moveToCoords(900, 30)

# Create a large text box with custom width and height
textBox4 = myModel.newTextBox(
    longText,
    title="4. Custom Size (500x350) and colors",
    width=500,
    height=350,
    borderColor=Qt.blue,
    backgroundColor=Qt.pink,
    titleAlignment='center'
)
textBox4.moveToCoords(10, 200)

# Create a large text box with a very long title to test width adjustment
textBox5 = myModel.newTextBox(
    longText,
    title="5. Very Long Title That Should Extend The Widget Width Automatically",
    titleAlignment='left'
)
textBox5.moveToCoords(550, 200)

# Create a large text box with various aspect customizations
textBox6 = myModel.newTextBox(
    longText,
    title="6. Custom Aspects",
    width=500,
    height=350,
    titleAlignment='center'
)
textBox6.moveToCoords(820, 370)

# Apply various aspect customizations using SGGameSpace setters
textBox6.setBorderColor(Qt.darkGreen)
textBox6.setBorderSize(3)
textBox6.setBorderRadius(10)
textBox6.setBackgroundColor(Qt.lightYellow)

# Customize title and text aspects
textBox6.title1_aspect.font = "Times New Roman"
textBox6.title1_aspect.size = 16
textBox6.title1_aspect.font_weight = "bold"
textBox6.title1_aspect.color = Qt.darkBlue
textBox6.title1_aspect.text_decoration = "underline"

textBox6.text1_aspect.font = "Georgia"
textBox6.text1_aspect.size = 11
textBox6.text1_aspect.color = Qt.darkRed
textBox6.text1_aspect.font_style = "italic"

# Apply the changes
textBox6.onTextAspectsChanged()

# Launch the model
myModel.launch()
sys.exit(monApp.exec_())

