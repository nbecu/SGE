# SGE - Developer Guidelines

This document is intended for developers contributing to the SGE library itself.

## 1. Roles and Terminology

SGE distinguishes three types of users interacting with the SGE environment:

- **Player**: The person who interacts with a game/simulation executed by SGE.
- **Modeler**: The person who develops a game/simulation using the SGE library.
- **Developer**: The person who develops new features for the SGE library itself.

Always use the terms **game/simulation**, **player**, **modeler**, and **developer** as defined above in documentation and code comments.

---

## 2. Naming Conventions

- **Function and variable names**: Use `snake_case` (e.g., `auto_forward`, `player_score`).
- **Method and function names**: Use `camelCase` (e.g., `newModelPhase`, `getEntityByName`).

---

## 3. Reserved Keywords for Method Names

When creating new methods or functions intended for modelers, always use the following reserved keywords as prefixes, whenever possible:

- **new**: To create a new type of entity (e.g., `newCellsOnGrid`, `newAgentSpecies`), a new entity instance (e.g., `newAgentAtCoords()`), or a new game element (e.g., `newPlayPhase()`, `newLegend`).
- **get**: To access or retrieve an element from the simulation (e.g., `getPlayer`, `getScore`).
- **delete**: To remove an element from the simulation (e.g., `deleteEntity`, `deleteAllAgents()`).
- **set**: To modify the value of a parameter or property of an element (e.g., `setParameter`, `setName`, `setEntities_withColumn()`, `setDefaultValues()`).
- **add**: To add a new element to an existing type or to add a feature to an existing element (e.g., `addAction`, `addIndicator`).
- **nb**: To obtain the number of entities, objects or instances.
- **is**: To perform a test (returns True or False) (e.g., `isDeleted()`).
- **do_**: To perform an action on an entity.
- **display**: To display an element on the SGE User Interface.

---

## 4. Method Organization Convention

### 4.1 Class Structure
Classes should be organized with a clear separation between developer methods and modeler methods:

1. **Developer Methods** (at the top of the class)
   - Constructor (`__init__`)
   - Internal helper methods
   - UI delegation methods
   - Model-View architecture methods
   - Utility methods for developers

2. **Visual Separator** (clear line with comment)
   ```python
   # ============================================================================
   # MODELER METHODS
   # ============================================================================
   ```

3. **Modeler Methods** (at the bottom of the class)
   - Organized by type using the reserved keywords above

### 4.2 Modeler Methods Organization
Within the modeler methods section, organize methods in the following order:

1. **NEW/ADD/SET Methods** (creation and modification)
   ```python
   # ============================================================================
   # NEW/ADD/SET METHODS
   # ============================================================================
   ```

2. **DELETE Methods** (removal)
   ```python
   # ============================================================================
   # DELETE METHODS
   # ============================================================================
   ```

3. **GET/NB Methods** (retrieval and counting)
   ```python
   # ============================================================================
   # GET/NB METHODS
   # ============================================================================
   ```

4. **IS/HAS Methods** (testing)
   ```python
   # ============================================================================
   # IS/HAS METHODS
   # ============================================================================
   ```

5. **DO/DISPLAY Methods** (actions, and display)
   ```python
   # ============================================================================
   # DO/DISPLAY METHODS
   # ============================================================================
   ```

6. **Other modeler methods** (other types of modele methods)
   ```python
   # ============================================================================
   # OTHER MODELER METHODS
   # ============================================================================
   ```

### 4.3 Example Structure
```python
class SGAgent(SGEntity):
    def __init__(self, ...):
        # Developer code
    
    # ============================================================================
    # DEVELOPER METHODS
    # ============================================================================
    
    def show(self):
        # UI delegation
    
    def updateView(self):
        # Model-View architecture
    
    # ============================================================================
    # MODELER METHODS
    # ============================================================================
    
    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================
    
    def moveTo(self, cell):
        # Movement method
    
    # ============================================================================
    # DELETE METHODS
    # ============================================================================
    
    # (No delete methods for agents)
    
    # ============================================================================
    # GET/NB METHODS
    # ============================================================================
    
    def getId(self):
        # Get agent ID
    
    def nbAgentsHere(self, specie=None):
        # Count agents
    
    # ============================================================================
    # IS/DO/DISPLAY METHODS
    # ============================================================================
    
    # (No is/do/display methods for agents)
```

---

## 5. Model-View Architecture

### 5.1 Overview
SGE implements a Model-View architecture to separate data/logic (Model) from UI/display (View) for core entities. This separation enables:
- **Fluid agent movement** without losing state
- **Better code organization** and maintainability
- **Cleaner separation of concerns** between game logic and UI

