# Aspect System Refactoring — Unified Architecture

**Date:** 2026-06-15  
**Status:** PLANNED (Phase 1 Extended)  
**Scope:** Refactor SGVisualAspect to use SGAspect for unified visual properties across all entity types

---

## Rationale

### Current State
- **SGAspect** (mainClasses/SGAspect.py): Rich visual properties for GameSpaces
  - Font, color, text decoration, alignment
  - Border style, size, color
  - Background color, image, patterns
  - Extended: padding, border-radius, hover states, etc.
  
- **SGVisualAspect** (mainClasses/SGAspectSystem.py): Minimal for symbologies
  - Only: `symbol_type`, `attribute`, `mapping`
  - Cannot express: text, styles, opacity, etc.

### Problem
- Two parallel systems for visual properties
- SGVisualAspect too limited for specification requirements
- Code duplication and inconsistency
- No shared theme system

### Solution
**Use SGAspect for BOTH GameSpaces and Symbologies**
- Single source of truth for visual properties
- Reuse existing themes (title1, title2, modern, minimal, colorful, etc.)
- Extend properties once, benefit everywhere
- No architectural conflicts (each context uses relevant properties)

---

## Architecture: Before vs After

### BEFORE (Current)
```
GameSpaces (SGLabel, SGButton, etc.)
    └── gs_aspect: SGAspect
        ├── font, size, color
        ├── border_style, border_size, border_color
        ├── background_color, background_image
        └── (20+ properties)

Symbologies (SGSymbology)
    └── aspects: [SGVisualAspect, SGVisualAspect, ...]
        ├── symbol_type ('color', 'border', etc.)
        ├── attribute
        └── mapping (value → symbol)
        
❌ Inconsistent, duplicated concepts
```

### AFTER (Proposed)
```
Visual Properties System
    └── SGAspect (single unified class)
        ├── Text: font, size, color, decoration, weight, style, alignment
        ├── Border: style, size, color, radius, opacity
        ├── Background: color, image, mode, opacity
        ├── Dimensions: padding, min_width, min_height
        ├── States: hover, pressed, disabled, active
        └── Methods: getCompleteStyle(), applyToQFont(), etc.

Used by:
    ├── GameSpaces (via gs_aspect, title_aspect, etc.)
    └── Symbologies (via SGSymbology mapping values to SGAspect instances)

✅ Unified, no duplication, extensible
```

---

## Changes to Phase 1 Architecture

### SGSymbology (Modified)
```python
class SGSymbology:
    def __init__(self, name):
        self.name = name
        self.aspects = {}  # {aspect_type: SGAspect}
        # aspect_type examples: 'default', 'hover', 'active'
        
    def get_aspect(self, aspect_type='default'):
        """Get SGAspect for rendering context"""
        return self.aspects.get(aspect_type, self.aspects.get('default'))
    
    def add_aspect(self, aspect_type, sg_aspect):
        """Register an SGAspect instance"""
        self.aspects[aspect_type] = sg_aspect
```

### SGVisualAspect (REMOVED)
- **Deleted:** mainClasses/SGAspectSystem.py (class only)
- **Reason:** Replaced by SGAspect
- **Impact:** Reduce code by ~100 lines, zero duplication

### SGAspectResolver (Enhanced)
```python
@staticmethod
def resolve_visual_style(entity, symbology_name, default_aspect=None):
    """
    Hierarchical resolution of visual styling
    
    Resolution order:
    1. Entity instance aspect override (if any)
    2. Symbology aspect for entity's attribute value
    3. Type-level symbology (from group)
    4. Default aspect
    
    Returns: SGAspect instance
    """
    # Implementation in next phase
```

### API Changes
- `newSymbology(attribute, mapping, symbol_type='color', name=None)`
  - **Before:** mapping is `{value: QColor}` or `{value: {color, width}}`
  - **After:** mapping is `{value: SGAspect}` (unified)

---

## Property Mapping: What Each Context Uses

