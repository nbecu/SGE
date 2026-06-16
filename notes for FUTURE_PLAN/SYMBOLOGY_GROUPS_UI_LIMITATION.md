# UI Limitation: Manual Symbology Groups Menu Display

## Problem

When a manual symbology group contains multiple symbologies from the same entity type, the UI displays only the **last symbology's radio button as checked** in the menu, even though **all symbologies in the group are actually active** in the backend.

### Example

When clicking "CompleteAnalysis" group (contains "HealthStatus" + "FertilityStatus"):
- **Menu display**: Only FertilityStatus radio button is checked
- **Backend state**: Both HealthStatus and FertilityStatus are active in `active_symbologies_by_type`
- **Grid display**: ✅ Correct - both symbologies displayed with blended colors
- **Legend display**: Shows FertilityStatus (consistent with checked menu item)

## Root Cause

Qt's `QActionGroup` with `setExclusive(True)` automatically unchecks other radio buttons when one is checked, even when `blockSignals()` is used. The issue occurs during the signal blocking mechanism designed to allow multiple selections.

## Current Workaround

- Legend displays only the checked radio button (reflects UI state)
- Backend functionality is 100% correct (both symbologies are active)
- This is a **cosmetic UI limitation**, not a functional bug

## Solution Strategy (Future)

Two possible approaches:

1. **Custom checkbox widget**: Replace radio buttons with custom styled checkboxes that look like radio buttons
   - Pros: Full control over appearance and behavior
   - Cons: Complex widget implementation

2. **Dual QActionGroups**: Create separate action groups for different modes
   - Exclusive group for automatic/manual groups
   - Non-exclusive group for multiple selections within groups
   - Add/remove actions dynamically as groups are activated/deactivated
   - Pros: Uses native Qt widgets
   - Cons: Complex state management

## Impact

- **Functionality**: None - system works correctly
- **UX**: Minor confusion - users see FertilityStatus checked but both are active
- **Severity**: Low - acceptable trade-off for current implementation

## Related Code

- `mainClasses/SGModel.py`:
  - `addEntTypeSymbologyinMenuBar()` - creates QActionGroup (line ~1563)
  - `_updateTypeMenuCheckbox()` - handles checkbox updates with signal blocking (line ~1920)
  - `_onGroupSymbologyClicked()` - activates groups (line ~1722)

- `mainClasses/SGLegend.py`:
  - `updateWithSymbologies()` - displays legend based on checked items (line ~36)
  - `getCheckedSymbologyOfEntity()` - reads checked radio buttons (line ~1977)

## Date Added

2026-06-16

## Priority

Low - cosmetic only, functionality is correct
