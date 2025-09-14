#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test example for EGL pID reorganization
This example creates gameSpaces with pID gaps to test the reorganization system
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# Create QApplication
monApp = QtWidgets.QApplication([])

def main():
    """
    Test EGL pID reorganization with gaps
    """
    print("Testing EGL pID reorganization...")
    
    # Create model with enhanced_grid layout
    model = SGModel(
        width=1200, 
        height=800, 
        typeOfLayout="enhanced_grid",
        x=2,  # Number of columns
        name="EGL Reorganization Test",
        windowTitle="EGL pID Reorganization Test"
    )
    
    # Create gameSpaces
    grid = model.newCellsOnGrid(columns=6, rows=4, format="square", size=30).grid
    dashboard = model.newDashBoard(title="Dashboard")
    progressGauge = model.newProgressGauge(model.newSimVariable("test", 50), title="Progress")
    textBox = model.newTextBox("Test text", title="Instructions")
    
    print("Before reorganization:")
    for gs in model.gameSpaces.values():
        if not gs.isPositionDefineByModeler():
            print(f"  {gs.id}: pID = {gs.pID}")
    
    # Launch the model (this will trigger reorganization)
    print("Launching model...")
    model.launch()
    
    print("After reorganization:")
    for gs in model.gameSpaces.values():
        if not gs.isPositionDefineByModeler():
            print(f"  {gs.id}: pID = {gs.pID}")
    
    print("EGL reorganization test completed!")
    
    # Keep the application running
    sys.exit(monApp.exec_())

if __name__ == "__main__":
    main()
