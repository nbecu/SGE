"""
Background image scaling modes demonstration.

Shows three modes for scaling background images in GameSpaces:
- 'stretch' (default): Scale to fill widget (may distort aspect ratio)
- 'cover': Scale to cover widget, maintain aspect (may crop)
- 'contain': Scale to fit inside widget, maintain aspect (may have margins)

Usage:
1. Run the script
2. See three grids side-by-side with different background modes
3. Resize the window to see how each mode responds
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# Application initialization
monApp = QtWidgets.QApplication([])
applySGELightTheme()

# Model creation
myModel = SGModel(1200, 750, windowTitle="Background Image Modes Demo")

# Create three grids side-by-side with different background modes
# Use a non-square image to clearly see the difference in scaling

# Grid 1: stretch mode - may distort
Cell1 = myModel.newCellsOnGrid(5, 10, "square", size=40, gap=10,
                               backgroundImage="./images/leaves.png")
grid1 = Cell1.grid
grid1.moveToCoords(40, 100)
grid1.setStyle({
    'background_image_mode': 'stretch',
    'border_color': Qt.red,
    'border_size': 3
})

# Grid 2: cover mode - covers all area, may crop
Cell2 = myModel.newCellsOnGrid(5, 10, "square", size=40, gap=10,
                               backgroundImage="./images/leaves.png")
grid2 = Cell2.grid
grid2.moveToCoords(450, 100)
grid2.setStyle({
    'background_image_mode': 'cover',
    'border_color': Qt.green,
    'border_size': 3
})

# Grid 3: contain mode - fits inside, may have margins
Cell3 = myModel.newCellsOnGrid(5, 10, "square", size=40, gap=10,
                               backgroundImage="./images/leaves.png")

grid3 = Cell3.grid
grid3.moveToCoords(860, 100)
grid3.setStyle({
    'background_image_mode': 'contain',
    'border_color': Qt.blue,
    'border_size': 3
})

# Labels for clarity
label1 = myModel.newLabel("Mode: stretch\n(may distort)", position=(40, 340),
                          textStyle_specs="color: red; font-weight: bold; font-size: 12px;")

label2 = myModel.newLabel("Mode: cover\n(may crop)", position=(450, 340),
                          textStyle_specs="color: green; font-weight: bold; font-size: 12px;")

label3 = myModel.newLabel("Mode: contain\n(may have margins)", position=(860, 340),
                          textStyle_specs="color: blue; font-weight: bold; font-size: 12px;")

# Zoom feature disabled for now (Item B testing)
# grid1.setBackgroundImageZoom(False)
# grid2.setBackgroundImageZoom(False)
# grid3.setBackgroundImageZoom(False)

myModel.show()
QtWidgets.QApplication.instance().exec()
