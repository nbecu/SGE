# SGE - Future Plan

This document contains the planned improvements and features for the SGE (Simulation Game Editor) project.

## Current Development Items

### Core Architecture & Framework
- [ ] Unify definition of `setValue` for the different classes
- [ ] Migrate to PyQt6
- [ ] Refactor getter methods in SGModel for consistent object retrieval by name (see REFACTORING_GETTER_METHODS.md)
- [ ] Refactor SGModel: Extract Game Action Export (lines 458-824) and Layout Management (lines 1271-1424) methods into separate classes using composition pattern

### User Interface & Display
- [ ] Main window auto resize
- [ ] Integrate two features from Enhanced Grid layout that are still missing : position readjsuted to save space (shrinked), and move up/down to control overlapping 
- [x] Background images in GameSpaces: add scaling modes (cover/contain/stretch) (June 2026) ✅ RELEASED
   - ✅ Added `gs_aspect.background_image_mode` with values: `cover`, `contain`, `stretch` (default: `stretch`)
   - ✅ Implemented rendering logic in all GameSpaces `paintEvent` with proper zoom integration
   - ✅ Exposed modeler API: `setStyle({ 'background_image_mode': 'cover' })`
- [x] GameSpace background image zoom: scale background image proportionally with zoom level (June 2026) ✅ RELEASED
   - ✅ **Default behavior:** background image scales with zoom (resize & magnifier modes)
   - ✅ **Configurable:** `setBackgroundImageZoom(False)` or `setStyle({ 'background_image_zoom_enabled': False })`
   - ✅ **Transparent cells alignment:** fixed to properly align with background image during zoom
   - ✅ **Code deduplication:** extracted `_calculateBackgroundImageViewport()` helper (single source of truth)
   - ✅ **Cover mode fix:** corrected negative offset coordinates in cover mode
   - ⏳ **Known limitation:** magnifier mode with `zoom_enabled=False` in complex scenarios (deferred to future iteration)
- [x] Bug on drag and move on SGGrid : impossible to drag on the right border (June 2026) ✅ FIXED
   - ✅ **Root cause:** Cells in magnifier mode were getting Qt's default geometry (100x30px) instead of intended size (40x40px)
   - ✅ **Fix:** Added explicit `cell.view.resize()` call in `_updatePositionsForViewport()` to set correct cell dimensions
   - ✅ **Result:** Cells now fit within grid bounds (257px right edge <= 266px grid width), right border drag works
- [ ] In SGGid, consider using getGridBoundsWidth()/getGridBoundsHeight() instead of getSizeXGlobal()/getSizeYGlobal(), because these two last methods add 1px for an undertermined reason

### POV System & Visual Elements
- [ ] Create a aspect system for entities to replace pov (résolution hierarchique des aspects) + create views to manage groups of symbologies
- [x] Add image support (JPG) in POV for legends and control panels
- [ ] Add possibility to integrate image icons in dashboards and progressGauge

### New Entities & Features
- [X] New `entity`: Tile
- [ ] Add configurable min/max values for simulation variables
- [x] Add a method to cell entity: getLastArrivedAgent
- [x] Add addEndGameCondition_onSimVar to SGEndGameRule — takes a SimVar directly instead of requiring the modeler to go through an Indicator
- [ ] Enhance Tile integration with POV system (improve existing inheritance-based integration for better tile-specific POV support)
- [ ] Clean and refactor SGDashboard to identify properly the modeler methods (and tests them), to rename better args : name title, displayName which are confusing,....
- [ ] Allow placing agents on Tiles (add ability to place agents directly on tiles, not just on cells)

