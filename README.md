# SGE - Simulation Game Editor

Welcome to SGE!

> 📚For detailed documentation:
> - For **Modeler** (creating games/simulations with SGE) → [README_modeler.md](./README_modeler.md) and [SGE Methods Catalog](https://htmlpreview.github.io/?https://github.com/nbecu/SGE/blob/main/docs/SGE_methods/sge_methods_catalog.html)
> - For **Developer** (contributing to the SGE library) → [README_developer.md](./README_developer.md) and [Architecture Diagrams](https://htmlpreview.github.io/?https://github.com/nbecu/SGE/blob/main/docs/archi_diagrams/index.html)

SGE (Simulation Game Editor) is a simulation game editor. It enables the modeling of a simulated environment and the integration of players who interact with the simulation elements through game actions. To enhance the user experience, SGE supports the addition of UI/UX game components—such as buttons, menus, dashboards, graphs, and end-game rules.
The three pillars of SGE are:
- a simulated environment,
- players,
- UI/UX game components.

These are explicit modeling classes in SGE, which can be manipulated, specified, and parameterized by the modeler.
Among existing modeling platforms, SGE stands at the intersection of a multi-agent modeling platform and a board game editor. It allows for the modeling of agents and cellular grids in interaction, each with autonomous behavior, as well as the definition of players, game spaces, and rules for placing or moving game pieces.


Developing a simulation game in SGE involves writing a script using SGE’s primitives, which automate the creation, specification, and graphical rendering of simulation elements. SGE’s Domain-Specific Language (DSL) is designed so that a modeler can implement a complete simulation game in about forty lines of code.

When a model is executed in SGE, the platform initializes the simulation entities and automatically generates all graphical elements and user controls, enabling players to interact with the simulation via a point-and-click interface.

The simulation runs turn-by-turn, with the platform automatically managing two distinct types of phases: play phases for player interactions, and model phases for activating agents and other autonomous entities. 

Simulation data and player actions are automatically recorded and can be visualized through various types of graphs (linear, circular, histograms, stack plots).


# Installation

## Prerequisites

- Python 3.10 or higher
- Git
- **PyQt6** (automatically installed as a dependency)

## Installation Steps

Execute the following commands in your terminal:

1. **Clone the SGE repository:**
```bash
git clone https://github.com/nbecu/SGE.git
cd SGE
```

2. **(Recommended) Create and activate a virtual environment:**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install SGE with all its dependencies:**
```bash
pip install .
```
This command reads the `pyproject.toml` file and will automatically install SGE along with all dependencies listed in it.

**Note:** 
- On Windows, `pywin32` will be automatically installed as part of the dependencies. On macOS/Linux, this dependency will be skipped.
- **PyQt6** is required and will be installed automatically. SGE migrated from PyQt5 to PyQt6 as of May 31, 2026. If you need the last PyQt5 version, use: `git checkout version_release_2026_05_26_last_pyqt5`