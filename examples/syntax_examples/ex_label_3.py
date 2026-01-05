import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
import random

monApp = QtWidgets.QApplication([])


myModel = SGModel(550, 250)


#Color options
options_color = ["red", "blue", "green", "yellow", "black", "white", "purple",
                      "orange", "pink", "cyan", "magenta", "brown", "gray", "navy", "teal", "gold",
                      "#FF0000", "#FFFF00", "#AB28F9", "#6A5ACD", "#FF4500", "#8A2BE2",
                      "rgb(127, 12, 0)", "rgb(6, 78, 255)", "rgb(0, 255, 0)",
                      "rgba(154, 20, 8, 0.5)", "rgba(114, 84, 210, 0.8)"]

#Text Style
options_font_family = ["Times New Roman", "Georgia", "Garamond", "Baskerville", "Arial", "Helvetica", "Verdana", "Tahoma", "Trebuchet MS", "Courier New", "Lucida Console", "Monaco", "Consolas", "Comic Sans MS", "Papyrus", "Impact"]
font_family = random.choice(options_font_family)

font_size = random.randint(16, 34)
text_color = random.choice(options_color)

options_text_decoration = ["none", "underline", "overline", "line-through", "blink"]
text_decoration = random.choice(options_text_decoration)

options_font_weight = ["normal", "bold", "bolder", "lighter", "100", "200", "300", "400", "500", "600", "700", "800", "900"]
font_weight = random.choice(options_font_weight)  # Choix aléatoire du poids de la police

options_font_style = ["normal", "italic", "oblique"]
font_style = random.choice(options_font_style)  # Choix aléatoire du style de police

textStyle_specs = f"font-family: {font_family}; font-size: {font_size}px; color: {text_color}; text-decoration: {text_decoration}; font-weight: {font_weight}; font-style: {font_style};"
    

# Border Styles
options_border_style = ["solid", "dotted", "dashed", "double", "groove", "ridge", "inset"]
border_style = random.choice(options_border_style)
border_size = random.randint(0, 5)
border_color = random.choice(options_color)

borderStyle_specs = f"border: {border_size}px {border_style} {border_color};"           


# ********* specific methods used in this example **************
def rgb(color):
    if color.startswith('#'):
        color = color.lstrip('#')
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        return r, g, b
    elif color.startswith('rgba'):
        r, g, b, a = map(float, color[5:-1].split(','))
        return int(r * 255), int(g * 255), int(b * 255)  # Convert values from 0-1 to 0-255
    elif color.startswith('rgb'):
        return tuple(map(int, color[4:-1].split(',')))
    else:
        return (255, 255, 255)  # Default color (white)

def colors_close(color1, color2, threshold=30):
    # Use the rgb function to get the RGB values
    r1, g1, b1 = rgb(color1)
    r2, g2, b2 = rgb(color2)
    # Calculate the distance between the two colors
    distance = ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
    # Check if the distance is less than the threshold
    return distance < threshold

def contrastingColor(aColor):
    # Convert the color to RGB format
    if aColor.startswith('#'):
        aColor = aColor.lstrip('#')
        r = int(aColor[0:2], 16)
        g = int(aColor[2:4], 16)
        b = int(aColor[4:6], 16)
    elif aColor.startswith('rgb'):
        r, g, b = map(int, aColor[4:-1].split(','))
    else:
        # If the color is not in the expected format, return a default color
        return "white"    # Calculate the brightness
    brightness = (0.299 * r + 0.587 * g + 0.114 * b)
    # Return a contrasting color
    return "#000000" if brightness > 186 else "#FFFFFF"
# *****************************************************


# set the background_color with a color that os not close to the text color
backgroundColor = random.choice([color for color in options_color if not colors_close(color, text_color)])

# Options for the background image
options_background_images = [
    "url('https://images.unsplash.com/photo-1506748686214-e9df14d4d9d0')",  # Landscape image
    "url('path/to/image.jpg')" 
]
background_image = random.choice(options_background_images)

options_background_position = ["left", "center", "right", "top", "bottom", "10px 20px", "50% 50%"]
background_position = random.choice(options_background_position)  
options_background_repeat = ["repeat", "repeat-x", "repeat-y", "no-repeat", "space", "round"]
background_repeat = random.choice(options_background_repeat)  
options_background_size = ["auto", "cover", "contain", "100px 50px", "50% 50%"]
background_size = random.choice(options_background_size) 
# Update the background_style variable to include other settings
backgroundColor_FullSpecs = f"background-color: {random.choice(options_color)}; background-image: {background_image}; background-position: {background_position}; background-repeat: {background_repeat}; background-size: {background_size};"

#For this exaple we do not used image ni background. We use color for background
backgroundColor_specs = f"background-color: {random.choice(options_color)};"

print(f"text_style:{textStyle_specs}")
print(f"border_style:{borderStyle_specs}")
print(f"background_style:{backgroundColor_specs}")

#Instead of using the newLabel_stylised() method, you can directly use the newLabel() method and provide the textStyle_specs, borderStyle_specs and backgroundColor_specs using the exact same syntax as used above)
myModel.newLabel('This is a text in a label',(70,100),textStyle_specs, borderStyle_specs, backgroundColor_specs)



myModel.launch()
sys.exit(monApp.exec_())

