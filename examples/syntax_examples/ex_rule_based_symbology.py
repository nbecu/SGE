"""
Rule-Based Symbology Example (Phase 3, Advanced)

Demonstrates:
- Complex conditional logic with multiple attributes
- Custom functions to determine visual style
- Combining multiple conditions in a single rule
- Dynamic aspect generation based on entity state

Example: Temperature & Humidity conditions
- Hot & Dry (temp > 30 & humidity < 50): Red with thick border
- Hot & Humid (temp > 30 & humidity >= 50): Orange with medium border
- Cold (temp <= 30): Blue with thin border
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])

myModel = SGModel(windowTitle="Rule-Based Symbology Example")

# Create cells with temperature and humidity attributes
Cells = myModel.newCellsOnGrid(8, 8, "square", size=60)
Cells.setEntities("temperature", 20)
Cells.setEntities("humidity", 50)

# Set random temperature and humidity values
import random
random.seed(42)
for cell in Cells.entities:
    temp = random.randint(15, 40)
    humidity = random.randint(20, 90)
    cell.setValue("temperature", temp)
    cell.setValue("humidity", humidity)

# Define a rule-based symbology using a custom function
def temperature_humidity_rule(entity):
    """
    Determine visual style based on temperature and humidity conditions.

    Rules:
    1. If temp > 30 AND humidity < 50: Hot & Dry → Red with thick border
    2. If temp > 30 AND humidity >= 50: Hot & Humid → Orange with medium border
    3. If temp <= 30: Cold → Blue with thin border
    """
    temp = entity.value("temperature")
    humidity = entity.value("humidity")

    # Rule 1: Hot & Dry
    if temp > 30 and humidity < 50:
        return SGAspect(
            background_color=QColor("red"),
            border_color=QColor("darkred"),
            border_size=3,
            text_content=f"HOT\nDRY\nT:{temp}°\nH:{humidity}%",
            text_color="white",
            text_size=8,
            text_weight="bold"
        )

    # Rule 2: Hot & Humid
    elif temp > 30 and humidity >= 50:
        return SGAspect(
            background_color=QColor("orange"),
            border_color=QColor("darkorange"),
            border_size=2,
            text_content=f"HOT\nWET\nT:{temp}°\nH:{humidity}%",
            text_color="white",
            text_size=8
        )

    # Rule 3: Cold
    elif temp <= 30:
        return SGAspect(
            background_color=QColor("lightblue"),
            border_color=QColor("darkblue"),
            border_size=1,
            text_content=f"COLD\nT:{temp}°\nH:{humidity}%",
            text_color="darkblue",
            text_size=8
        )

    # Fallback (should not happen if rules are complete)
    return SGAspect(background_color=QColor("gray"))

# Create symbology using the rule function
Cells.newSymbology(
    "temperature",  # attribute name (used for naming)
    rule_function=temperature_humidity_rule,
    name="ClimateConditions"
)

# Add legend to show the rule mappings
myModel.newLegend()

# Launch
print("Rule-Based Symbology Example:")
print("==============================")
print("This example uses a custom function to determine cell appearance")
print("based on temperature AND humidity conditions together.")
print()
print("Rules applied:")
print("1. Hot & Dry (T > 30 & H < 50): Red background, thick border")
print("2. Hot & Humid (T > 30 & H >= 50): Orange background, medium border")
print("3. Cold (T <= 30): Blue background, thin border")
print()
print("Each cell displays its temperature and humidity values dynamically.")
print()
print("Key advantage of rule-based symbologies:")
print("- Can evaluate multiple attributes simultaneously")
print("- More flexible than simple conditional aspects (apply_if)")
print("- Can perform complex logic and calculations")
print("- Returns complete SGAspect with all properties customized")

myModel.launch()
sys.exit(monApp.exec())
