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

- **new**: To create a new type of entity (e.g., `newCellsOnGrid`, `newAgentSpecies`), a new entity instance (e.g., `newAgentAtCoords()`), or a new game element (e.g., `newGamePhase()`, `newLegend`).
- **get**: To access or retrieve an element from the simulation (e.g., `getPlayer`, `getScore`).
- **delete**: To remove an element from the simulation (e.g., `deleteEntity`, `deleteAllAgents()`).
- **set**: To modify the value of a parameter or property of an element (e.g., `setParameter`, `setName`, `setEntities_withColumn()`, `setDefaultValues()`).
- **add**: To add a new element to an existing type or to add a feature to an existing element (e.g., `addAction`, `addIndicator`).
- **nb**: To obtain the number of entities, objects or instances.
- **is**: To perform a test (returns True or False) (e.g., `isDeleted()`).
- **do_**: To perform an action on an entity.

---

## 4. General Recommendations

- All docstrings and comments must be written in English.
- Be consistent with naming and terminology throughout the codebase.
- When in doubt, refer to existing SGE code for examples of good practice.

---

## 5. Additional Information

For more information about SGE usage and modeling, see `README_modeler.md`.

---

## 6. Future Plan
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
