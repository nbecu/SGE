# SGE - Future Plan

This document contains the planned improvements and features for the SGE (Simulation Game Editor) project.

## Current Development Items

### Core Architecture & Framework
- [ ] Unify definition of `setValue` for the different classes
- [ ] Migrate to PyQt6

### User Interface & Display
- [ ] Correct the zoom model menu 
- [ ] Main window auto resize
- [ ] Integrate two features from Enhanced Grid layout that are still missing : position readjsuted to save space (shrinked), and move up/down to control overlapping 
- [ ] create a "Theme system" to apply ready-to-use gs_aspect to all gameSpaces (and a menu to edit, save and load themes of sgAspect)

### POV System & Visual Elements
- [ ] Create a aspect system for entities to replace pov (résolution hierarchique des aspects) + create views to manage groups of symbologies
- [ ] Add image support (JPG) in POV for legends and control panels
- [ ] Add possibility to integrate image icons in dashboards and progressGauge

### New Entities & Features
- [ ] New `entity`: Tile
- [ ] Add configurable min/max values for simulation variables
- [ ] Add a method to cell entity: getLastArrivedAgent
- [ ] Améliorer le systeme de addEndGameCondition_onIndicator    Pour l'instant pour une simVar, il faut prendre l'indicateur issu de la simVar --> il faudrait ajouter addEndGameCondition_onSimVar qui prend directement une simVar

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
- [ ] Amélioratin de MethodCatalog - html à prévoir
      - quand on scroll, on veut scroller que le panneau de la liste des méthodes, et non pas le bandeau d'en-tete et le bandeau latéral
      - dans le panneau latéral, il y a une mauvaise ergonomie  de fonctionnalités entre les 'boutons' bleu de la rubrique classes et la liste déroulante Class de la rubrique Filters. Les boutons bleus agissent comme des marqueurs pour scroller direction aux différentes sections. Cette fonctionnalité est intéressante mais le rendu graphique la met trop en avant. Il faudrait que ce soit plus discret, et positinné ailleurs. Le rendu graphique des 'boutons bleus' est très esthétique. Il faudrait remplacer la liste déroulante de filtre de class, par un système de 'boutons bleues' ayant cette même esthétique (ce remplacement ne concerne que class ; les autres types de filtre sont à garder tel quel). 
      trier les méthodes listés dans chaque catégorie par ordre alphabétique
      - pemrettre de déplier l'encadrer de chaque méthode
      - dans le panneau de la liste des méthodes, au niveau de l'intitulé du nom de class, juste en dessous, il est affiché le décompte du nombre de méthode. Je veux que le nombre affiché correspondent au nombre de méthodes présentement affichés pour cette class
      - dans le panneau de la liste des méthodes, au niveau de l'encart pour chaque classes, je veux que sectins de chaque catégorie soient affichés selon l'ordre logique utilisé dans SGE. Je veux que cet ordre logique soit stocké quelque part dans le code , et qu'il soit appaelé programatiquement à chaque fois qu'on en a besoin, afin que si plus tard cet oprdre change, ça soit prit en compte automatiqeemnet. Cet ordre logique est New add set, detele get, nb is, has, do , display, other. 
      - dans le panneau de la liste des méthodes, au niveau de l'encart pour chaque classes, pour chaque   section de catégorie, je veux ques les méthodes soient triés par ordre alphabétique 


## Completed Items

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
