# Phase 2: Menu UI Design for Symbology System

**Date:** 2026-06-14  
**Status:** APPROVED  
**Based on:** Phase 1 Architecture + User Requirements

---

## 1. Menu Structure

### Visual Layout

```
symbologyMenu
├─ ════════════════════════════ GROUPS
├─ Health [checkbox]
├─ Owner [checkbox]
├─ Status [checkbox]
├─ Fertility [checkbox]
│
├─ ════════════════════════════ BY TYPE
├─ Cell (submenu)
│  ├─ Health [radio]
│  ├─ Owner [radio]
│  ├─ Fertility [radio]
│  └─ (separator)
├─ Agent (submenu)
│  ├─ Health [radio]
│  ├─ Status [radio]
│  └─ (separator)
└─ Tile (submenu)
   ├─ Owner [radio]
   └─ Fertility [radio]
```

### Notes
- **GROUPS section:** checkboxes (multi-select possible)
- **BY TYPE section:** radio buttons (only one active per type)
- Separator between sections for clarity
- Only symbologies that exist for a type are shown in that type's submenu

---

## 2. Activation Logic

### Use Case 1: Display Group for All Types

```
User clicks: GROUPS > Health [checkbox]
→ For all entity types that have "Health" symbology:
   entity_type.displaySymbology("Health")
→ Active: Health for Cell, Agent, Tile (if all have it)
```

### Use Case 2: Start with Group, Then Override One Type

```
Step 1: User clicks GROUPS > Health [checkbox]
        → Cell.displaySymbology("Health")
        → Agent.displaySymbology("Health")
        → Tile.displaySymbology("Health")

Step 2: User clicks BY TYPE > Agent > Status [radio]
        → Agent.displaySymbology("Status")  # Override for Agent only
        → Cell and Tile remain on "Health"
        
Result:
- GROUPS > Health: [✓] (partially active - not all types)
- BY TYPE > Cell > Health: [✓]
- BY TYPE > Agent > Status: [✓]
- BY TYPE > Tile > Health: [✓]
```

### Use Case 3: Specify Different Symbologies per Type

```
User clicks:
- BY TYPE > Cell > Health [radio]
- BY TYPE > Agent > Status [radio]
- BY TYPE > Tile > Owner [radio]

Result:
- GROUPS section: all unchecked (no groups fully active)
- BY TYPE > Cell > Health: [✓]
- BY TYPE > Agent > Status: [✓]
- BY TYPE > Tile > Owner: [✓]
```

---

## 3. Implementation Details

### Menu Item Creation

**For GROUPS section:**
```python
def addSymbologyGroup(group_name):
    """
    Add a symbology group to the GROUPS section.
    When clicked, displays this symbology for all types that have it.
    """
    item = QAction(group_name, self, checkable=True)
    item.triggered.connect(lambda: self.onGroupSymbologyClicked(group_name))
    self.symbologyGroupsMenu.addAction(item)
```

**For BY TYPE section:**
```python
def addTypeSymbology(entity_type, symbology_name):
    """
    Add a symbology to a type's submenu (BY TYPE section).
    Uses radio buttons (only one active per type).
    """
    submenu = self.getOrCreateTypeSubmenu(entity_type.name)
    item = QAction(symbology_name, self, checkable=True)
    item.triggered.connect(lambda: self.onTypeSymbologyClicked(entity_type, symbology_name))
    # Create action group for radio button behavior
    if not hasattr(submenu, 'symbology_group'):
        submenu.symbology_group = QActionGroup(submenu)
    submenu.symbology_group.addAction(item)
    submenu.addAction(item)
```

### Click Handlers

**Group click:**
```python
def onGroupSymbologyClicked(self, group_name):
    group = self.model.symbology_groups.get(group_name)
    if group:
        # Activate for all types in group
        for type_name in group.get_all_entity_types():
            entity_type = self.model.getEntityType(type_name)
            entity_type.displaySymbology(group_name)
            # Update BY TYPE checkboxes to reflect activation
            self.updateTypeSymbologyCheckboxes(type_name, group_name)
```