| Property | GameSpaces | Symbologies | Notes |
|----------|-----------|------------|-------|
| **Text** | | | |
| font, size, color | ✅ | ✅ | Both support text |
| text_decoration, font_weight, font_style | ✅ | ✅ | Both support text styling |
| alignment | ✅ | ✅ | Both support alignment |
| **Border** | | | |
| border_style, border_size, border_color | ✅ | ✅ | Both support borders |
| border_radius | ✅ | ✅ | GameSpace widgets + cell/agent borders |
| **Background** | | | |
| background_color | ✅ | ✅ | Both support bg color |
| background_image | ✅ | ✅ | Both support bg image |
| background_image_mode | ✅ | ✅ | Both support scaling modes |
| **Dimensions** | | | |
| padding, min_width, min_height | ✅ | ⚠️ | Mostly for GameSpaces |
| **States** | | | |
| hover_*, pressed_*, disabled_* | ✅ | ❌ | Only for interactive GameSpaces |

✅ = Used in context  
❌ = Not relevant, simply ignored  
⚠️ = Possible future use

---

## Migration Path

### Phase 1 Extended: Refactor
1. Remove SGVisualAspect class
2. Modify SGSymbology to use SGAspect
3. Update API: `newSymbology()` to accept SGAspect instances
4. Update SGAspectResolver for unified resolution

### Phase 2: No Changes
- Menu UI works unchanged
- Visual rendering uses new SGAspect-based symbologies
- Backward compat layer still works

### Phase 3+: Advanced Features
- Support for gradients (SGAspect + interpolation)
- Support for intervals with classification
- Support for custom rules (expressions)
- Texture/pattern support

---

## Backward Compatibility

### Breaking Changes
- ✅ **None for users**: Old `newPov()` still works via compatibility layer
- ⚠️ **Internal only**: SGVisualAspect removed (never public API)

### Migration for Code
Old Phase 1 code:
```python
mapping = {100: QColor("green"), 50: QColor("red")}
Cells.newSymbology("health", mapping)
```

New code (Phase 1 Extended):
```python
mapping = {
    100: SGAspect(background_color=QColor("green"), border_size=3),
    50: SGAspect(background_color=QColor("red"), border_size=1)
}
Cells.newSymbology("health", mapping)
```

Both work via adapter layer during transition.

---

## Implementation Plan

### Step 1: Create SGAspect Adapter
- Wrapper to accept both old format `{value: QColor}` and new format `{value: SGAspect}`
- Converts old → new internally

### Step 2: Update SGSymbology
- Change `self.aspects` structure from list to dict
- Support multiple aspect types (default, hover, active)

### Step 3: Update SGAspectResolver
- Resolve SGAspect instead of individual properties
- Hierarchical resolution returns complete SGAspect

### Step 4: Update Rendering
- SGEntityView uses resolved SGAspect
- Extract properties as needed (color, border, text, etc.)

### Step 5: Remove Old Code
- Delete SGVisualAspect class
- Clean up SGAspectSystem.py

---

## Files Affected

| File | Type | Change |
|------|------|--------|
| SGAspect.py | Existing | No change (already complete) |
| SGAspectSystem.py | Existing | Remove SGVisualAspect class, keep SGSymbology/SGAspectResolver |
| SGSymbology.py | NEW | Extract SGSymbology to dedicated file (optional refactor) |
| SGEntityType.py | Modified | newSymbology() adapter layer |
| SGEntityView.py | Modified | Use SGAspect for rendering |
| SGModel.py | No change | Menu system unchanged |

---

## Risk Assessment

### Low Risk
- ✅ SGAspect already well-tested in GameSpaces
- ✅ Unused properties simply ignored (no side effects)
- ✅ Backward compat layer absorbs old API

### Mitigations
- Create adapter layer for smooth transition
- Keep old code available during testing
- Comprehensive test coverage before cleanup

---

## Benefits

1. **Code Reduction:** Remove 100+ lines of SGVisualAspect duplication
2. **Feature Parity:** Symbologies get all SGAspect features for free
3. **Consistency:** Same visual model everywhere
4. **Maintainability:** Single class to update for visual properties
5. **Extensibility:** Add feature once, benefit both GameSpaces and symbologies
6. **Themes:** Reuse existing SGAspect themes for symbologies

---

## Next Steps

1. ✅ Document this refactoring (this file)
2. ⏭️ Create SYMBOLOGY_SPECIFICATION.md (detailed spec)
3. ⏭️ Update PHASE_1_COMPLETION_SUMMARY.md
4. ⏭️ Implement Phase 1 Extended refactoring
5. ⏭️ Test with examples
6. ⏭️ Update Phase 2 for unified architecture

---

## Questions for Review

- ✓ Is unified SGAspect architecture clear?
- ✓ Are property mappings correct?
- ✓ Any missing edge cases?
- ✓ Backward compat approach acceptable?
