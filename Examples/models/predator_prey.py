import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(660, 444, windowTitle="Wolf hunts closest sheep (radius 3) and kills it if its on the same location")

Cell = myModel.newCellsOnGrid(
    columns=16, rows=10, format="square", gap=0, size=40, neighborhood='moore', boundaries='closed'
)

# Terrain setup (same spirit as Example 6)
Cell.setEntities("landForm", "plain")
Cell.setRandomEntities("landForm", "mountain", 10)
Cell.setRandomEntities("landForm", "lac", 6)
Cell.newPov("base", "landForm", {"plain": Qt.green, "lac": Qt.blue, "mountain": Qt.darkGray})
Cell.newBorderPov("transparent", "landForm", {"plain": Qt.transparent, "lac": Qt.transparent, "mountain": Qt.transparent})
Cell.displayBorderPov("transparent")

# Agent species
Sheep = myModel.newAgentType("Sheep", "ellipseAgent1", defaultSize=18, locationInEntity="center", defaultColor=Qt.white)
Wolf  = myModel.newAgentType("Wolf",  "ellipseAgent2", defaultSize=20, locationInEntity="center", defaultColor=Qt.red)

# Place agents: 5 sheep on plains; 1 wolf on plain
Sheep.newAgentsAtRandom(5, condition=lambda c: c.isValue("landForm", "plain"))
Wolf.newAgentsAtRandom(1,  condition=lambda c: c.isValue("landForm", "plain"))

# Time phase
p1 = myModel.newModelPhase(auto_forward=True,message_auto_forward=False)

# Sheep wander randomly but only on plains
p1.addAction(lambda: Sheep.moveRandomly(condition=lambda c: c.isValue("landForm", "plain")))

# Wolf hunts: find the closest sheep within radius 4, then move towards it (movement allowed only on plains)
def wolf_hunt_step():
    wolf = Wolf.getEntities()[0]

    # Find closest sheep within distance 4 (returns one agent by default)
    target_sheep = wolf.getClosestAgentMatching(
        agentSpecie=Sheep,
        max_distance=3
        # You could add conditions_on_cell / conditions_on_agent if needed
    )

    if target_sheep:
        # Move towards target; restrict movement to plains if desired
        print(f"Sheep detected at distance {wolf.cell.distanceTo(target_sheep.cell)}")
        wolf.moveTowards(target_sheep.cell, condition=lambda c: c.isValue("landForm", "plain"))
        
    else:
        # Optional fallback: roam randomly if no sheep in sight
        wolf.moveRandomly(condition=lambda c: c.isValue("landForm", "plain"))

p1.addAction(wolf_hunt_step)


p2 = myModel.newModelPhase()
# Wolf eat: delete the sheep which is on the same location, if it exists
def wolf_eat_step():
    wolf = Wolf.getEntities()[0]
    if wolf.hasAgentsHere(Sheep):
        print(f"Wolf eat a sheep ")
        Sheep.deleteEntity(wolf.getAgentsHere(Sheep)[0])
    
p2.addAction(wolf_eat_step)




myModel.launch()
sys.exit(monApp.exec_())