### 5.2 Core Classes

#### Model Classes (Data & Logic)
- **`SGAgent`**: Agent model containing game logic, attributes, and behavior
- **`SGCell`**: Cell model containing cell data, agents list, and cell logic

#### View Classes (UI & Display)
- **`SGAgentView`**: Agent view handling UI rendering, mouse events, and visual interactions
- **`SGCellView`**: Cell view handling cell rendering, click events, and visual display

### 5.3 Model-View Relationship
- Each **Model** has a corresponding **View** instance
- Models contain the **game logic** and **data**
- Views handle **UI rendering** and **user interactions**
- Views delegate **game actions** back to their corresponding models

### 5.4 Key Methods

#### `show()` Method
The `show()` method is crucial for proper UI display:
- **Purpose**: Makes the widget visible and ensures proper positioning
- **Usage**: Called after creating views or moving agents between grids
- **Interaction**: Works with `update()` to ensure visual updates

#### `update()` vs `repaint()`
- **`update()`**: Schedules a repaint event (asynchronous, Qt event-driven)
- **`repaint()`**: Forces immediate repaint (synchronous, blocking)
- **Best Practice**: Use `update()` for better performance and responsiveness

### 5.5 Implementation Guidelines

#### Creating Model-View Pairs
```python
# Use factory methods for consistent creation
agent = entityDef.newAgentAtCoords(x, y)  # Creates both model and view
cell = entityDef.newCell(x, y)            # Creates both model and view
```

#### Moving Agents Between Grids
```python
# When moving agents, ensure proper view parenting
agent.moveTo(newCell)
# The moveTo method handles:
# - Changing view parent to new grid
# - Calling show() for proper positioning
# - Processing Qt events for layout updates
```

#### View Lifecycle Management
```python
# Views are automatically managed by the Model-View system
# Developers should not manually create or destroy views
# Use the factory methods in SGEntityFactory
```

---

## 6. Type Identification Attributes

Use boolean attributes with the `is` prefix to identify the type of object and enable different behaviors:

- **`isAdmin`**: For players (e.g., `self.isAdmin = True` for admin players)
- **`isAgentDef`**: For entity definitions (e.g., `self.isAgentDef = True` for agent species)
- **`isCellDef`**: For entity definitions (e.g., `self.isCellDef = True` for cell types)
- **`isLegend`**: For UI components (e.g., `self.isLegend = True` for pure legend display)
- **`isControlPanel`**: For UI components (e.g., `self.isControlPanel = True` for control interfaces)

These attributes help separate responsibilities and enable type-specific behavior without complex inheritance hierarchies.

---

## 7. API Ergonomics and Delegation

### Delegation Methods
Prefer creating delegation methods in core classes (`SGModel`, `SGEntityDef`, `SGEntity`, `SGPlayer`) to simplify the API for modelers:

```python
# Instead of: model.timeManager.newPlayPhase(...)
# Use: model.newPlayPhase(...)

```

### Instance Getters
Use getter methods with the `get` prefix for important instances instead of direct attribute access:

```python
# Instead of: model.adminPlayer
# Use: model.getAdminPlayer()

def getAdminPlayer(self):
    return self.players.get("Admin")
```

### Utility Methods
Utility methods are centralized in `SGExtensions.py` to avoid code duplication and provide common functionality across the codebase. When creating new utility functions, consider adding them to this module rather than duplicating code in multiple classes.

### Complex Instance Creation
Use `new` prefix methods for creating complex instances with multiple parameters:

```python
def newModifyActionWithDialog(self, entityDef, attribute):
    # Creates a modify action that prompts user for value
```


---

## 8. General Recommendations

- All docstrings and comments must be written in English.
- Be consistent with naming and terminology throughout the codebase.
- When in doubt, refer to existing SGE code for examples of good practice.

---

## 9. Additional Information

For more information about SGE usage and modeling, see `README_modeler.md`.

---

## 10. Future Plan
- [ ] Add a method `displayBorderPov` (similar to `SGEntity>displayPov`).
- [ ] Create a POV system to manage groups of symbologies.
- [ ] Correct the zoom.
- [ ] Unify font style sheets for `SGEndGameRule`.
- [ ] Add a modeler style sheet config methods for `gameSpaces` who don't have yet.
- [ ] Main window auto resize.
- [ ] Refactor auto resize of text spacings in `gameSpaces` (using geometry).
- [ ] New `gameAction`: activate.
- [ ] Rename Update `gameAction` to Modify.
- [ ] Unify definition of `setValue` for the different classes.
- [ ] Create a recuperation system for simulation status with `updateAtMaj` functions.