### Graphs & Analytics Interface
- [x] Graphs interface : improve the selection menu of graphs (dynamic group combobox: Cells/Agents/Tiles; single_select for pie/stackplot/hist; hide flat indicators)
- [x] Graphs interface : allow to hide all graphs that are flat (no value change)
- [x] Graphs interface : allow the modeler to specify the graphs that he wants to see in the menu (`addGraphPreset` + `hideDefaultGraphMenuItems`)
- [x] Graphs interface : allow to specify a multi-graph window with graphs specify by the modeler (`newMultiGraphWindow` + `addPanel`)
- [ ] Histogram : allow multiple indicators simultaneously — requires either (1) recomputing bins on-the-fly over the combined value range, or (2) a shared fixed bin grid [global_min, global_max]. Currently limited to single_select because each indicator's bins are pre-computed independently at recording time.
- [x] `addGraphPreset`: add `x_axis` parameter to let the modeler specify the x-axis mode per preset (`'Rounds'`, `'Rounds & Phases'`, `'Specified phase'`).
- [x] `addGraphPreset`: show the graph type icon in front of the preset name in the Graphs menu.
- [x] `addGraphPreset` / `createGraphMenu`: add `myModel.hideDefaultGraphMenuItems()` API so the modeler can hide the default entries (Linear Chart, Histogram, Pie Chart, Stack Plot) that he wants to hide, while continuins to expose presets.
- [ ] Graph color management: when possible, use entity or entity-state colors defined in the model (e.g. `SGEntityType.color`, quali attribute state colors) instead of the fixed COLORS palette — fallback to current palette when no model color is defined.
- [ ] Graph indicator selection persistence: auto-save the selected indicators, group filter, and x_axis option when the user closes a graph window; auto-restore them on next open — no user interaction required. Use a `graph_config.json` file (same pattern as `layout_config.json` / `theme_config.json`), keyed by `model_name + graph_type` (or `model_name + preset_name`). Validate restored keys against available indicators on load and silently ignore missing ones (model may have changed). Note: fix the `sys.argv[0]` path issue first — it currently saves to the SGE root when running from an IDE instead of saving next to the model script.
- [ ] Improve data record of gameactions (perhaps using SGAbstractAction.updateServer_gameAction_performed())

### Simulation Management & Data
- [ ] Create a importData et exportData qui s'occupe d'aller chercher les bons chemins dans le rep projet
- [ ] Create automatic recording of simulation state at each round
- [ ] Create a recovery system for simulation in case it shuts down (could use `updateAtMaj` function)
- [ ] Allow to start the simulation at a specified time step
- [ ] Add a item in SGModel menu bar to record the state of the world (state of model entities), and add the possibility to use a saved state of the world, as an initialization state for a new simulation
- [ ] Add the possibility to export gameAction logs
- [ ] Define writable export paths for exe mode (see notes for FUTURE_PLAN/EXPORT_WRITE_PATHS.md)
- [x] Implement BotPlayer system for automated gameplay and testing (see docs/guides/BOT_PLAYER_SYSTEM.md). Bot tested and validated on TicTacToe.

### Multiplayer & Configuration
- [ ] Adapt Solutre game to the new Distributed Game Session system

### Documentation & Tools 


## Completed Items

- [x] Architectural improvements — branch `dev_claude_archi_improves` (May 2026)
  - ✅ P1: Replaced all 30 star imports in SGModel.py with explicit named imports — eliminates silent namespace collisions and makes dependencies visible
  - ✅ P2: Added `getAllGameSpaces()` to SGModel — unifies `gameSpaces` and `TextBoxes` into a single iterable
  - ✅ P4: Decomposed `SGTimeManager.nextPhase()` into `_advanceCounters()`, `_updateCurrentPlayer()`, `_executeAndRefresh()` — from 70-line god method to readable 20-line orchestrator
  - ✅ P5: Removed 4 dead imports from SGModel.py (`email.policy.default`, `logging.config.listen`, `paho.mqtt`, `pyrsistent.s`)
  - ✅ P6: Added `SGAgent.repositionView()` — SGModel.positionAllAgents() no longer touches agent views directly; view orchestration stays on the agent
  - ✅ P7: Created `SGColors` class as single source of truth for named colors — replaced 170 lines of Qt monkey-patching repetition with a loop; `Qt.orange` etc. still work for backward compatibility
  - ✅ P8: Added `clearHistory(before_round=None)` to AttributeAndValueFunctionalities — prevents unbounded memory growth in long simulations
  - ✅ P9: Removed orphan comments in SGModel (`# self.users`, `# self.players  # Moved above`) and clarified dead ValueError branch in SGAgent
  - ✅ Installed pytest and reorganized `tests/` into effective pytest suite (54 tests, conftest.py, real assert statements, @pytest.mark.parametrize)
  - ⏳ P3: Mixin couplé à `model.timeManager` — effort élevé, reporté
  - ⏳ P10: SGGameSpaceSizeManager par instance — état per-instance justifié (setters effectivement utilisés), non corrigé
  - ✅ SGModel section cleanup (chantier B, May 2026) — all 19 sections have 4-space indented headers and passive outline methods; SETTINGS MENU, THEME AND SYMBOLOGY sections added
  - ✅ Replaced `hasattr(self, 'type')` anti-pattern with explicit `isEntity`/`isEntityType` boolean flags on SGEntity and SGEntityType — consistent with existing isAgentType/isCellType/isTileType convention
  - ✅ Expanded test suite to 94 tests across 4 files: simulation cycles (28 tests — Cell, Agent, Tile, SimVariable, movement, watchers, history), player and game actions (12 tests — all 5 GameAction types + BotPlayer), polymorphism (12 tests)
  - ✅ Closed both architecture diagnostics (Nov 2025 and May 2026) — all items resolved or explicitly deferred

