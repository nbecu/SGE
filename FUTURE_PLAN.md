# SGE - Future Plan

This document contains the planned improvements and features for the SGE (Simulation Game Editor) project.

## Current Development Items

- [ ] Create a POV system to manage groups of symbologies.
- [ ] Correct the zoom.
- [ ] Unify font style sheets for `SGEndGameRule`.
- [ ] Refactor SGModel to follow the ordering convention of SGE for modeler methods
- [ ] Create a system to extract automatically all modeler methods, to generate a SGE methods Glossary (kind of user technical guide)
- [ ] Add a modeler style sheet config methods for `gameSpaces` who don't have yet.
- [ ] Add in SGModel menu bar the possibility to choose the displayTooltip of entities
- [ ] Main window auto resize.
- [ ] Refactor auto resize of text spacings in `gameSpaces` (using geometry).
- [ ] Integrate the enhanced grid layout of `gameSpaces`
- [ ] correct the drag and drop movement of `gameSpaces`
- [ ] New `entity`: Tile.
- [ ] Rename EntDef to a name that makes more sense.
- [ ] Rename species to a name that makes more sense.
- [ ] Unify definition of `setValue` for the different classes.
- [ ] Improve data record of gameactions (perhaps using the )
- [ ] Create automatic recording of simulation state at each round
- [ ] Create a recovery system for simulation in case it shuts down (could use `updateAtMaj` function)
- [ ] Add the possibility to export gameAction logs
- [ ] Add configurable min/max values for simulation variables
- [ ] Improve model configuration management for multiplayer games
- [ ] Add image support (JPG) in POV for legends and control panels
- [ ] Add possibility to integrate image icons in dashboards and progressGauge
- [ ] Graphs interface : improve the selection menu of graphs
- [ ] Graphs interface : allow to hide all graphs that are flat (no value change)
- [ ] Graphs interface : allow the modeler to specify the graphs that he wants to see in the menu
- [ ] Graphs interface : allow to specify a multi-graph window with graphs specify by teh modeler
- [ ] Allow to start the simulation at a specifeied time step
- [ ] add a item in SGModel menu bar to record the state of the world (state of model entities), and add the possibility to use a saved state of the world, as an initialization state for a new simulation 
- [ ] Migrate to PyQt6

## Completed Items

<!-- Add completed items here as they are finished -->

## Notes

This future plan is regularly updated as new ideas emerge and priorities change. Each item represents a potential improvement or new feature for the SGE framework.
