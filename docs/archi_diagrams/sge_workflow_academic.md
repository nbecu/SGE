# SGE Model Construction Workflow - Academic Version

This diagram presents the core workflow for building SGE models in a simplified, academic format suitable for scientific publications.

## Overview

The SGE framework follows a systematic approach to model construction, progressing from basic structural elements to interactive simulation components.

```mermaid
flowchart TD
    A[Model Initialization] --> B[Grid & Cell Definition]
    B --> C[Agent Species Creation]
    C --> D[Visual Representation]
    D --> E[Player Interaction System]
    E --> F[Game Phases & Rules]
    F --> G[Model Actions]
    G --> H[User Interface Components]
    H --> I[Complete Simulation]

    %% Detailed sub-processes
    A --> A1[SGModel Setup<br/>Window Configuration]
    B --> B1[Grid Creation<br/>Cell Attributes<br/>Spatial Configuration]
    C --> C1[Agent Definition<br/>Attribute Specification<br/>Initial Placement]
    D --> D1[POV Creation<br/>Color Mapping<br/>Visual Styling]
    E --> E1[Player Creation<br/>Action Definition<br/>Interaction Rules]
    F --> F1[Phase Management<br/>Automation Rules<br/>Conditional Logic]
    G --> G1[Model Actions<br/>Automated Behaviors<br/>Entity Interactions]
    H --> H1[Legends<br/>Dashboards<br/>Control Panels]
    I --> I1[Simulation Variables<br/>End Conditions<br/>Data Recording]

    %% Styling for academic presentation
    classDef mainStep fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#000
    classDef subStep fill:#f5f5f5,stroke:#616161,stroke-width:1px,color:#000
    classDef finalStep fill:#e8f5e8,stroke:#388e3c,stroke-width:2px,color:#000

    class A,B,C,D,E,F,G,H mainStep
    class A1,B1,C1,D1,E1,F1,G1,H1 subStep
    class I,I1 finalStep
```

## Core Components and Workflow

### **Phase 1: Structural Foundation**
- **Model Initialization**: Create SGModel instance with window properties
- **Grid & Cell Definition**: Establish spatial structure with cell attributes

### **Phase 2: Agent-Based Elements**
- **Agent Species Creation**: Define agent types with behavioral attributes
- **Visual Representation**: Configure POV (Point of View) for visual mapping

### **Phase 3: Simulation Logic**
- **Player Interaction System**: Create players with game actions and control panels
- **Game Phases & Rules**: Implement play phases and automated model phases

### **Phase 4: Automated Behaviors**
- **Model Actions**: Define automated behaviors for entities and system interactions

### **Phase 5: Interface and Completion**
- **User Interface Components**: Add legends, dashboards, and control elements
- **Complete Simulation**: Add simulation variables, end conditions, and data recording

## Key Framework Characteristics

### **Progressive Development**
The SGE framework supports incremental model construction, allowing developers to build complexity gradually while maintaining system stability.

### **Separation of Concerns**
- **Structural**: Grid and cell management
- **Behavioral**: Agent definition and interaction
- **Visual**: POV and symbology systems
- **Interactive**: Player actions and game phases

### **Model-View Architecture**
Each entity maintains a clear separation between data/logic (Model) and presentation (View), enabling flexible visualization and interaction.

## Implementation Pattern

```python
# 1. Model Setup
model = SGModel(width, height, windowTitle="Simulation")

# 2. Grid Definition
cells = model.newCellsOnGrid(rows, cols, format, size)
cells.setEntities(attribute, value)

# 3. Agent Creation
agents = model.newAgentSpecies(name, shape, properties)
agents.newAgentAtCoords(cells, x, y, attributes)

# 4. Visual Configuration
cells.newPov(name, attribute, colorMapping)
agents.newPov(name, attribute, colorMapping)

# 5. Interface Components
legend = model.newLegend()
dashboard = model.newDashBoard(title)

# 6. Player System
player = model.newPlayer(name)
player.addGameAction(action)

# 7. Phase Management
playPhase = model.newPlayPhase(name, players, actions)
modelPhase = model.newModelPhase(actions, conditions)

# 8. Model Actions
modelAction = model.newModelAction(actions=[lambda: doSomething()])
cellAction = model.newModelAction_onCells(actions=[lambda cell: cell.doSomething()])

# 9. Launch
model.launch()
```

This workflow demonstrates SGE's systematic approach to agent-based simulation development, providing a clear methodology for researchers and practitioners in computational modeling.
