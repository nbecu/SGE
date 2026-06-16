# Instance Symbologies Legend (Points d'Intérêt)

## Overview

Add support for a **separate legend display of instance symbologies** (entity-level overrides). This allows modelers to visualize and explain custom colors applied to specific entities, which often represent "points of interest" or "areas of particular interest" in the simulation.

## Motivation

When using instance symbologies:
```python
cell = Cells.getCell(1, 1)
cell.setInstanceSymbology("Fertility", "fertility", {0: QColor("purple"), 1: QColor("cyan")})
```

The grid displays the entity in the override color (purple/cyan), but the standard legend shows only the type-level symbology (brown/green). This is confusing for players:
- They see purple in the grid
- But the legend shows brown

**Solution:** Separate legend showing instance overrides, clearly marked as special points of interest.

## Proposed API

```python
# Standard legend: type-level symbologies
standard_legend = myModel.newLegend(name="Symbologies")

# Instance overrides legend: only custom entity-level symbologies
overrides_legend = myModel.newLegend(instance_symbologies_only=True, name="Points d'Intérêt")
```

## Implementation Details

### Parameter: `instance_symbologies_only`

When `instance_symbologies_only=True`:

1. **Data collection**: Iterate over all entities in model
   - For each entity type: `entity_type.getAllEntities()` (or equivalent)
   - For each entity: check `entity.instance_aspects` dict
   - Extract unique symbologies and colors

2. **Grouping**: Group by symbology name (not by entity)
   - Example:
     ```
     Points d'Intérêt
     ─── Fertility ───
     0 (purple) — cell(1,1)
     1 (cyan) — cell(1,1)
     ```

3. **Display behavior**:
   - If no instance symbologies exist: **display nothing** (empty legend body, just title remains)
   - If overrides exist: display per symbology with value→color pairs
   - No "No overrides" message or placeholder text

### Data Structure

Legend receives from `updateWithSymbologies()`:
```python
# Current (type-level):
{type1: {'shape': 'Fertility', 'border': None}, ...}

# New (instance-level):
{
  'instance_overrides': {
    'Fertility': {
      Cells: [(value, color, entity_id), ...],
      Sheep: [(value, color, entity_id), ...],
    },
    'OtherSymbology': {...}
  }
}
```

Or simpler: `updateWithSymbologies()` identifies `instance_symbologies_only=True` and collects data differently.

### Collection Logic

```python
if instance_symbologies_only:
    # Collect from all entities
    overrides_by_symbology = {}
    for entity_type in [all types]:
        for entity in entity_type.getAllEntities():
            for symbology_name, symbology in entity.instance_aspects.items():
                if symbology_name not in overrides_by_symbology:
                    overrides_by_symbology[symbology_name] = {}
                for value, aspect in symbology.mapping.items():
                    color = aspect.background_color
                    if symbology_name not in overrides_by_symbology:
                        overrides_by_symbology[symbology_name] = []
                    overrides_by_symbology[symbology_name].append((value, color, entity))
    # Pass to legend for display
    legend.updateWithInstanceOverrides(overrides_by_symbology)
```

### Legend Display

For each symbology with overrides:
1. Show symbology name as section title (like "Fertility")
2. List unique value→color pairs
3. Optionally: show which entities have the override (e.g., "cell(1,1)")

## Example Usage

```python
myModel = SGModel(windowTitle="Points d'Intérêt Example")

Cells = myModel.newCellsOnGrid(5, 5, "square", size=60)
Cells.newSymbology("fertility", {0: QColor("brown"), 1: QColor("green")})

# Mark special cells as points of interest
cell_poi = Cells.getCell(2, 2)
cell_poi.setInstanceSymbology("Fertility", "fertility", 
                               {0: QColor("purple"), 1: QColor("cyan")})

# Standard symbologies legend
legend1 = myModel.newLegend(name="Symbologies")

# Points of interest legend (shows purple/cyan override)
legend2 = myModel.newLegend(instance_symbologies_only=True, name="Points d'Intérêt")

myModel.launch()
```

Expected display in `legend2`:
```
Points d'Intérêt
─── Fertility ───
0 (purple)
1 (cyan)
```

## Implementation Plan

1. **Update `SGLegend.updateWithSymbologies()`**
   - Add parameter `instance_symbologies_only=False`
   - If True: collect instance overrides instead of type symbologies

2. **Add method to collect overrides**
   - Iterate all entities
   - Aggregate by symbology name and value
   - Return structure suitable for legend display

3. **Update `newLegend()` signature**
   - Add parameter `instance_symbologies_only=False`
   - Pass to legend initialization

4. **Create example**
   - `examples/syntax_examples/ex_instance_symbologies_legend.py`
   - Show parallel display of standard + override legends

## Related Notes

- [[SYMBOLOGY_MENU_IMPROVEMENTS]] — Phase 2 work on menu structure and symbologies
- [[ENABLE_DISABLE_KEYWORDS]] — Future API consistency work
- `ex_symbology_groups_hierarchy.py` — Contains example with instance override (cell(1,1) with purple/cyan)

## Timeline

**Priority:** Medium  
**Estimated effort:** 3-4 hours (data collection + legend display + testing)  
**Blocker:** None — can be done independently

## Notes

- Instance overrides are currently **not visible in any legend**, creating UX confusion
- This feature makes them explicitly discoverable
- Aligns with SGE design philosophy: "explicit is better than implicit"
- Natural evolution of symbology system as models become more complex
