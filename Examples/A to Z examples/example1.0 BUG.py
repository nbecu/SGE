import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(600,600, windowTitle="About pov (1)", typeOfLayout='vertical')

#First thing first: define the size of the grid (x, y), the shape of cells, their size, and other parameters
aGrid=myModel.createGrid(10,10,"square",size=50)
#Then set the value of the cells for a given parameter
#In this example the parameter is landUse, and the values given are 'grass', 'forest' and 'shrub'

#The method setValueForCells() sets the value of all cells
aGrid.setValueForCells({"landUse":"grass"})
#The method setForX() sets the value of cells which x coordinate match a given value. X=1 corresponds to the first columnn on the left side of the grid 
aGrid.setForX({"landUse":"forest"},1)
aGrid.setForX({"landUse":"forest"},2)
#The method setForRandom()sets the value of a number of randomly selected cells on the grid 
aGrid.setForRandom({"landUse":"shrub"},10)
#C'est pas un bug, mais c'est le  nom de la méthode qui est à changer. Voici ce que propose chatGPT pour que ce soit plus facilement compréhensible
# def set_random_cells(attribute_name, attribute_value, num_cells):
#     """
#     Sets the value of the given attribute to a random number of cells on the grid.
    
#     Args:
#         attribute_name (str): Name of the attribute to set.
#         attribute_value (int): Value to set the attribute to.
#         num_cells (int): Number of cells to set the attribute value for.
#     """

myModel.setUpPov("povLandUse","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen},[aGrid])

myModel.launch_withoutMqtt() 

sys.exit(monApp.exec_())
