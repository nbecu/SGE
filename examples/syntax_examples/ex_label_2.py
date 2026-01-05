import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# Initialize the application
monApp = QtWidgets.QApplication([])
myModel = SGModel(700, 400)  # Adjusted window size to display all labels

# Define styles (as in your example)
textStyle_specs1 = "font-family: Papyrus; font-size: 26px; color: blue; text-decoration: blink; font-weight: 300; font-style: normal;"
borderStyle_specs1 = "border: 4px inset magenta;"
backgroundColor_specs1 = "background-color: cyan;"

textStyle_specs2 = "font-family: Comic Sans MS; font-size: 33px; color: yellow; text-decoration: line-through; font-weight: lighter; font-style: normal;"
borderStyle_specs2 = "border: 5px dashed gold;"
backgroundColor_specs2 = "background-color: teal;"

textStyle_specs3 = "font-family: Arial; font-size: 16px; color: rgb(255, 0, 0); text-decoration: underline; font-weight: bold; font-style: italic;"
borderStyle_specs3 = "border: 3px solid purple;"
backgroundColor_specs3 = "background-color: lightgray;"

textStyle_specs4 = "font-family: Courier New; font-size: 14px; color: darkgreen; text-decoration: none; font-weight: normal; font-style: normal;"
borderStyle_specs4 = "border: 2px dotted rgba(0, 100, 0, 0.8);"
backgroundColor_specs4 = "background-color: lightyellow;"

textStyle_specs5 = "font-family: Times New Roman; font-size: 20px; color: white; text-decoration: none; font-weight: bold; font-style: normal;"
borderStyle_specs5 = "border: 3px groove navy;"
backgroundColor_specs5 = "background-color: darkslategray;"

text = "Styled label example"

# Label 1: Blinking text, magenta inset border, cyan background
myModel.newLabel(text, (30, 30), textStyle_specs1, borderStyle_specs1, backgroundColor_specs1, fixedWidth=300)

# Label 2: Strike-through text, gold dashed border, teal background, right-aligned
myModel.newLabel(text, (350, 30), textStyle_specs2, borderStyle_specs2, backgroundColor_specs2, alignement="Right", fixedWidth=300)

# Label 3: Red text, purple solid border, light gray background, centered
myModel.newLabel(text, (30, 150), textStyle_specs3, borderStyle_specs3, backgroundColor_specs3, alignement="Center", fixedWidth=300, fixedHeight=60)

# Label 4: Dark green text, green dotted border, light yellow background, vertically centered
myModel.newLabel(text, (350, 150), textStyle_specs4, borderStyle_specs4, backgroundColor_specs4, alignement="VCenter", fixedWidth=300, fixedHeight=80)

# Label 5: White text on dark gray background, navy groove border, justified alignment
myModel.newLabel(
    text="Label with justified text and groove border, dark gray background and white text. This label demonstrates justified alignment and a 'groove' border type.",
    position=(20, 280),
    textStyle_specs=textStyle_specs5,
    borderStyle_specs=borderStyle_specs5,
    backgroundColor_specs=backgroundColor_specs5,
    alignement="Justify",
    fixedWidth=400
)

# Label 6: Underlined text, thin blue border, transparent background (no background-color), left-aligned
textStyle_specs6 = "font-family: Verdana; font-size: 18px; color: darkblue; text-decoration: underline; font-weight: normal; font-style: normal;"
borderStyle_specs6 = "border: 1px solid darkblue;"
myModel.newLabel(text, (430, 300), textStyle_specs6, borderStyle_specs6, "", alignement="Left", fixedWidth=250)

# Launch the application
myModel.launch()
sys.exit(monApp.exec_())
