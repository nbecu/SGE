import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(500, 350, windowTitle="Neighborhood Hexagonal grid - moore (6 neighbors) - closed boundaries")

# Hexagonal grid: neighborhood='moore' => 6 neighbors
Cell = myModel.newCellsOnGrid(8, 7, "hexagonal", gap=0, size=40, neighborhood='moore', boundaries='open')

Cell.setEntities("landForm", "plain")
Cell.setRandomEntities("landForm", "mountain", 6)
Cell.setRandomEntities("landForm", "lac", 4)
Cell.newPov("base", "landForm", {"plain": Qt.green, "lac": Qt.blue, "mountain": Qt.darkGray})

# Debug: Check neighbor counts for all cells
print("=== DEBUG: Neighbor counts for all cells ===")
for cell in Cell.entities:
    neighbors = cell.getNeighborCells()
    print(f"Cell ({cell.xCoord}, {cell.yCoord}): {len(neighbors)} neighbors")
    if len(neighbors) != 6:
        print(f"  WARNING: Expected 6 neighbors, got {len(neighbors)}")
        print(f"  Neighbor coords: {[(n.xCoord, n.yCoord) for n in neighbors]}")
print("=== End Debug ===")

# Debug: Check specific cell (6, 5) that had issues
print("\n=== DEBUG: Specific check for cell (6, 5) ===")
cell_6_5 = Cell.getCell(6, 5)
if cell_6_5:
    neighbors = cell_6_5.getNeighborCells()
    print(f"Cell (6, 5): {len(neighbors)} neighbors")
    print(f"Neighbor coords: {[(n.xCoord, n.yCoord) for n in neighbors]}")
    
    # Check hexagonal pattern
    if cell_6_5.yCoord % 2 == 0:  # Even row
        expected_pattern = [(-1,-1), (-1,0), (0,-1), (0,1), (1,0), (1,1)]
    else:  # Odd row
        expected_pattern = [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]
    
    print(f"Expected pattern for row {cell_6_5.yCoord}: {expected_pattern}")
    
    # Check each expected neighbor
    for dx, dy in expected_pattern:
        expected_x = 6 + dx
        expected_y = 5 + dy
        
        # Apply toroidal wrap-around
        wrapped_x = ((expected_x - 1) % 8) + 1
        wrapped_y = ((expected_y - 1) % 7) + 1
        
        # Check if this neighbor exists
        neighbor_exists = any(n.xCoord == wrapped_x and n.yCoord == wrapped_y for n in neighbors)
        
        print(f"  ({dx}, {dy}) -> ({expected_x}, {expected_y}) -> wrapped to ({wrapped_x}, {wrapped_y}) -> {'✓' if neighbor_exists else '✗'}")
print("=== End Specific Debug ===")

Bees = myModel.newAgentSpecies("Bees", "circleAgent", defaultSize=10, defaultColor=QColor.fromRgb(165,42,42), locationInEntity="center")
Bees.newAgentsAtRandom(1, condition=lambda c: c.isValue("landForm", "plain"))

p1 = myModel.newModelPhase()
p1.addAction(lambda: Bees.moveRandomly(condition=lambda cell: cell.isValue("landForm", "plain")))

myModel.launch()
sys.exit(monApp.exec_())