**Type click:**
```python
def onTypeSymbologyClicked(self, entity_type, symbology_name):
    entity_type.displaySymbology(symbology_name)
    # Uncheck all groups (since this is an override)
    # because this type no longer follows its group
    self.updateGroupCheckboxes(entity_type, symbology_name)
```

---

## 4. State Synchronization

### Problem
- GROUPS section and BY TYPE section can represent overlapping states
- Need to keep them in sync visually

### Solution: Tracking Active Symbologies per Type

```python
Model.active_symbologies_by_type = {
    "Cell": "Health",      # Currently displaying this symbology
    "Agent": "Status",     # Override: different from group
    "Tile": "Health"       # Following group
}

Model.active_symbology_groups = {
    "Health": ["Cell", "Tile"],  # Partially active
    "Status": ["Agent"],
    "Owner": []
}
```

### Update Rules

**When GROUPS checkbox clicked:**
- Set `active_symbology_by_type[type] = group_name` for all types in group
- Update `active_symbology_groups[group_name] = [all types]`
- Update BY TYPE radio buttons to reflect changes

**When BY TYPE radio clicked:**
- Set `active_symbology_by_type[type] = symbology_name`
- Remove this type from any group's active list
- Mark group as "partially active" in GROUPS section (visual indicator: unchecked but partially filled)

---

## 5. Visual Indicators

### For Partially Active Groups

When a group is active for some types but not all:

**Option A:** Tri-state checkbox
- ☑ = fully active (all types)
- ☐ = inactive (no types)
- ⊡ = partially active (some types)

**Option B:** Color indicator
- Green checkmark = fully active
- Orange checkmark = partially active
- No checkmark = inactive

**Recommendation:** Use Option A (tri-state) as it's more standard

---

## 6. Integration with Phase 1

### What Phase 1 Provides
- ✅ Symbologies defined at Model level
- ✅ Groups created automatically when multiple types share same name
- ✅ `displaySymbology(name)` method on EntityType
- ✅ Hierarchical resolution via SGAspectResolver

### What Phase 2 Adds
- Menu UI structure (GROUPS + BY TYPE sections)
- Click handlers for group and type symbologies
- State tracking (active_symbologies_by_type)
- Visual indicators (checkboxes, radio buttons, partial state)

---

## 7. Testing Strategy

### Unit Tests (Menu Logic)
- Test group activation for all types
- Test type override behavior
- Test state synchronization

### Integration Tests (Full Flow)
- Test Use Case 1: Group activation
- Test Use Case 2: Override after group
- Test Use Case 3: Independent type selection

### UI Tests (Menu Appearance)
- Verify GROUPS section appears
- Verify BY TYPE sections created correctly
- Verify checkboxes/radio buttons show correct state
- Verify partial-active visual indicator works

---

## 8. Files to Modify in Phase 2

1. **mainClasses/SGModel.py**
   - Add `active_symbologies_by_type` dict
   - Add `active_symbology_groups` dict
   - Modify menu creation logic
   - Add click handlers

2. **mainClasses/SGEntityType.py**
   - Already has `displaySymbology(name)` method
   - May add helper to get list of available symbologies

3. **Menu creation** (in SGModel.initUI or similar)
   - Create GROUPS section with symbology_groups
   - Populate BY TYPE section from symbologies

---

## 9. Backwards Compatibility

Current POV system uses:
- `addEntTypeSymbologyinMenuBar(type, name)`
- Stores in `povShapeColor` and `povBorderColorAndWidth`

Phase 2 will:
- Migrate to `displaySymbology(name)` (already compatible)
- Keep wrapper for legacy POV if needed
- Update menu structure to reflect new groups

---

## Notes

- **Naming:** "GROUPS" section makes it clear these activate multiple types
- **Radio buttons:** Enforce "one active per type" constraint naturally
- **Partial state:** Communicates that group is partially active (some types overridden)
- **Future extension:** Can add "Views" (pre-configured group combinations) in Phase 3+

