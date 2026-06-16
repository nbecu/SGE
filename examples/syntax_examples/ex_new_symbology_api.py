"""
New Symbology API - Phase 3 (June 2026)

Demonstrates the cleaner, explicit API for creating symbologies:
- newSymbology() for discrete/nominal values (traditional)
- newSymbologyGradient() for continuous color gradients
- newSymbologyClassified() for interval classification

Legend now displays each type appropriately:
- Nominal: List of discrete values
- Gradient: Color bar showing smooth transition
- Classified: Color bands for each interval
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from mainClasses.SGClassifier import SGClassifier
from PyQt6.QtGui import QColor

monApp = QtWidgets.QApplication([])
applySGELightTheme()

myModel = SGModel(1400, 900, windowTitle="New Symbology API - Phase 3")

# Create cells with test attributes
Cells = myModel.newCellsOnGrid(8, 8, "square", size=40, gap=5)
Cells.setEntities("health", 50)
Cells.setEntities("temperature", 50)
Cells.setEntities("income", 50)

# Set values from 0-100
Cells.setEntities_withGradient("health", 0, 100)
Cells.setEntities_withGradient("temperature", 0, 100)
Cells.setEntities_withGradient("income", 0, 100)

print("=" * 70)
print("NEW SYMBOLOGY API TEST")
print("=" * 70)

# ========================================================================
# 1. NOMINAL SYMBOLOGY (discrete categories)
# ========================================================================
print("\n[1] Nominal Symbology - Traditional discrete values")
print("-" * 70)

health_aspects = {
    25: SGAspect(background_color=QColor("red"), text_content="{health}"),
    50: SGAspect(background_color=QColor("yellow"), text_content="{health}"),
    75: SGAspect(background_color=QColor("lime"), text_content="{health}"),
    100: SGAspect(background_color=QColor("green"), text_content="{health}"),
}

Cells.newSymbology("health", health_aspects, name="HealthDiscrete")
print("[PASS] Created nominal symbology for health")

# ========================================================================
# 2. GRADIENT SYMBOLOGY (smooth color transition)
# ========================================================================
print("\n[2] Gradient Symbology - Smooth color interpolation")
print("-" * 70)

# Linear gradient (blue → red)
temp_gradient = {
    0: SGAspect(background_color=QColor("blue")),
    100: SGAspect(background_color=QColor("red")),
}

Cells.newSymbologyGradient(
    "temperature",
    temp_gradient,
    interpolation="linear",
    name="TemperatureLinear"
)
print("[PASS] Created linear gradient for temperature (blue->red)")

# Sigmoid gradient (smooth S-curve)
temp_sigmoid = {
    0: SGAspect(background_color=QColor("cyan")),
    100: SGAspect(background_color=QColor("magenta")),
}

Cells.newSymbologyGradient(
    "temperature",
    temp_sigmoid,
    interpolation="sigmoid",
    name="TemperatureSigmoid"
)
print("[PASS] Created sigmoid gradient for temperature (cyan->magenta)")

# ========================================================================
# 3. CLASSIFICATION SYMBOLOGY (interval-based)
# ========================================================================
print("\n[3] Classification Symbology - Interval classes")
print("-" * 70)

# Quantile classification (4 equal-count bins)
quantile_mapping = SGClassifier.classify_quantile(
    Cells.entities,
    attribute="income",
    num_classes=4
)

Cells.newSymbologyClassified(
    "income",
    quantile_mapping,
    name="IncomeQuantile"
)
print("[PASS] Created quantile classification for income")

# Manual classification (custom thresholds)
manual_mapping = SGClassifier.classify_manual(
    thresholds=[0, 33, 66, 100],
    colors=[QColor("green"), QColor("yellow"), QColor("red")]
)

Cells.newSymbologyClassified(
    "income",
    manual_mapping,
    name="IncomeManual"
)
print("[PASS] Created manual classification for income")

# ========================================================================
# CREATE LEGEND
# ========================================================================
print("\n[4] Creating Legend with improved display")
print("-" * 70)

legend = myModel.newLabel(
    "SYMBOLOGY LEGEND\n\n"
    "Health (Nominal):\n"
    "25=Red, 50=Yellow, 75=Green, 100=Bright Green\n\n"
    "Temperature (Gradient):\n"
    "Linear: Blue (0C) -> Red (100C)\n"
    "Sigmoid: Cyan (0C) -> Magenta (100C)\n\n"
    "Income (Classification):\n"
    "Quantile: 4 equal-count bins\n"
    "Manual: 3 threshold bins",
    position=(700, 50)
)

print("[PASS] Legend label created")

# ========================================================================
# MENU DISPLAY
# ========================================================================
print("\n" + "=" * 70)
print("MENU DISPLAY")
print("=" * 70)
print("\nAvailable symbologies in menu:")
print("  Health:")
print("    - HealthDiscrete (nominal: discrete values)")
print("  Temperature:")
print("    - TemperatureLinear (gradient: linear interpolation)")
print("    - TemperatureSigmoid (gradient: sigmoid interpolation)")
print("  Income:")
print("    - IncomeQuantile (classified: 4 quantile bins)")
print("    - IncomeManual (classified: 3 manual thresholds)")

print("\n" + "=" * 70)
print("API COMPARISON")
print("=" * 70)

print("""
OLD API (less clear):
  Cells.newSymbology("attr", mapping, interpolation="linear")
  Cells.newSymbology("attr", mapping, classification_method="quantile")

NEW API (explicit):
  Cells.newSymbologyGradient("attr", mapping, interpolation="linear")
  Cells.newSymbologyClassified("attr", mapping)

BENEFITS:
  1. Clear intent - reader immediately knows what type is created
  2. Specialized parameters - only relevant options shown
  3. Better IDE autocomplete - separate method signatures
  4. Consistent with existing API - setEntities_withGradient(), setEntities_withClassification()
  5. Cleaner legends - each type displayed appropriately
""")

myModel.show()
sys.exit(monApp.exec())
