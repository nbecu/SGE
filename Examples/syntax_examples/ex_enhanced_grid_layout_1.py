#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test example for Enhanced Grid Layout (EGL) in SGE

This example demonstrates the new EGL functionality by creating
multiple gameSpaces and organizing them using the enhanced grid layout.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# Create QApplication
monApp = QtWidgets.QApplication([])

def main():
    """
    Main function to test Enhanced Grid Layout
    """
    print("Testing Enhanced Grid Layout (EGL) in SGE...")
    
    # Create model with enhanced_grid layout
    model = SGModel(
        width=700, 
        height=500, 
        typeOfLayout="enhanced_grid",  # New EGL option
        x=2,  # Number of columns
        name="Enhanced Grid Layout Test Model",
        windowTitle="Enhanced Grid Layout Test"
    )
    
    print(f"Model created with typeOfLayout: {model.typeOfLayout}")
    print(f"Layout type: {type(model.layoutOfModel).__name__}")
    
    # Create cells on a grid
    Cells = model.newCellsOnGrid(columns=8, rows=6, format="square", size=40)
    grid = Cells.grid
    print(f"Grid created: {grid.id}")
    
    # Create a legend
    legend = model.newLegend("Test Legend", alwaysDisplayDefaultAgentSymbology=True)
    print(f"Legend created: {legend.id}")
    
    simVar = model.newSimVariable("score", initValue=50)

    # Create a dashboard
    dashboard = model.newDashBoard(title="Test Dashboard")
    dashboard.addIndicatorOnSimVariable(simVar)
    print(f"Dashboard created: {dashboard.id}")
    
    # Create a progress gauge
    progressGauge = model.newProgressGauge(simVar, minimum=0, maximum=100, title="Progress")
    print(f"Progress gauge created: {progressGauge.id}")
    
    # Create a button
    button = model.newButton(lambda: simVar.incValue(1), "Add 1",(350,50))
    

    # Create a text box
    textBox = model.newTextBox("Welcome to EGL test!", title="Instructions")
    print(f"Text box created: {textBox.id}")
    
    # Test explicit positioning (should be respected by EGL)
    legend.moveToCoords(500, 100)
    print(f"Legend positioned explicitly at (500, 100)")
    
    # Launch the model
    print("Launching model...")
    model.launch()
    
    print("EGL test completed!")
    
    # Keep the application running
    sys.exit(monApp.exec_())

if __name__ == "__main__":
    main()
