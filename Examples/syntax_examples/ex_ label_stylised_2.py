import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
import random
import string

monApp = QtWidgets.QApplication([])

myModel = SGModel(550, 550)


#Color options
options_color = ["red", "blue", "green", "yellow", "black", "white", "purple",
                      "orange", "pink", "cyan", "magenta", "brown", "gray", "navy", "teal", "gold",
                      "#FF0000", "#FFFF00", "#AB28F9", "#6A5ACD", "#FF4500", "#8A2BE2",
                      "rgb(127, 12, 0)", "rgb(6, 78, 255)", "rgb(0, 255, 0)",
                      "rgba(154, 20, 8, 0.5)", "rgba(114, 84, 210, 0.8)"]


#Text Style options
options_font_family = ["Times New Roman", "Georgia", "Garamond", "Baskerville", "Arial", "Helvetica", "Verdana", "Tahoma", "Trebuchet MS", "Courier New", "Lucida Console", "Monaco", "Consolas", "Comic Sans MS", "Papyrus", "Impact"]
#text_color  # see  options_color
options_text_decoration = ["none", "underline", "overline", "line-through", "blink"]
options_font_weight = ["normal", "bold", "bolder", "lighter", "100", "200", "300", "400", "500", "600", "700", "800", "900"]
options_font_style = ["normal", "italic", "oblique"]

# Border Styles options
options_border_style = ["solid", "dotted", "dashed", "double", "groove", "ridge", "inset"]
#border_size   # any integer from 0 to 100. O is equal to 'no border'
#border_color  # see  options_color

# Background Style
#background_color  # see  options_color

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

def generate_random_text():
    length = random.randint(10, 25)  # Longueur aléatoire entre 10 et 25
    letters = string.ascii_letters + string.digits  # Lettres et chiffres
    random_text = ''.join(random.choice(letters) for _ in range(length))  # Générer le texte aléatoire
    return random_text
# *****************************************************


for i in range(25):  # Repeat 15 times
    font_family = random.choice(options_font_family)
    font_size = random.randint(7, 24)
    text_color = random.choice(options_color)
    text_decoration = random.choice(options_text_decoration)
    font_weight = random.choice(options_font_weight)  # Choix aléatoire du poids de la police
    font_style = random.choice(options_font_style)  # Choix aléatoire du style de police
    
    border_style = random.choice(options_border_style)
    border_size = random.randint(0, 5)
    border_color = random.choice(options_color)
    text = f"{i}:{generate_random_text()}"
    position = (random.randint(0, 380),random.randint(20, 530))
    
    background_color = random.choice([color for color in options_color if not colors_close(color, text_color)])

    text_style = f"font-family: {font_family}; font-size: {font_size}px; color: {text_color}; text-decoration: {text_decoration}; font-weight: {font_weight}; font-style: {font_style};"
    border_specs = f"border: {border_size}px {border_style} {border_color};"           

    print(f"Text {i}:\n"
          f"text_style: {text_style}\n"
          f"border_specs: {border_specs}\n"
          f"background_color: {background_color}\n")

    # Use newLabel_stylised instead of newLabel
    myModel.newLabel_stylised(text, position,
                              font=font_family, size=font_size, color=text_color,
                              text_decoration=text_decoration, font_weight=font_weight,
                              font_style=font_style, border_style=border_style,
                              border_size=border_size, border_color=border_color,
                              background_color=background_color)




myModel.launch()
sys.exit(monApp.exec_())

