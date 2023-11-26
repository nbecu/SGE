import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp=QtWidgets.QApplication([])

myModel=SGModel(500,300, windowTitle="A simulation/game with agents", typeOfLayout ="grid")

Cell=myModel.newGrid(6,4,"square",gap=2,size=40)
# Cell=Cell.cellDef
Cell.setEntities("landUse","grass")
##  Pour pouvoir rassembler Agents et Cells (sous ENtity), faut que newGrid renvoie la CellCollection
#      il faudra certainement renonmmer CellCollection en CellSpec   (comme AgentSpec qui est parfois appelé AgentDict ou AgentCollec)
#       et ce serai plus propre de créer une class CellSpec et AgentSpec plutot que d'utiliser l'attribut me='collec' 
Cell.setEntities_withColumn("landUse","forest",1)
Cell.setEntities_withColumn("landUse","forest",2)
Cell.setRandomEntities("landUse","shrub",10)

Cell.newPov("ICanSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.yellow,"forest":Qt.darkGreen})
Cell.newPov("ICantSeeShrub","landUse",{"grass":Qt.green,"shrub":Qt.green,"forest":Qt.darkGreen})

# Here, a "type" of agent is called a species.
# To create a species, it needs : a name and a shape 
# You can add a dict of attributs with values (optionnal).

# Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1",{"health":{"good","bad"},"hunger":{"good","bad"}}) 
# Dans ce code commenté, juste au dessus (le dict d'attribut et value ressemble à la définitiondes valeurs possibles
# Mais en fait, on a vu que ces dict qui sont déclaré à la création d'une speciie sont en fait des dict de valeur de EntDef
# Du coup, il faut retirer ces dict de déclaration d'attribut et valeurs des variables de la méthode newAgentSpecies()
# TODO : dans tous les ex., retirer des variables de la méthode newAgentSpecies() les dict qui ressemble à la déclaration d'attribut et valeurs 
#Par contre, on peut trouver utile de définir des valeurs par default des attributs
# Du coup, j'ai ajouté une novuelle méthodes pour déclarer ces valeurs par default
Sheeps=myModel.newAgentSpecies("Sheeps","triangleAgent1")
Sheeps.setDefaultValues({"health":{"good","bad"},"hunger":{"good","bad"}})

# For each attribute, you can set up points of view with colors :
Sheeps.newPov("Sheeps -> Health","health",{'good':Qt.blue,'bad':Qt.red})
Sheeps.newPov("Sheeps -> Hunger","hunger",{'good':Qt.green,'bad':Qt.yellow})

# You can now create agents from its species and place them on a particular cell, or random by giving None values and
# give them attributes with values :
m1=Sheeps.newAgentAtCoords(Cell,3,3,{"health":"good","hunger":"bad"})
m2=Sheeps.newAgentAtCoords(Cell)

#You can also edit your agent attribute values like this :
m2.setValue('health','good')
m2.setValue('hunger','good')



Legend=myModel.newLegend(showAgentsWithNoAtt=True)
myModel.launch() 

sys.exit(monApp.exec_())
