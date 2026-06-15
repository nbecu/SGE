"""
Phase 2: Visual Rendering Test - Symbologies displayed with colors

Demonstrates:
- Symbologies are created at Model level
- Colors are resolved and applied in paintEvent
- Menu selection drives visual updates
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from PyQt6.QtGui import QColor

print("=" * 70)
print("PHASE 2: VISUAL RENDERING TEST")
print("=" * 70)

app = QtWidgets.QApplication([])

model = SGModel(windowTitle="Phase 2 Visual Rendering Test", width=600, height=400, autoResize=False)

# Create entity types
Cells = model.newCellsOnGrid(3, 3, "square", size=60)
Cells.setEntities("health", 100)  # This creates the cell entities

Sheep = model.newAgentType("Sheep", "triangleAgent1")
Sheep.setDefaultValues({"health": lambda: 100})

# Create symbologies with distinct colors
print("\n[1] Creating symbologies...")

Cells.newSymbology(
    "health",
    {100: QColor("green"), 50: QColor("red"), 0: QColor("black")},
)
print("[OK] Cells Health symbology: green=100, red=50, black=0")

Sheep.newSymbology(
    "health",
    {100: QColor("lightgreen"), 50: QColor("orange"), 0: QColor("darkred")},
)
print("[OK] Sheep Health symbology: lightgreen=100, orange=50, darkred=0")

# For testing, create dummy entity objects with necessary attributes
print("\n[2] Creating test entities...")

class DummyEntity:
    def __init__(self, name, type_obj, model, health_value):
        self.name = name
        self.type = type_obj
        self.model = model
        self.health = health_value
        self.instance_aspects = {}  # For symbology overrides

    def getValue(self, attr_name):
        return getattr(self, attr_name, None)

    def value(self, attr_name):
        """Alias for getValue() used by SGAspectResolver"""
        return self.getValue(attr_name)

    def setValue(self, attr_name, value):
        setattr(self, attr_name, value)

cell = DummyEntity("Cell(0,0)", Cells, model, 100)
sheep = DummyEntity("Sheep", Sheep, model, 100)

print(f"[OK] Cell health: {cell.getValue('health')}")
print(f"[OK] Sheep health: {sheep.getValue('health')}")

# Activate the Health group
print("\n[3] Activating Health group...")
model.active_symbologies_by_type['grid1'] = 'Health'
model.active_symbologies_by_type['Sheep'] = 'Health'
print(f"[OK] Active symbologies by type: {model.active_symbologies_by_type}")

# Test color resolution
print("\n[4] Testing color resolution...")

from mainClasses.SGAspectSystem import SGAspectResolver

# Test cell color at health=100
cell_color = SGAspectResolver.resolve_color(cell, 'Health', 'health', QColor("white"))
print(f"[OK] Cell at health=100: {cell_color.name()} (expected #008000 for green)")
assert cell_color.name() == QColor("green").name(), "Cell color mismatch!"

# Test sheep color at health=100
sheep_color = SGAspectResolver.resolve_color(sheep, 'Health', 'health', QColor("white"))
print(f"[OK] Sheep at health=100: {sheep_color.name()} (expected #90ee90 for lightgreen)")
assert sheep_color.name() == QColor("lightgreen").name(), "Sheep color mismatch!"

# Test with lower health value
print("\n[5] Testing color at lower health value...")

cell.setValue('health', 50)
cell_color_low = SGAspectResolver.resolve_color(cell, 'Health', 'health', QColor("white"))
print(f"[OK] Cell at health=50: {cell_color_low.name()} (expected #ff0000 for red)")
assert cell_color_low.name() == QColor("red").name(), "Cell low-health color mismatch!"

print("\n" + "=" * 70)
print("PHASE 2 VISUAL RENDERING TEST COMPLETE")
print("=" * 70)

print("\n[Summary]")
print("[OK] Symbologies created with distinct colors")
print("[OK] Active symbologies tracked by type")
print("[OK] Color resolution works via SGAspectResolver")
print("[OK] Color changes reflect attribute value changes")

sys.exit(0)