- [x] Finalize distributed game system (Jan 2025)
  - ✅ Complete implementation of session management with create/join modes
  - ✅ Implement player role selection dialog with reservation system
  - ✅ Add connection error handling with user-friendly warnings
  - ✅ Create comprehensive guides for modelers and players
  - ✅ All features documented and tested

- [x] Correct the zoom model menu (Dec 2024)
  - ✅ Implemented zoomPlusModel() to zoom in all grids
  - ✅ Implemented zoomLessModel() to zoom out all grids  
  - ✅ Implemented zoomFitModel() to reset zoom for all grids
  - ✅ Connected menu bar icons to working zoom functionality
  - ✅ Used getGrids() method to iterate through all model grids

- [x] Create a system to extract automatically all modeler methods, to generate a SGE methods Glossary (kind of user technical guide) (Sept 2025)

- [x] Refactor SGModel to follow the ordering convention of SGE for modeler methods (Sept 2025)
  - ✅ Added proper section separators for MODELER METHODS
  - ✅ Organized methods by type: NEW/ADD/SET, DELETE, GET/NB, IS/HAS, DO/DISPLAY
  - ✅ Moved developer methods to DEVELOPER METHODS section
  - ✅ Organized developer methods into logical sub-sections by responsibility
  - ✅ Added placeholder methods for IDE outline visibility
  - ✅ Maintained all functionality while improving code organization

- [x] Extract MQTT functionality into SGMQTTManager class (Sept 2025)
  - ✅ Created new SGMQTTManager class for all MQTT logic
  - ✅ Refactored SGModel to delegate MQTT calls to SGMQTTManager
  - ✅ Separated MQTT protocol configuration from game launch logic
  - ✅ Added optional broker host parameter for modelers (localhost or online)
  - ✅ Maintained all MQTT functionality while improving separation of concerns

- [x] Rename EntDef to a name that makes more sense (Sept 2025)
  - ✅ Renamed SGEntityDef → SGEntityType, SGCellDef → SGCellType, SGAgentDef → SGAgentType
  - ✅ Renamed attributes: classDef → type, entityName → name
  - ✅ Renamed methods: entityType() → category(), newAgentType() → newAgentType()
  - ✅ Updated all imports, references, and examples
  - ✅ Fixed ControlPanel LegendItems display issue
  - ✅ All tests and examples working correctly
- [x] Rename species to a name that makes more sense

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

- [x] Add in SGModel menu bar the possibility to choose the displayTooltip of entities (Sept 2025)
  - ✅ Added tooltip selection menu in SGModel Settings
  - ✅ Created individual tooltip submenus for each EntityDef (CellDef and AgentDef)
  - ✅ Implemented `setTooltip()` modeler method in SGEntityDef
  - ✅ Added support for attribute names, static text, and lambda functions
  - ✅ Created `hasAttribute()` method in AttributeAndValueFunctionalities
  - ✅ Removed obsolete "Custom" option from displayTooltip()
  - ✅ Added comprehensive examples in syntax_examples/
  - ✅ Menu dynamically updates when new EntityDefs are created

- [x] Integrate the enhanced grid layout of `gameSpaces` (Sept 2025)
  - ✅ Created `SGEnhancedGridLayout` class inheriting from `SGAbstractLayout`
  - ✅ Added `"enhanced_grid"` as new `typeOfLayout` option in `SGModel`
  - ✅ Implemented `layoutOrder` system for automatic column organization
  - ✅ Added user interface for `layoutOrder` management via editable table dialog
  - ✅ Implemented polymorphic `applyLayout()` method across all layout classes
  - ✅ Added tooltip display for `layoutOrder` values
  - ✅ Support for manual positioning with `moveToCoords()` override
  - ✅ Integrate a menu and the possibility to export the settings (layoutOrders and/or absolute position)

