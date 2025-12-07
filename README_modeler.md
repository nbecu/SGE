# SGE - Simulation Game Editor (For Modelers)

Simulation Game Editor (SGE) is a Python-based framework designed to help game/simulation modelers create their own game/simulation efficiently. With SGE, you can focus on defining game pieces, game actions, autonomous agents, and grid-based gameboards (including neighbor calculations), without needing to redevelop the underlying interface or computational logic.
Modeling a game/simulation in SGE is intuitive: it primarily involves defining and parameterizing the structural elements of your project using SGE’s primitives. The platform automatically generates a ready-to-use interface, allowing players to interact with the game/simulation directly through a dedicated window.


## How does it work ?

SGE is like a puzzle, all the pieces are already here, you just need to give it order and custom to create your ideas.

![image](https://github.com/nbecu/SGE/assets/119414220/888f6d78-5434-4b70-8969-0b1e971a4b8e)

## Agent Movement Methods

SGE provides two main methods for moving agents:

### `moveTo(destinationCell)`
- **Purpose**: Move agent to a specific cell
- **Handles**: Both initial placement and movement
- **Usage**: Can be used immediately after agent creation
- **Example**: `agent.moveTo(targetCell)`

### `moveAgent(method, target, numberOfMovement, condition)`
- **Purpose**: Move agent using predefined movement patterns
- **Handles**: Movement only (agent must already be placed)
- **Usage**: Requires agent to be already on a cell

#### Movement Methods:

**1. Random Movement:**
```python
agent.moveAgent()  # Random movement to any neighbor
agent.moveAgent(condition=lambda cell: cell.isNotValue("terrain", "metal"))
```

**2. Cell Movement:**
```python
agent.moveAgent(target=53)        # Move to cell with ID 53
agent.moveAgent(target=(5, 7))   # Move to cell at coordinates (5, 7)
```

**3. Direction Movement:**
```python
agent.moveAgent(target="up")      # Move north
agent.moveAgent(target="down")    # Move south
agent.moveAgent(target="left")    # Move west
agent.moveAgent(target="right")   # Move east
```

**4. Auto-detection (when method='random'):**
```python
agent.moveAgent(target=53)        # Auto-detects as cell movement
agent.moveAgent(target=(5, 7))   # Auto-detects as cell movement
agent.moveAgent(target="up")     # Auto-detects as direction movement
```

**Important**: Use `moveTo()` for initial placement, `moveAgent()` for subsequent movements.

## Layout Options

SGE supports different layout types for organizing gameSpaces:
- **`"vertical"`**, **`"horizontal"`**, **`"grid"`**: Standard layouts
- **`"enhanced_grid"`**: Advanced layout with automatic column organization and user-controllable ordering

Example: `model = SGModel(typeOfLayout="enhanced_grid")`

### Enhanced Grid Layout Configuration

For Enhanced Grid Layout, you can save and load layout configurations:

```python
# Save current layout configuration
model.saveLayoutConfig("my_layout")

# Load a saved configuration
model.loadLayoutConfig("my_layout")

# Check available configurations
configs = model.getAvailableLayoutConfigs()
```

## Game Actions Interaction Modes

SGE provides multiple ways to trigger game actions. Each action type can be configured with `interaction_modes` to control how it can be triggered:

### Interaction Modes Configuration

The `interaction_modes` parameter is a dictionary that controls where and how actions can be triggered:

- **`controlPanel`** (bool, default: `True`): Action appears in the ControlPanel
- **`contextMenu`** (bool, default: `False`): Action appears in the right-click context menu
- **`button`** (bool, default: `False`): Action appears as a button (only for Activate actions)
- **`directClick`** (bool, default: `False`): Action triggers automatically on left-click without selection in ControlPanel
  - `True`: Action can be triggered directly by clicking on the entity
  - `False`: Action requires selection in ControlPanel first
  - Note: Move actions use drag & drop by default (independent of directClick)

### Game Actions Summary Table

| Type d'Action | Entités Cibles | ControlPanel | Menu Contextuel | Bouton | DirectClick (défaut) | DirectClick (souhaité) | Notes |
|---------------|----------------|--------------|-----------------|--------|----------------------|------------------------|-------|
| **Modify** | Agents, Tiles, Cells | ✅ (défaut) | ✅ (optionnel) | ❌ | `False` | - | Pas de directClick |
| **Activate** | Agents, Tiles, Cells, Model | ✅ (défaut) | ✅ (optionnel) | ✅ (`button=True`) | `False` | `True` | Peut être activé |
| **Delete** | Agents, Tiles, Cells | ✅ (défaut) | ✅ (optionnel) | ❌ | `False` | `True` | Peut être activé |
| **Create** | Cells (pour créer Agents/Tiles) | ✅ (défaut) | ❌ | ❌ | `False` | `True` | Peut être activé |
| **Move** | Agents, Tiles | ✅ (défaut) | ✅ (optionnel) | ❌ | `False` | - | Drag & drop par défaut (indépendant) |
| **Flip** | Tiles | ✅ (défaut) | ✅ (optionnel) | ❌ | `True` | - | Défaut = directClick |

### Examples

```python
# Flip with directClick=True (default)
flipAction = myModel.newFlipAction(
    tile_type,
    interaction_modes={
        "controlPanel": True,
        "contextMenu": True,
        "directClick": True  # Default for Flip
    }
)

# Activate with button and directClick=True
activateAction = myModel.newActivateAction(
    agent_type,
    aMethod=lambda: doSomething(),
    interaction_modes={
        "controlPanel": True,
        "button": True,
        "buttonPosition": (100, 200),  # Position for button
        "directClick": True  # Optional, not default
    }
)

# Move with drag & drop (default, independent of directClick)
moveAction = myModel.newMoveAction(
    agent_type,
    interaction_modes={
        "controlPanel": True
        # Move actions use drag & drop by default (independent of directClick)
    }
)
```

## Styling GameSpaces

SGE provides a unified styling system (`gs_aspect`) that allows you to style GameSpaces using different syntaxes:

### Syntax Options

**1. Style parameters in factory method:**
```python
timeLabel = myModel.newTimeLabel("Game Time", backgroundColor=Qt.cyan, textColor=Qt.darkBlue, borderColor=Qt.blue)
dashboard = myModel.newDashBoard("Scores", borderColor=Qt.red, backgroundColor=Qt.yellow, textColor=Qt.black)
```

**2. Style methods after creation:**
```python
timeLabel = myModel.newTimeLabel("Game Time")
timeLabel.setBackgroundColor(Qt.cyan)
timeLabel.setTextColor(Qt.darkBlue)
timeLabel.setBorderColor(Qt.blue)
```

**3. Mix both syntaxes:**
```python
timeLabel = myModel.newTimeLabel("Game Time", backgroundColor=Qt.cyan, textColor=Qt.blue)
timeLabel.setBorderColor(Qt.darkCyan)  # Modify after creation
```

All syntaxes pass through the unified `gs_aspect` system, ensuring consistent styling behavior. You can also use themes to apply predefined styles:

```python
gameSpace.applyTheme('modern')  # Apply a predefined theme
```

See `examples/syntax_examples/ex_game_space_style_various_syntax.py` for complete examples.

## Method Catalog

SGE provides a comprehensive method catalog to help modelers discover and use available methods:

### Generated Files
- **`sge_methods_catalog.json`**: Complete method catalog in JSON format
- **`sge_methods_catalog.html`**: Interactive HTML documentation with advanced filtering
- **`sge_methods_snippets.json`**: VS Code/Cursor snippets for code completion

### Method Categories
Methods are organized into categories:
- **NEW**: Creation methods (`newAgent`, `newCell`, `newModelPhase`)
- **SET**: Value modification methods (`setValue`, `incValue`, `decValue`)
- **GET**: Data retrieval methods (`getValue`, `getCell`, `getEntities`)
- **NB**: Counting methods (`nbAgents`, `nbCells`)
- **DELETE**: Removal methods (`deleteEntity`, `deleteAllAgents`)
- **IS/HAS**: Boolean test methods (`isValue`, `hasAgent`, `isEmpty`)
- **DO**: Action methods (`moveTo`, `moveAgent`, `moveRandomly`)
- **DISPLAY**: UI methods (`displayTimeInWindowTitle`, `show`)
- **METRIC**: Statistical/metrics calculation methods (`metricOnEntities`, `metricOnEntitiesWithValue`) - Available on EntityTypes (AgentType, CellType, TileType)

### Usage
The method catalog includes inherited methods from parent classes, making it easy to discover all available functionality for each entity type.

## Game Action Logs Export

SGE provides functionality to export game action logs for analysis and debugging (see `exportGameActionLogs` and `enableAutoSaveGameActionLogs` in the methods catalog).

## Folder hierarchy
- Examples
  - example1.0.py
- mainClasses
  - gameActions
  - layout
  - SGModel.py
  - SGGrid.py
  - ...
- Game
  - myGame.py

We encourage you to start your own game with an example to better understand SGE. You can seek the documentation [here](link to online doc)

## Requirements
```
python            3.8+
numpy             1.24.2
paho-mqtt         1.6.1
PyQt5             5.15.9
PyQt5-Qt5         5.15.2
PyQt5-sip         12.11.1
SQLAlchemy        2.0.3
pyrsistent
matplotlib
pywin32
```

## Context
SGE is developped under the supervision of [LIENSs](https://lienss.univ-larochelle.fr/) Laboratory (La Rochelle University, France) within different research projects. 
SGE answer to an academic need in serious game to have simplier ways to create serious games.
SGE first version was presented at [ISAGA 2023](https://apps.univ-lr.fr/cgi-bin/WebObjects/Colloque.woa/1/wa/colloque?code=3141).

## Authors and contributors
@nbecu Nicolas Becu
@Neraliel Marine Regien
@aossant Alexis Ossant

## License
SGE is under open-source license (CECILL V2). The license allows modification, copy and distribution along with contract terms. Modified version should preserve CECILL V2 License.