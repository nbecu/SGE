#!/usr/bin/env python3
"""
Test script for the gs_aspect system and modeler methods.
This script tests the new styling capabilities across different GameSpaces.
"""

import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Initialize QApplication before importing SGE
app = QApplication.instance()
if app is None:
    app = QApplication(sys.argv)

from mainClasses.SGSGE import *

def test_gs_aspect_system():
    """Test the gs_aspect system with various GameSpaces."""
    
    print("Testing gs_aspect system...")
    
    # Create a model
    model = SGModel(typeOfLayout="enhanced_grid", nb_columns=2)
    
    # Test 1: SGTextBox with gs_aspect
    print("1. Testing SGTextBox...")
    textBox = model.newTextBox("Hello World!", "Test TextBox", titleAlignment='center')
    textBox.setBorderColor(Qt.red)
    textBox.setTextColor(Qt.blue)
    textBox.setFontSize(14)
    textBox.setBackgroundColor(Qt.lightGray)
    
    # Test 2: SGEndGameRule with gs_aspect
    print("2. Testing SGEndGameRule...")
    endGameRule = model.newEndGameRule("Test Rules", 1, borderColor=Qt.green, backgroundColor=Qt.white)
    endGameRule.setBorderSize(2)
    endGameRule.setTextColor(Qt.darkGreen)
    endGameRule.setBackgroundColor(Qt.yellow)
    
    # Test 3: SGUserSelector with gs_aspect
    print("3. Testing SGUserSelector...")
    userSelector = model.newUserSelector(["Admin", "Player1", "Player2"])
    userSelector.setBorderColor(Qt.blue)
    userSelector.setTextColor(Qt.darkBlue)
    userSelector.setTitleText("User Selection")
    userSelector.setCheckboxStyle({'color': 'darkblue', 'font_size': 12})
    
    # Test 4: SGDashBoard with gs_aspect
    print("4. Testing SGDashBoard...")
    dashboard = model.newDashBoard("Test Dashboard", Qt.black, 1, Qt.white, Qt.black, "vertical")
    dashboard.setBorderColor(Qt.purple)
    dashboard.setTextColor(Qt.darkMagenta)
    dashboard.setTitleText("Custom Dashboard")
    
    # Test 5: SGTimeLabel with gs_aspect
    print("5. Testing SGTimeLabel...")
    timeLabel = model.newTimeLabel("Game Time", backgroundColor=Qt.cyan, textColor=Qt.darkCyan)
    timeLabel.setBorderColor(Qt.darkCyan)
    timeLabel.setTitleText("Custom Time")
    timeLabel.setLabelStyle({'color': 'darkcyan', 'font_weight': 'bold'})
    
    # Test 6: SGVoid with gs_aspect
    print("6. Testing SGVoid...")
    void = model.newVoid("Test Void", 150, 100)
    void.setBorderColor(Qt.gray)
    void.setBackgroundColor(Qt.lightGray)
    void.setSize(200, 150)
    
    # Test 7: Theme system
    print("7. Testing Theme system...")
    
    # Apply different themes to different GameSpaces
    textBox.applyTheme('modern')
    endGameRule.applyTheme('colorful')
    userSelector.applyTheme('blue')
    dashboard.applyTheme('green')
    timeLabel.applyTheme('minimal')
    void.applyTheme('gray')
    
    # Test 8: Style dictionary method
    print("8. Testing setStyle method...")
    textBox.setStyle({
        'border_color': Qt.red,
        'background_color': Qt.white,
        'text_color': Qt.black,
        'font_size': 16,
        'font_weight': 'bold',
        'border_radius': 5,
        'padding': 10
    })
    
    # Test 9: Individual style methods
    print("9. Testing individual style methods...")
    endGameRule.setBorderRadius(8)
    endGameRule.setPadding(12)
    endGameRule.setMinWidth(200)
    endGameRule.setMinHeight(100)
    
    print("All tests completed successfully!")
    
    # Show the model
    model.show()
    
    return model

def test_theme_application():
    """Test different theme application approaches."""
    
    print("\nTesting theme application approaches...")
    
    model = SGModel(typeOfLayout="enhanced_grid", nb_columns=3)
    
    # Create some GameSpaces
    textBox1 = model.newTextBox("Text 1", "Title 1")
    textBox2 = model.newTextBox("Text 2", "Title 2")
    dashboard1 = model.newDashBoard("Dashboard 1", Qt.black, 1, Qt.white, Qt.black, "vertical")
    timeLabel1 = model.newTimeLabel("Time 1")
    
    print("Created GameSpaces for theme testing...")
    
    # Test individual theme application
    print("Applying individual themes...")
    textBox1.applyTheme('modern')
    textBox2.applyTheme('colorful')
    dashboard1.applyTheme('blue')
    timeLabel1.applyTheme('minimal')
    
    print("Individual theme application completed!")
    
    model.show()
    return model

if __name__ == "__main__":
    try:
        print("Starting gs_aspect system tests...")
        
        # Test basic functionality
        model1 = test_gs_aspect_system()
        
        # Test theme application
        model2 = test_theme_application()
        
        print("\nAll tests completed successfully!")
        print("Check the displayed windows to see the results.")
        
        # Run the application
        app.exec_()
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
