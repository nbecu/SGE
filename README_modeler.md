# SGE - Simulation Game Editor (For Modelers)

> Have you ever dreamed of an editor that easily turns your simulation grid-based game following an agent-based approach ideas into reality? 

Simulation Game Editor (SGE) is a Python-based solution powered by PyQt5. Its aim is to help game modellers create grid-based simulation games using an agent-based approach without having to redevelop the basic interface and calculation functionality. Modelling a game in SGE essentially consists of **defining the various structural elements** of the game and **setting variables**.

SGE is unique compared with other pre-existing simulation development tools: it implements the notion of viewpoints, players, game actions and game phases directly into the structure of the model, like ready-to-use packs. SGE makes it possible to create  **distributed asymmetric simulations**: each player can interact with the others according to their skills, their personal understanding of the situation and a specific computer interface running on a chosen computer terminal.

> Calculate, test, develop but faster

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

### `moveAgent(method, direction, target, condition)`
- **Purpose**: Move agent using predefined movement patterns
- **Handles**: Movement only (agent must already be placed)
- **Usage**: Requires agent to be already on a cell
- **Methods**: `"random"`, `"cardinal"`, `"cell"`
- **Example**: `agent.moveAgent(method="random", condition=lambda cell: cell.isNotValue("terrain", "metal"))`

**Important**: Use `moveTo()` for initial placement, `moveAgent()` for subsequent movements.

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