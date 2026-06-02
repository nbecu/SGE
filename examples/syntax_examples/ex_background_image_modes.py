"""
Background image scaling modes demonstration.

Shows three modes for scaling background images in GameSpaces:
- 'stretch' (default): Scale to fill widget (may distort aspect ratio)
- 'cover': Scale to cover widget, maintain aspect (may crop)
- 'contain': Scale to fit inside widget, maintain aspect (may have margins)

Usage:
1. Run the script
2. Click through the game phases to see grid with different background modes
3. Resize the window to see how each mode responds
"""

from mainClasses.SGSGE import *

# Application initialization
monApp = QtWidgets.QApplication([])
applySGELightTheme()

# Model creation
myModel = SGModel(1200, 750, windowTitle="Background Image Modes Demo")

# Create three grids side-by-side with different background modes
# Use a non-square image to clearly see the difference in scaling

# Grid 1: stretch mode (default) - may distort
grid1 = myModel.newGameSpace("SGGrid", "Grid 1 (stretch)", 0, 0)
Cell1 = myModel.newCellsOnGrid(5, 5, "square", size=40, gap=10,
                               backgroundImage="./images/background_sea.jpg")
grid1.setStyle({
    'background_image_mode': 'stretch',
    'border_color': Qt.red,
    'border_size': 3
})

# Grid 2: cover mode - covers all area, may crop
grid2 = myModel.newGameSpace("SGGrid", "Grid 2 (cover)", 410, 0)
Cell2 = myModel.newCellsOnGrid(5, 5, "square", size=40, gap=10,
                               backgroundImage="./images/background_sea.jpg")
grid2.setStyle({
    'background_image_mode': 'cover',
    'border_color': Qt.green,
    'border_size': 3
})

# Grid 3: contain mode - fits inside, may have margins
grid3 = myModel.newGameSpace("SGGrid", "Grid 3 (contain)", 820, 0)
Cell3 = myModel.newCellsOnGrid(5, 5, "square", size=40, gap=10,
                               backgroundImage="./images/background_sea.jpg")
grid3.setStyle({
    'background_image_mode': 'contain',
    'border_color': Qt.blue,
    'border_size': 3
})

# Labels for clarity
label1 = myModel.newGameSpace("SGLabel", "Mode: stretch\n(may distort)", 40, 340)
label1.setStyle({'text_color': Qt.red, 'font_size': 12, 'font_weight': 'bold'})

label2 = myModel.newGameSpace("SGLabel", "Mode: cover\n(may crop)", 450, 340)
label2.setStyle({'text_color': Qt.green, 'font_size': 12, 'font_weight': 'bold'})

label3 = myModel.newGameSpace("SGLabel", "Mode: contain\n(may have margins)", 850, 340)
label3.setStyle({'text_color': Qt.blue, 'font_size': 12, 'font_weight': 'bold'})

# Test zoom feature (Item B) on the first grid
print("Grid 1 (stretch mode) has zoom enabled by default")
print("  - Zoom in/out with mouse wheel to see background image scale with cells")
print("  - Use setBackgroundImageZoom(False) to disable zoom")

# Optional: disable zoom on grid2 to show the difference
# grid2.setBackgroundImageZoom(False)
# label2.setText("Mode: cover\n(zoom disabled)")

myModel.show()
QtWidgets.QApplication.instance().exec()
