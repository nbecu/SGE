# **SGE - Simulation Game Editor**

> Have you ever dreamed of an editor that easily turns your simulation grid-based game following an agent-based approach ideas into reality? 

Simulation Game Editor (SGE) is a Python based solution powered by PyQt5. It aims to help game modellers to create a simulation grid-based game following an agent-based approach without having to develop the model: **you just need to change some variables**.

SGE is unique from other pre-existent simulation tools: it implements the notion of point of views, game actions and player time round directly in the model code, like an all-in-one pack. SGE aims to create **distributed asymmetric simulations**: every participant will be immersed in a different point of view according to their personal aptitudes and understandings.

> Calculate, test, develop but faster

## How does it work ?

SGE is like a puzzle, all the pieces are already here, you just need to give it order and custom to create your ideas.

![image](https://github.com/nbecu/SGE/assets/119414220/888f6d78-5434-4b70-8969-0b1e971a4b8e)

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
```

## Future plan
- [ ] add a method "displayBorderPov" (similar to SGEntity>displayPov)
_ [ ] create a POV system to manage groups of symbologies
- [ ] correct the zoom
- [ ] unify font style sheets for SGEndGameRule
- [ ] add a modeler style sheet config methods for gameSpaces who don't have yet
- [ ] main window auto resize
- [ ] refractoring auto resize of text spacings in gameSpaces (using geometry)
- [ ] new gameAction : activate
- [ ] rename Update gameAction to Modify
- [ ] unify definition of setValue for the different classes
- [ ] create a recuperation system for simulation status with updateAtMaj functions

## mqtt version
SGE can function in mqtt betwenn differents clients. Require a broker like [mosquitto](https://mosquitto.org/download/)

## syntax code of modeler side methods
- new     create a new entity (ex. newAgentAtCoords(), newAgentSpecies), or create a new game element (ex. newGamePhase())
- get    collect entities, objects or instances
- nb     to obtain the number of entities, objects or instances
- set    to set a value        (ex. setEntities_withColumn(), setDefaultValues())
- is     to do a test (returns True or false)   (ex. isDeleted())
- delete	to delete entities from the simulation (ex. deleteAllAgents())

- do_     perform an action on an entity

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


