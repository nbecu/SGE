#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple example for SGUserSelector orientations.
Minimal example to quickly test horizontal vs vertical layouts.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mainClasses.SGSGE import *

# Create QApplication
monApp = QtWidgets.QApplication([])

# Create model
myModel = SGModel(600, 400, windowTitle="UserSelector Orientation Test")

# Create players
player1 = myModel.newPlayer("Player 1")
player2 = myModel.newPlayer("Player 2")
player3 = myModel.newPlayer("Player 3")

# Create control panels
player1.newControlPanel("Player 1 Actions")
player2.newControlPanel("Player 2 Actions")
player3.newControlPanel("Player 3 Actions")

# Create horizontal user selector
userSelector_horizontal = myModel.newUserSelector(orientation='horizontal')
if userSelector_horizontal:
    userSelector_horizontal.moveToCoords(50, 50)

# Create vertical user selector
userSelector_vertical = myModel.newUserSelector(orientation='vertical')
if userSelector_vertical:
    userSelector_vertical.moveToCoords(200, 100)

# Create phase
myModel.newPlayPhase('Test Phase', [player1, player2, player3])

print("UserSelector Orientation Test")
print("- Horizontal selector at (50, 50)")
print("- Vertical selector at (300, 50)")
print("- Close window to exit")

# Launch and run
myModel.launch()
sys.exit(monApp.exec_())