- [x] Improve Method Catalog HTML interface (setp 2025)
  - ✅ Fixed scroll behavior: only content panel scrolls, header and sidebar remain fixed
  - ✅ Replaced class filter dropdown with blue buttons for better ergonomics
  - ✅ Added "All" button for class filtering
  - ✅ Implemented hierarchical filtering: class buttons act as first-level filter
  - ✅ Added alphabetical sorting of methods within each category
  - ✅ Made method cards expandable/collapsible with +/- indicators
  - ✅ Added dynamic method count updates based on visible methods
  - ✅ Implemented logical SGE category order (NEW, ADD, SET, DELETE, GET, NB, IS, HAS, DO, DISPLAY, OTHER)
  - ✅ Added "Expand All Methods" button in header with green styling
  - ✅ Improved inheritance display: moved "(from ClassName)" to separate line above signature
  - ✅ Unified inheritance styling between classes and methods
  - ✅ Fixed header overlap with proper spacing (200px margin)
  - ✅ All changes integrated into source code for persistence

- [x] Create a "Theme system" to apply ready-to-use gs_aspect to all gameSpaces (Jan 2025)
  - ✅ Implemented complete theme system with predefined themes (modern, minimal, colorful, blue, green, gray)
  - ✅ Created Custom Theme Editor dialog for creating and editing custom themes
  - ✅ Added theme persistence in `theme_config.json` with automatic loading at startup
  - ✅ Implemented Theme Assignment dialog for assigning themes to GameSpaces
  - ✅ Added dynamic discovery of predefined themes from `SGAspect.py`
  - ✅ Implemented "Apply to All..." functionality for global theme application
  - ✅ Added theme code generation for promoting custom themes to predefined
  - ✅ All GameSpaces support theme application via `applyTheme(theme_name)`
  - ✅ Theme configurations can be saved and loaded via `applyThemeConfig(config_name)`

- [x] Uniformize font style management across all GameSpaces classes (Jan 2025)
  - ✅ Migrated all 12 GameSpaces to use unified `gs_aspect` system
  - ✅ Refactored `onTextAspectsChanged()` methods to use centralized helpers
  - ✅ Created helper methods: `_applyAspectToLabel()`, `mapAlignmentStringToQtFlags()`, `applyToQFont()`, `applyToQLabel()`
  - ✅ Reduced code duplication by ~60-70% across all GameSpaces
  - ✅ All GameSpaces support consistent style methods: `setTextColor()`, `setFontSize()`, `setFontFamily()`, etc.
  - ✅ Unified style application through `gs_aspect` for both container and text styles
  - ✅ All styles pass through `gs_aspect` ensuring consistent behavior

- [x] Generalize background image support via gs_aspect across all GameSpaces (Jan 2025)
  - ✅ Implemented `setBackgroundImage()` method in `SGGameSpace` base class
  - ✅ Added `gs_aspect.background_image` attribute support
  - ✅ Implemented `getBackgroundImagePixmap()` helper method with fallback to background color
  - ✅ Extended background image support to all GameSpaces using `paintEvent()` (SGTextBox, SGDashBoard, SGEndGameRule, SGUserSelector, SGProgressGauge, SGTimeLabel, SGVoid, SGLabel, SGButton, SGLegend, SGGrid)
  - ✅ Background images can be set via `setBackgroundImage(path_or_qpixmap)` or `setStyle({ 'background_image': 'path' })`
  - ✅ All GameSpaces now support using images instead of colors for background

## Git Branch Organization Convention

SGE follows a structured branch naming convention:
- **`main`** → Main development branch
- **`version_*`** → Stable released versions (e.g., `version_august_2025`)
- **`candidate_*`** → Release candidates (e.g., `main_candidate_release_sept_2025`)
- **`dev_*`** → Active development branches
- **`project_*`** → Project-specific branches
- **`legacy_*`** → Historical/archived branches
- **`experimental_*`** → Experimental features

Workflow: `dev_*` → `candidate_*` → `version_*` → `legacy_*`

## Notes

This future plan is regularly updated as new ideas emerge and priorities change. Each item represents a potential improvement or new feature for the SGE framework.
