# Add `enable`/`disable` Keywords for API Consistency

## Overview

Currently, SGE has 11 modeler methods using `enable...()` and `disable...()` patterns that are miscategorized as "OTHER MODELER METHODS" instead of having dedicated keywords. Additionally, 8+ methods using `set...()` pattern with boolean-like intent could be refactored for clarity.

## Motivation

**Current State:** Method naming is inconsistent
```python
SGModel.enableBotPlayer()                    # enable (no keyword)
SGControlPanel.setShowSectionTitles(True)    # set (ambiguous intent)
SGModel.hideDefaultGraphMenuItems()          # hide (inconsistent verb)
```

**Goal:** Unified `enable`/`disable` keyword for clearer intent and consistency with reserved keywords in README_developer.md

## Candidates for Refactoring

### Phase 1: Recategorize Existing Methods (11 methods)

These already use `enable/disable` pattern but are in "OTHER MODELER METHODS":

**SGEndGameRule:**
- `enableEndGameBanner()` / `disableEndGameBanner()`
- `enableEndGameRuleHighlight()` / `disableEndGameRuleHighlight()`

**SGModel:**
- `enableBotPlayer()` / `disableBotPlayer()`
- `enableAutoSaveGameActionLogs()`
- `enableDistributedGame()`
- `hideDefaultGraphMenuItems()` → `disableDefaultGraphMenuItems()`

**SGPlayer:**
- `enableActionPoints()` / `disableActionPoints()`

### Phase 2: Refactor `set...()` Methods (8 methods)

These use `setShow/setHide/setEnabled` pattern and could be refactored.

**⚠️ NAMING AMBIGUITY ALERT:**

For methods like `setShowSectionTitles()`, refactoring to `disableSectionTitles()` is **ambiguous** because:
- `disableSectionTitles()` suggests disabling the titles themselves
- What we really want: disable the **display** of section titles
- The titles are still enabled; only their visibility is toggled

**Solution Options:**

```python
# Option A: Explicit about display intent
enableSectionTitlesDisplay() / disableSectionTitlesDisplay()
enableIconsInContextMenuDisplay() / disableIconsInContextMenuDisplay()

# Option B: Use show/hide verbs (clearer intent)
showSectionTitles() / hideSectionTitles()
showIconsInContextMenu() / hideIconsInContextMenu()

# Option C: Keep current (setShow/setEnabled)
setShowSectionTitles(True/False)
setShowIconsInContextMenu(True/False)
```

**Recommendation:** Option B (`show/hide`) better expresses "toggle visibility" intent, or Option A if we want consistency with `enable/disable` keyword but need explicit "Display" suffix.

**Methods to Refactor:**
- `SGControlPanel.setShowSectionTitles()` → `showSectionTitles()` / `hideSectionTitles()`
- `SGControlPanel.setShowSelectionBorder()` → `showSelectionBorder()` / `hideSelectionBorder()`
- `SGControlPanel.setShowTitle()` → `showTitle()` / `hideTitle()`
- `SGEndGameRule.setEndGameAnimationEnabled()` → `enableEndGameAnimation()` / `disableEndGameAnimation()`
- `SGModel.setShowIconsInContextMenu()` → `showIconsInContextMenu()` / `hideIconsInContextMenu()`
- `SGTimeLabel.setDisplayPhaseName()` → `showPhaseName()` / `hidePhaseName()`
- `SGTimeLabel.setDisplayPhaseNumber()` → `showPhaseNumber()` / `hidePhaseNumber()`
- `SGTimeLabel.setDisplayRoundNumber()` → `showRoundNumber()` / `hideRoundNumber()`

## Additional Keywords to Consider

If implementing `enable/disable`, consider also adding:
- **`show`/`hide`** — for display-related toggles (clearer than enable/disable for visibility)
- These are semantic variants better suited to UI visibility, while `enable/disable` suit feature toggles

## Implementation Plan

1. **Update README_developer.md** — Add `enable`, `disable` to reserved keywords section
2. **Recategorize methods** — Move 11 existing enable/disable methods to new keyword category
3. **Refactor problematic methods** — Choose Option A or B for display-intent methods
4. **Update method catalog** — Regenerate `sge_methods_catalog.json`
5. **Update docstrings** — Clarify intent in method documentation

## Related Issues

- Inconsistent API terminology (see commit messages in Phase 2.5)
- Method catalog miscategorization ("OTHER MODELER METHODS" is too vague)
- Symbology API naming alignment (see `displaySymbology()` decision from June 2026)

## Timeline

- Not blocking — can be done in dedicated refactoring sprint
- Medium priority — improves API clarity and discoverability
- Estimated effort: 2-3 hours for refactoring + testing

## References

- `README_developer.md` — Reserved keywords section
- `docs/SGE_methods/sge_methods_catalog.json` — Current method categories
- `CONTEXT_SGE_FOR_CHATBOT.md` — API design conventions
