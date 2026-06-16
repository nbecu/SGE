# Refactorization Plan: Defaults as Symbologies

## Current State Analysis

### Where Defaults Are Defined
- `SGEntityType.__init__()`: 
  - `self.defaultShapeColor` (Qt.white for cells, Qt.black for agents)
  - `self.defaultBorderColor` (Qt.black)
  - `self.defaultBorderWidth` (1)

### Where Defaults Are Used
1. **Rendering** (when `active_aspect_view is None`):
   - SGCell, SGAgent, SGTile use these defaults for colors
   
2. **Game actions** (SGActivate, SGCreate, SGDelete, etc.):
   - Preview colors for entity actions
   
3. **Direct property access**:
   - `entity.borderColor = self.type.defaultBorderColor`

### Current Architecture Problem
```
EntityType
  ├─ defaultShapeColor (Qt.Color) 
  ├─ defaultBorderColor (Qt.Color)
  ├─ defaultBorderWidth (int)
  └─ symbologies: {name: SGSymbology}
     └─ active_aspect_view (when symbology selected)
```

If `active_aspect_view` is None, fall back to defaults.
If selected, use symbology aspect.

## Proposed Architecture

```
EntityType
  ├─ default_symbology: SGSymbology  (ALWAYS exists, like built-in symbology)
  └─ symbologies: {name: SGSymbology}
     └─ active_aspect_view (when user-selected symbology active)
```

### Key Changes
1. **Remove**: `defaultShapeColor`, `defaultBorderColor`, `defaultBorderWidth`
2. **Add**: `default_symbology: SGSymbology` (singleton, always exists)
3. **Update rendering**: Always use `active_aspect_view` (either user-selected or default)
4. **Preserve API**: `newAgentType(..., defaultColor=Qt.black)` still works (creates default_symbology)

## Implementation Steps

### Phase 1: SGAspect Enhancement
- [ ] Add comment documenting "default aspect" role
- [ ] (No code changes needed, SGAspect already sufficient)

### Phase 2: SGSymbology for Defaults
- [ ] Create `_create_default_symbology()` method in SGEntityType
- [ ] Input: defaultShapeColor, defaultBorderColor, defaultBorderWidth
- [ ] Output: SGSymbology with single-value mapping covering "any value"
- [ ] Store as `self.default_symbology`

### Phase 3: Update Rendering
- [ ] Change rendering logic: always use `active_aspect_view`
- [ ] If user selected a symbology: `active_aspect_view = user_symbology`
- [ ] If no selection: `active_aspect_view = default_symbology`
- [ ] Remove fallback to `defaultShapeColor`, etc.

### Phase 4: Update Game Actions
- [ ] Change game actions to use `default_symbology` instead of `defaultShapeColor`

### Phase 5: API Compatibility
- [ ] Keep `newAgentType(..., defaultColor)` parameter
- [ ] Internally: `defaultColor` → `default_symbology`
- [ ] No breaking changes for modelers

### Phase 6: Tests & Examples
- [ ] Verify all examples still work
- [ ] Test default symbology displays correctly
- [ ] Test symbology selection overrides default

## Benefits
1. ✅ Single source of truth: all aspects (default + user-selected) use symbologies
2. ✅ Cleaner rendering logic: always use aspect system, no special cases
3. ✅ Foundation for hierarchy: can extend to per-instance symbologies later
4. ✅ Consistent menu: defaults appear in symbology system (optional feature)
5. ✅ Backward compatible: API stays the same

## Risks & Mitigation
| Risk | Mitigation |
|------|-----------|
| Breaking changes to rendering | Careful refactoring with testing |
| Examples break | Test all examples after changes |
| Performance impact | Default symbology is lightweight, no perf impact |

## Timeline Estimate
- SGAspect: 30 min
- Rendering: 1 hour
- Game actions: 30 min
- Tests & polish: 1 hour
- **Total: ~3 hours**
