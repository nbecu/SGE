# SGE - Simulation Game Editor

Welcome to SGE!

For detailed documentation for : 
- **modeler** (creating games/simulations with SGE), please see [README_modeler.md](./README_modeler.md) and the [SGE Methods Catalog](https://htmlpreview.github.io/?https://github.com/nbecu/SGE/blob/main_candidate_release_sept_2025/docs/SGE_methods/sge_methods_catalog.html).
- **developer** (contributing to the SGE library itself), please see [README_developer.md](./README_developer.md) and the [Architecture Diagrams](https://htmlpreview.github.io/?https://github.com/nbecu/SGE/blob/main_candidate_release_sept_2025/docs/archi_diagrams/index.html).



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



