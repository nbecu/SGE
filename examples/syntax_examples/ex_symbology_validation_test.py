"""
Validation test: Verify symbology examples work correctly (no GUI)

Tests the 3 examples programmatically without launching GUI.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from mainClasses.SGAspectSystem import SGAspectResolver
from PyQt6.QtGui import QColor

print("=" * 70)
print("SYMBOLOGY VALIDATION TEST SUITE")
print("=" * 70)

# Initialize app (headless)
app = QtWidgets.QApplication([])

# ============================================================================
# TEST 1: Simple health symbology (CASE 1 - auto-derived name)
# ============================================================================
print("\n[TEST 1] Simple symbology with auto-derived names")
print("-" * 70)

model1 = SGModel(windowTitle="Test1", width=400, height=300, autoResize=False)
Cells1 = model1.newCellsOnGrid(3, 3, "square", size=40)
Cells1.setEntities("health", 100)

Cells1.newSymbology("health", {100: QColor("green"), 50: QColor("red")})
print("[OK] Cells.newSymbology('health', {...})")

Sheep1 = model1.newAgentType("Sheep", "triangleAgent1")
Sheep1.setDefaultValues({"health": lambda: 100})
Sheep1.newSymbology("health", {100: QColor("green"), 50: QColor("red")})
print("[OK] Sheep.newSymbology('health', {...})")

# Verify group was created
assert "Health" in model1.symbology_groups
assert "Health" in model1.symbologies
health_group = model1.symbology_groups["Health"]
assert "grid1" in health_group.get_all_entity_types()
assert "Sheep" in health_group.get_all_entity_types()
print(f"[OK] Automatic group 'Health' created with types: {health_group.get_all_entity_types()}")

# ============================================================================
# TEST 2: Multiple symbologies (CASE 2 - explicit names required)
# ============================================================================
print("\n[TEST 2] Multiple symbologies for same attribute")
print("-" * 70)

model2 = SGModel(windowTitle="Test2", width=400, height=300, autoResize=False)
Cells2 = model2.newCellsOnGrid(3, 3, "square", size=40)
Cells2.setEntities("health", 100)

# First: with auto-derived name
Cells2.newSymbology("health", {100: QColor("green"), 50: QColor("red")})
print("[OK] First symbology with auto-derived name 'Health'")

# Second: must use explicit name
Cells2.newSymbology(
    "health",
    {100: QColor("blue"), 50: QColor("orange")},
    name="HealthAlternate"
)
print("[OK] Second symbology with explicit name 'HealthAlternate'")

# Verify both exist
assert "Health" in model2.symbologies
assert "HealthAlternate" in model2.symbologies
print(f"[OK] Model has both symbologies: {list(model2.symbologies.keys())}")

# Verify error when trying to create 2nd auto-derived
print("[TEST] Trying to create 2nd auto-derived 'Health' without explicit name...")
try:
    Cells2.newSymbology("health", {100: QColor("purple")})
    print("[FAIL] Should have raised ValueError")
    sys.exit(1)
except ValueError as e:
    print(f"[OK] Caught expected error")

# ============================================================================
# TEST 3: Groups and hierarchy
# ============================================================================
print("\n[TEST 3] Symbology groups and hierarchical resolution")
print("-" * 70)

model3 = SGModel(windowTitle="Test3", width=400, height=300, autoResize=False)

Cells3 = model3.newCellsOnGrid(3, 3, "square", size=40)
Cells3.setEntities("fertility", 0)

Sheep3 = model3.newAgentType("Sheep", "triangleAgent1")
Sheep3.setDefaultValues({"fertility": lambda: 50})

# Create same-named symbologies in different types
Cells3.newSymbology("fertility", {0: QColor("brown"), 1: QColor("green")})
Sheep3.newSymbology("fertility", {0: QColor("gray"), 50: QColor("white")})

print("[OK] Created 'Fertility' symbologies in Cells and Sheep")

# Verify group
fertility_group = SGAspectResolver.get_symbology_group(model3, "Fertility")
assert fertility_group is not None
assert len(fertility_group.get_all_entity_types()) == 2
print(f"[OK] Group 'Fertility' contains: {fertility_group.get_all_entity_types()}")

# Test hierarchical resolution
cell = Cells3.getCell(1, 1)
cell.setValue("fertility", 0)

# Type-level (no instance override)
color_type = SGAspectResolver.resolve_color(cell, "Fertility", "fertility", QColor("black"))
assert color_type.name() == QColor("brown").name()
print(f"[OK] Type-level resolution: fertility=0 >> {color_type.name()}")

# Instance override
cell.setInstanceSymbology("Fertility", "fertility", {0: QColor("purple")})
color_override = SGAspectResolver.resolve_color(cell, "Fertility", "fertility", QColor("black"))
assert color_override.name() == QColor("purple").name()
print(f"[OK] Instance override: fertility=0 >> {color_override.name()}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("ALL VALIDATION TESTS PASSED")
print("=" * 70)

print("\nSummary:")
print("  [OK] CASE 1: Auto-derived names work for single symbology per attribute")
print("  [OK] CASE 2: Explicit names required for multiple symbologies per attribute")
print("  [OK] CASE 2: Error handling prevents accidental duplicates")
print("  [OK] Automatic groups created for same-named symbologies across types")
print("  [OK] Hierarchical resolution (instance > type > default)")

print("\nPhase 1 is validated and ready for production use!")
sys.exit(0)
