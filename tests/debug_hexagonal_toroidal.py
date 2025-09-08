#!/usr/bin/env python3
"""
Debug test for hexagonal toroidal neighborhood issues
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mainClasses.SGSGE import *

def debug_hexagonal_toroidal():
    """
    Debug specific cells that have wrong neighbor counts
    """
    print("=== Debug Hexagonal Toroidal Neighborhood ===")
    
    # Create Qt application
    monApp = QtWidgets.QApplication([])
    
    # Create model
    model = SGModel(500, 350, windowTitle="Debug Hexagonal Toroidal")
    
    # Create cell definition and grid in one step (like in examples)
    cellDef = model.newCellsOnGrid(8, 7, "hexagonal", gap=0, size=40, neighborhood='moore', boundaries='open')
    
    print(f"Grid created: 8 rows x 7 columns")
    print(f"Grid type: hexagonal")
    print(f"Neighborhood: moore")
    print(f"Boundaries: open")
    
    # Find cells with wrong neighbor counts
    print("\n=== Finding Cells with Wrong Neighbor Counts ===")
    
    cells_with_wrong_count = []
    
    for cell in cellDef.entities:
        neighbors = cell.getNeighborCells()
        neighbor_count = len(neighbors)
        
        if neighbor_count != 6:
            cells_with_wrong_count.append((cell.xCoord, cell.yCoord, neighbor_count, neighbors))
    
    if cells_with_wrong_count:
        print(f"Found {len(cells_with_wrong_count)} cells with wrong neighbor counts:")
        for x, y, count, neighbors in cells_with_wrong_count:
            print(f"\nCell ({x}, {y}): {count} neighbors")
            print(f"  Neighbor coords: {[(n.xCoord, n.yCoord) for n in neighbors]}")
            
            # Debug: Check what the hexagonal pattern should be
            if y % 2 == 0:  # Even row
                expected_pattern = [(-1,-1), (-1,0), (0,-1), (0,1), (1,0), (1,1)]
            else:  # Odd row
                expected_pattern = [(-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0)]
            
            print(f"  Expected pattern for row {y}: {expected_pattern}")
            
            # Check each expected neighbor
            print(f"  Checking expected neighbors:")
            for dx, dy in expected_pattern:
                expected_x = x + dx
                expected_y = y + dy
                
                # Apply toroidal wrap-around
                wrapped_x = ((expected_x - 1) % 8) + 1
                wrapped_y = ((expected_y - 1) % 7) + 1
                
                # Check if this neighbor exists
                neighbor_exists = any(n.xCoord == wrapped_x and n.yCoord == wrapped_y for n in neighbors)
                
                print(f"    ({dx}, {dy}) -> ({expected_x}, {expected_y}) -> wrapped to ({wrapped_x}, {wrapped_y}) -> {'✓' if neighbor_exists else '✗'}")
    else:
        print("✓ All cells have correct neighbor counts")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    debug_hexagonal_toroidal()
