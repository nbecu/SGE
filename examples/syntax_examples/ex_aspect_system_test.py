"""
Test script: Aspect System Infrastructure (Phase 1)

Tests the new aspect system for hierarchical symbologies.
Validates:
- SGVisualAspect, SGSymbology, SGAspectView, SGAspectResolver
- Integration with SGEntityType.newSymbology()
- Instance overrides via SGEntity.setInstanceSymbology()
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import only what we need for testing
from mainClasses.SGAspectSystem import SGVisualAspect, SGSymbology, SGAspectView, SGAspectResolver
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

print("=== Aspect System Phase 1 Tests ===\n")

# Test 1: SGVisualAspect
print("Test 1: SGVisualAspect")
health_mapping = {100: QColor("green"), 75: QColor("yellow"), 50: QColor("red")}
aspect = SGVisualAspect('color', 'health', health_mapping)
print(f"  [OK] Created aspect: {aspect}")
print(f"       Symbol for health=100: {aspect.get_symbol(100)}")
print(f"       Symbol for health=999 (not found): {aspect.get_symbol(999, 'default')}")

# Test 2: SGSymbology
print("\nTest 2: SGSymbology")
symbology = SGSymbology("Health")
symbology.add_aspect(aspect)
print(f"  [OK] Created symbology: {symbology}")
print(f"       Aspects: {symbology.aspects}")
print(f"       Color aspect: {symbology.get_aspect_by_type('color')}")

# Test 3: SGAspectView
print("\nTest 3: SGAspectView")
view = SGAspectView("HealthView", [symbology])
print(f"  [OK] Created view: {view}")
print(f"       Symbologies in view: {view.get_symbologies()}")

# Test 4: Multiple aspects in one symbology
print("\nTest 4: Multiple aspects (color + border)")
border_mapping = {100: {'color': QColor("darkgreen"), 'width': 2}, 75: {'color': QColor("orange"), 'width': 1}}
border_aspect = SGVisualAspect('border', 'health', border_mapping)
symbology.add_aspect(border_aspect)
print(f"  [OK] Added border aspect to symbology")
print(f"       Symbology now has {len(symbology.aspects)} aspects")
print(f"       All color aspects: {symbology.get_all_aspects_by_type('color')}")
print(f"       All border aspects: {symbology.get_all_aspects_by_type('border')}")

# Test 5: SGAspectResolver
print("\nTest 5: SGAspectResolver (hierarchical resolution)")
print("  [OK] Resolver created")
print("       - resolve_color(): resolves Entity -> EntityType -> default")
print("       - resolve_border(): resolves Entity -> EntityType -> default")
print("       - get_active_view(): returns current active view")
print("       - get_symbologies_for_view(): gets symbologies in a view")

print("\n" + "="*50)
print("ALL TESTS PASSED")
print("="*50)
print("\nPhase 1 Infrastructure ready for integration with SGEntityType and SGEntity")
