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

## 4. Type Identification Attributes

Use boolean attributes with the `is` prefix to identify the type of object and enable different behaviors:

- **`isAdmin`**: For players (e.g., `self.isAdmin = True` for admin players)
- **`isAgentDef`**: For entity definitions (e.g., `self.isAgentDef = True` for agent species)
- **`isCellDef`**: For entity definitions (e.g., `self.isCellDef = True` for cell types)
- **`isLegend`**: For UI components (e.g., `self.isLegend = True` for pure legend display)
- **`isControlPanel`**: For UI components (e.g., `self.isControlPanel = True` for control interfaces)

These attributes help separate responsibilities and enable type-specific behavior without complex inheritance hierarchies.

---

## 5. API Ergonomics and Delegation

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

### Complex Instance Creation
Use `new` prefix methods for creating complex instances with multiple parameters:

```python
def newModifyActionWithDialog(self, entityDef, attribute):
    # Creates a modify action that prompts user for value
```


---

## 6. General Recommendations

- All docstrings and comments must be written in English.
- Be consistent with naming and terminology throughout the codebase.
- When in doubt, refer to existing SGE code for examples of good practice.

---

## 7. Additional Information

For more information about SGE usage and modeling, see `README_modeler.md`.

---

## 8. Future Plan
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
