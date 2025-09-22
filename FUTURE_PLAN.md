# SGE - Future Plan

This document contains the planned improvements and features for the SGE (Simulation Game Editor) project.

## Current Development Items

### Core Architecture & Framework
- [ ] Refactor SGModel to follow the ordering convention of SGE for modeler methods
- [ ] Unify definition of `setValue` for the different classes
- [ ] Rename EntDef to a name that makes more sense
- [ ] Rename species to a name that makes more sense
- [ ] Migrate to PyQt6

### User Interface & Display
- [ ] Correct the zoom model menu 
- [ ] Main window auto resize
- [ ] Integrate two features from Enhanced Grid layout that are still missing : position readjsuted to save space (shrinked), and move up/down to control overlapping 
- [ ] create a "Theme system" to apply ready-to-use sgAspect to all gameSpaces (and a menu to edit, save and load themes of sgAspect)

### POV System & Visual Elements
- [ ] Create a aspect system for entities to replace pov (résolution hierarchique des aspects) + create views to manage groups of symbologies
- [ ] Add image support (JPG) in POV for legends and control panels
- [ ] Add possibility to integrate image icons in dashboards and progressGauge

### New Entities & Features
- [ ] New `entity`: Tile
- [ ] Add configurable min/max values for simulation variables
- [ ] Add a method to cell entity: getLastArrivedAgent

### Graphs & Analytics Interface
- [ ] Graphs interface : improve the selection menu of graphs
- [ ] Graphs interface : allow to hide all graphs that are flat (no value change)
- [ ] Graphs interface : allow the modeler to specify the graphs that he wants to see in the menu
- [ ] Graphs interface : allow to specify a multi-graph window with graphs specify by the modeler
- [ ] Improve data record of gameactions (perhaps using SGAbstractAction.updateServer_gameAction_performed())

### Simulation Management & Data
- [ ] Create automatic recording of simulation state at each round
- [ ] Create a recovery system for simulation in case it shuts down (could use `updateAtMaj` function)
- [ ] Allow to start the simulation at a specified time step
- [ ] Add a item in SGModel menu bar to record the state of the world (state of model entities), and add the possibility to use a saved state of the world, as an initialization state for a new simulation
- [ ] Add the possibility to export gameAction logs

### Multiplayer & Configuration
- [ ] Improve model configuration management for multiplayer games

### Documentation & Tools
- [ ] Create a system to extract automatically all modeler methods, to generate a SGE methods Glossary (kind of user technical guide)
- [x] Add in SGModel menu bar the possibility to choose the displayTooltip of entities (Dec 2024)
  - ✅ Added tooltip selection menu in SGModel Settings
  - ✅ Created individual tooltip submenus for each EntityDef (CellDef and AgentDef)
  - ✅ Implemented `setTooltip()` modeler method in SGEntityDef
  - ✅ Added support for attribute names, static text, and lambda functions
  - ✅ Created `hasAttribute()` method in AttributeAndValueFunctionalities
  - ✅ Removed obsolete "Custom" option from displayTooltip()
  - ✅ Added comprehensive examples in syntax_examples/
  - ✅ Menu dynamically updates when new EntityDefs are created


## Completed Items

### User Interface & Display
- [x] Implement zoom functionality for grids (Sept 2025)
  - ✅ Added mouse wheel zoom support for SGGrid (zoomIn/zoomOut)
  - ✅ Implemented independent zoom levels for multiple grids
  - ✅ Fixed agent positioning during zoom with recreation strategy
  - ✅ Corrected hexagonal cell positioning calculations
  - ✅ Added comprehensive zoom examples (ex_zoom_1.py, ex_zoom_2.py, ex_zoom_3.py)
  - ✅ Supports both square and hexagonal grids with agents
  - ✅ Maintains agent positions (center, corners, random) during zoom operations

- [x] Add a modeler style sheet config methods for `gameSpaces` who don't have yet (Sept 2025)
- [x] Unify font style sheets for `SGEndGameRule` (Sept 2025)
  - ✅ Unified all gameSpaces to use `gs_aspect` system consistently
  - ✅ Added missing `paintEvent()` methods for SGProgressGauge and SGEndGameRule
  - ✅ Implemented multi-theme system for SGEndGameCondition and SGControlPanel
  - ✅ Eliminated all hardcoded style adaptations
  - ✅ Added comprehensive style configuration methods for modelers
  - ✅ All gameSpaces now support: `setBorderColor()`, `setBorderSize()`, `setBackgroundColor()`, `setTextColor()`

- [x] Fix widget size management for `SGEndGameRule` and `SGTextBox` (Sept 2025)
- [x] Refactor auto resize of text spacings in `gameSpaces` (using geometry) (Sept 2025)
  - ✅ Created `SGGameSpaceSizeManager` class for dedicated size management
  - ✅ Integrated size manager into `SGGameSpace` base class
  - ✅ Fixed `SGTextBox` to dynamically adapt to text content
  - ✅ Fixed `SGEndGameRule` to dynamically adapt to number of conditions
  - ✅ Added automatic size adjustment when content changes
  - ✅ Eliminated hardcoded fixed sizes (160x100, 150x150)
  - ✅ Implemented content-based sizing similar to `SGLegend` pattern

- [x] Correct the drag and drop movement of `gameSpaces` (Sept 2025)
  - ✅ Refactored drag & drop system from QDrag-based to direct mouse movement
  - ✅ Implemented intuitive hotspot behavior (clicked point stays under cursor)
  - ✅ Fixed compatibility issues with SGControlPanel.mousePressEvent
  - ✅ Updated SGGrid.mouseMoveEvent to use new drag & drop implementation
  - ✅ Added proper drag state management (dragging flag, drag_start_position)
  - ✅ Eliminated non-intuitive positioning behavior
  - ✅ All gameSpaces now support smooth, intuitive drag & drop movement

- [x] Integrate the enhanced grid layout of `gameSpaces` (Sept 2025)
  - ✅ Created `SGEnhancedGridLayout` class inheriting from `SGAbstractLayout`
  - ✅ Added `"enhanced_grid"` as new `typeOfLayout` option in `SGModel`
  - ✅ Implemented `layoutOrder` system for automatic column organization
  - ✅ Added user interface for `layoutOrder` management via editable table dialog
  - ✅ Implemented polymorphic `applyLayout()` method across all layout classes
  - ✅ Added tooltip display for `layoutOrder` values
  - ✅ Support for manual positioning with `moveToCoords()` override
  - ✅ Integrate a menu and the possibility to export the settings (layoutOrders and/or absolute position)

## Notes

This future plan is regularly updated as new ideas emerge and priorities change. Each item represents a potential improvement or new feature for the SGE framework.
