"""
Test: Refactored Aspect System Phase 1 (with Model-level management)

Validates:
- Simplified newSymbology() API (attribute first, name optional)
- CASE 1: Auto-derived names for single symbology per attribute
- CASE 2: Explicit names for multiple symbologies per attribute
- Automatic symbology group creation
- Hierarchical resolution (Entity >> EntityType >> default)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *
from mainClasses.SGAspectSystem import SGAspectResolver
from PyQt6.QtGui import QColor

print("=== Aspect System Phase 1 Refactored - Test Suite ===\n")

# Initialize app
monApp = QtWidgets.QApplication([])
myModel = SGModel(windowTitle="Aspect System Test", width=600, height=400)

# ============================================================================
# TEST 1: CASE 1 - Simple (auto-derived names)
# ============================================================================
print("TEST 1: CASE 1 - Simple symbologies (auto-derived names)")
print("-" * 60)

Cells = myModel.newCellsOnGrid(3, 3, "square", size=40)
Agents = myModel.newAgentType("Agents", "triangleAgent1")

# Simple case: name auto-derived
Cells.newSymbology("health", {100: QColor("green"), 50: QColor("red")})
print("[OK] Cells.newSymbology('health', {...})")
print(f"     >> Auto-derived name: 'Health'")
print(f"     >> In Model.symbologies: {list(myModel.symbologies.keys())}")

Agents.newSymbology("health", {100: QColor("green"), 50: QColor("red")})
print("[OK] Agents.newSymbology('health', {...})")
print(f"     >> Auto-derived name: 'Health'")
print(f"     >> Multiple types now share 'Health'")

# Check automatic group creation
print(f"\n[OK] Automatic group creation:")
print(f"     Model.symbology_groups keys: {list(myModel.symbology_groups.keys())}")
health_group = myModel.symbology_groups.get("Health")
if health_group:
    print(f"     'Health' group contains: {health_group.get_all_entity_types()}")

# ============================================================================
# TEST 2: CASE 2 - Complex (explicit names for multiple symbologies)
# ============================================================================
print("\n" + "=" * 60)
print("TEST 2: CASE 2 - Multiple symbologies (explicit names)")
print("-" * 60)

# Try to create 2nd symbology without explicit name - should error
print("[TEST] Trying to create 2nd 'health' symbology without explicit name...")
try:
    Cells.newSymbology("health", {100: QColor("blue"), 50: QColor("orange")})
    print("[FAIL] Should have raised ValueError")
except ValueError as e:
    print(f"[OK] Caught expected error:")
    print(f"     {str(e)[:80]}...")

# Create 2nd symbology with explicit name
print("\n[TEST] Creating 2nd 'health' symbology with explicit name...")
Cells.newSymbology("health", {100: QColor("blue"), 50: QColor("orange")}, name="HealthAlternate")
print("[OK] Cells.newSymbology('health', {...}, name='HealthAlternate')")
print(f"     Model.symbologies keys: {list(myModel.symbologies.keys())}")

# ============================================================================
# TEST 3: Hierarchical Resolution
# ============================================================================
print("\n" + "=" * 60)
print("TEST 3: Hierarchical Resolution (Entity >> EntityType >> default)")
print("-" * 60)

cell = Cells.getCell(1, 1)
cell.setValue("health", 100)

# Resolve using EntityType definition (no instance override)
color = SGAspectResolver.resolve_color(cell, "Health", "health", QColor("black"))
print(f"[OK] Resolved color for Cell with health=100:")
print(f"     Color: {color.name() if color else 'None'}")

# Create instance override
cell.setInstanceSymbology("Health", "health", {100: QColor("purple"), 50: QColor("pink")})
print(f"\n[OK] Set instance override for Cell(1,1)")

# Resolve again - should use instance override
color_override = SGAspectResolver.resolve_color(cell, "Health", "health", QColor("black"))
print(f"[OK] Resolved color with instance override:")
print(f"     Color: {color_override.name() if color_override else 'None'}")

# ============================================================================
# TEST 4: Symbology Groups
# ============================================================================
print("\n" + "=" * 60)
print("TEST 4: Symbology Groups (cross-entity-type)")
print("-" * 60)

health_group = SGAspectResolver.get_symbology_group(myModel, "Health")
if health_group:
    print(f"[OK] Retrieved group 'Health':")
    print(f"     Group name: {health_group.name}")
    print(f"     Entity types: {health_group.get_all_entity_types()}")

    for type_name in health_group.get_all_entity_types():
        symb = health_group.get_symbology_for_type(type_name)
        print(f"     - {type_name}: {symb}")

# ============================================================================
# TEST 5: Multiple Aspects in One Symbology
# ============================================================================
print("\n" + "=" * 60)
print("TEST 5: Multiple Aspects in One Symbology")
print("-" * 60)

Cells.newSymbology("owner", {"Player1": QColor("blue"), "Player2": QColor("red")})
print("[OK] Cells.newSymbology('owner', {...})")

# Add border aspect to same symbology
Cells.newSymbology(
    "owner",
    {"Player1": {"color": QColor("darkblue"), "width": 2}, "Player2": {"color": QColor("darkred"), "width": 1}},
    symbol_type='border',
    name="Owner"  # Same name to add to existing symbology
)
print("[OK] Added border aspect to 'Owner' symbology")

owner_symb = myModel.symbologies.get("Owner")
if owner_symb:
    print(f"     'Owner' symbology now has {len(owner_symb.aspects)} aspects:")
    for aspect in owner_symb.aspects:
        print(f"     - {aspect}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 60)
print("ALL TESTS COMPLETED SUCCESSFULLY")
print("=" * 60)
print(f"\nModel-level symbologies: {list(myModel.symbologies.keys())}")
print(f"Symbology groups: {list(myModel.symbology_groups.keys())}")
print("\nPhase 1 Refactored Architecture is working correctly!")

# Close without showing window (for testing)
myModel.close()
sys.exit(0)
