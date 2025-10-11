# SGE Classes Diagram for Modelers

This diagram shows the main classes that modelers interact with when creating SGE games and simulations.

## Overview

Modelers primarily work with these core classes to build their games:

```mermaid
classDiagram
    class SGModel {
        +newCellsOnGrid(columns, rows, format, size)
        +newAgentSpecies(name, shape, defaultColor)
        +newPlayer(name)
        +newPlayPhase(phaseName, activePlayers, modelActions)
        +newModelPhase(actions, condition, name)
        +newSimVariable(name, initValue, color)
        +newLegend(title, alwaysDisplayDefaultAgentSymbology)
        +newDashBoard(title, borderColor, textColor)
        +newControlPanel(title, defaultActionSelected)
        +newProgressGauge(simVar, minimum, maximum, title)
        +newTimeLabel(title, backgroundColor, textColor)
        +newEndGameRule(title, numberRequired)
        +newTextBox(content, title)
        +newLabel(text, position, textStyle_specs)
        +getAdminPlayer()
        +roundNumber()
        +timeManager
    }

    class SGAgent {
        +moveTo(destinationCell)
        +moveAgent(method, target, numberOfMovement, condition)
        +getId()
        +getCoords()
        +setValue(attribute, value)
        +getValue(attribute)
        +isValue(attribute, value)
        +isNotValue(attribute, value)
        +nbAgentsHere(specie)
    }

    class SGCell {
        +getId()
        +getCoords()
        +setValue(attribute, value)
        +getValue(attribute)
        +isValue(attribute, value)
        +isNotValue(attribute, value)
        +getAgentsOnCell()
        +nbAgentsOnCell(specie)
        +getNeighbors(boundaries, neighborhood)
    }

    class SGPlayer {
        +addGameAction(gameAction)
        +addGameActions(gameActions)
        +newControlPanel(title, defaultActionSelected)
        +getName()
        +isAdmin
    }

    class SGEntityDef {
        +newAgentAtCoords(x, y)
        +newAgentOnCell(cell)
        +newCell(x, y)
        +getCell(x, y)
        +getAllCells()
        +getAllAgents()
        +setTooltip(type)
        +displayTooltip(type)
    }

    class SGTimeManager {
        +newPlayPhase(phaseName, activePlayers, modelActions)
        +newModelPhase(actions, condition, name)
        +getCurrentPhase()
        +nextPhase()
        +getPhaseByName(name)
        +getAllPhases()
        +isPhaseActive(phaseName)
        +autoForward()
        +roundNumber
    }

    class SGGameAction {
        +execute()
        +getName()
        +getNumber()
        +setNumber(number)
    }

    class SGPlayPhase {
        +addAction(action)
        +addModelAction(modelAction)
        +isActive()
        +getName()
        +getActivePlayers()
        +autoForwardWhenAllActionsUsed
    }

    class SGModelPhase {
        +addAction(action)
        +addModelAction(modelAction)
        +isActive()
        +getName()
        +getCondition()
        +auto_forward
    }

    class SGSimulationVariable {
        +setValue(value)
        +getValue()
        +incValue(increment)
        +decValue(decrement)
        +calcValue(function)
        +getName()
        +getColor()
    }

    class SGModelAction {
        +execute()
        +addAction(action)
    }

    class SGGameSpace {
        +setBorderColor(color)
        +setBorderSize(size)
        +setBackgroundColor(color)
        +setTextColor(color)
        +moveToCoords(x, y)
        +show()
        +update()
    }

    %% Relationships
    SGModel --> SGEntityDef : creates
    SGModel --> SGPlayer : creates
    SGModel --> SGSimulationVariable : creates
    SGModel --> SGModelAction : creates
    SGModel --> SGGameAction : creates
    SGModel --> SGGameSpace : creates
    SGModel --> SGTimeManager : contains
    
    SGEntityDef --> SGAgent : creates
    SGEntityDef --> SGCell : creates
    
    SGPlayer --> SGGameAction : uses
    SGPlayer --> SGPlayPhase : uses
    
    SGAgent --> SGCell : moves to
    SGCell --> SGAgent : contains
    
    SGTimeManager --> SGPlayPhase : creates
    SGTimeManager --> SGModelPhase : creates
    SGModelPhase --> SGModelAction : uses
    SGModelAction --> SGAgent : acts on
    SGModelAction --> SGCell : acts on
    
    SGGameAction --> SGAgent : acts on
    SGGameAction --> SGCell : acts on
    
    SGGameSpace --> SGSimulationVariable : displays
```

## Key Classes for Modelers

### Core Model Classes
- **SGModel**: Main entry point for creating games
- **SGEntityDef**: Factory for creating agents and cells
- **SGAgent**: Individual agents in the simulation
- **SGCell**: Grid cells containing agents and data

### Player and Interaction Classes
- **SGPlayer**: Represents a player in the game
- **SGGameAction**: Actions players can perform (acts on agents and cells)
- **SGPlayPhase**: Interactive game phases with player actions
- **SGModelPhase**: Automated game phases with model actions
- **SGTimeManager**: Manages game phases and timing

### Data and Display Classes
- **SGSimulationVariable**: Variables for scores, counters, etc.
- **SGGameSpace**: UI components (legends, dashboards, etc.)
- **SGModelAction**: Automated actions for model phases

## Usage Patterns

### 1. Basic Setup
```python
model = SGModel()
cellDef = model.newCellsOnGrid(10, 10, "square", 30)
agentDef = model.newAgentSpecies("Sheeps", "circleAgent", Qt.gray)
```

### 2. Creating Entities
```python
agent = agentDef.newAgentAtCoords(5, 5)
cell = cellDef.getCell(5, 5)
agent.moveTo(cell)
```

### 3. Player Actions
```python
player = model.newPlayer("Player 1")
action = model.newCreateAction(agentDef, {"health": "good"}, 5)
player.addGameAction(action)
```

### 4. Game Phases
```python
playPhase = model.newPlayPhase("Player Turn", ["Player 1"], [])
modelPhase = model.newModelPhase([lambda: agent.moveAgent()], lambda: model.roundNumber() > 5)

# Access timeManager directly
timeManager = model.timeManager
currentPhase = timeManager.getCurrentPhase()
roundNumber = timeManager.roundNumber
```
