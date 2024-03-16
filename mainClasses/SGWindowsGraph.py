import sys

import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

#from mainClasses.SGDiagram import SGDiagram
from mainClasses.SGDiagramCircular import SGDiagramCircular
from mainClasses.SGDiagramHistogram import SGDiagramHistogram
from mainClasses.SGDiagramLinear import SGDiagramLinear
from mainClasses.SGDiagramStackPlot import SGDiagramStackPlot
from mainClasses.SGMultiGraphMultiWindow import SGMultiGraphMultiWindow



class SGWindowsGraph(QWidget):
    def __init__(self, model):
        super(SGWindowsGraph, self).__init__()
        layout = QGridLayout(self)
        self.model = model


    # def getAllHistoryData(self):
    #     historyData = []
    #     for aEntity in self.model.getAllEntities():
    #         h = aEntity.getHistoryDataJSON()
    #         historyData.append(h)
    #     return historyData

    def getAllHistoryData_new(self):
        return self.model.dataRecorder.dictOfData

    def action_one_graph(self):
        # data = self.getAllHistoryData()
        sgDiagramLinear = SGDiagramLinear(self.model)
        sgDiagramLinear.show()
        return sgDiagramLinear
    
    def action_one_graph_test(self):
        # Exemple d'utilisation
        # data = self.getAllHistoryData()
        data  = self.getAllHistoryData_new()

        # data['Cell'][5]
        # data['Consumer'][5]
        #-->      Explications sur data. Le premier niveau de  clé est le nom de l'entité, le deuxième est l'id

        #data['Consumer'][5]['energy']
        #la troisième niveau de clés correspond à l'attribut
        #Et la valeur est une liste qui contient l'historique des valeurs depuis le step 0 (initialisation), jusqu'au "dernier step -1"
            #  le dernier step (le step en cours) n'est pas dispo dans l'historique des data car ce step n'est pas encore terminé (il sera terminé que lorsqu'on passera au step suivant)
            # un "step" correspond un clique sur bouton play.
                 # Donc lorsque l'exemple comporte 3 phases par Round et que l'on a cliqué 8 fois, ca fait
                      # première valeur -> valeur à l'initialisation
                      # deuxième valeur -> Round 1, phase 1
                      # 3ème valeur -> Round 1, phase 2
                      # 4ème  valeur -> Round 1, phase 3
                      # 5ème  valeur -> Round 2, phase 1
                      # 6ème valeur -> Round 2, phase 2
                      # 7ème valeur -> Round 2, phase 3
                      # 8ème valeur -> Round 3, phase 1
                 # Si un aute exemple comporte 1 seul phase par Round  et que l'on a cliqué 8 fois, ca fait
                      # première valeur -> valeur à l'initialisation
                      # deuxième valeur -> Round 1, phase 1
                      # 3ème valeur -> Round 2, phase 1
                      # 4ème  valeur -> Round 3, phase 1
                      # 5ème  valeur -> Round 4, phase 1
                      # 6ème valeur -> Round 5, phase 1
                      # 7ème valeur -> Round 6, phase 1
                      # 8ème valeur -> Round 7, phase 1
        phases = set(entry['phase'] for entry in data)
        rounds = set(entry['round'] for entry in data)

        cell_data = [ sum(1 for entry in data if entry['round'] == r and entry['phase'] == p and entry['entityDef'] == 'Cell')
                     for r in rounds for p in phases]
        agent_data = [ sum(1 for entry in data if entry['round'] == r and entry['phase'] == p and entry['entityDef'] == 'Agent')
            for r in rounds for p in phases]
        xValue = [r * len(phases) + p for r in rounds for p in phases]

        sgDiagramTest = SGDiagramTest(xValue=xValue, cell_data=cell_data, agent_data=agent_data)
        sgDiagramTest.show()

    def action_circular_diagram(self):
        #data = self.getAllHistoryData()
        sgDiagramCircular = SGDiagramCircular(self.model)
        sgDiagramCircular.show()
        return sgDiagramCircular

    def action_stackplot_diagram(self):
        sgDiagramStackPlot = SGDiagramStackPlot(self.model)
        sgDiagramStackPlot.show()
        return sgDiagramStackPlot

    def action_histogram_diagram(self):
        sgDiagramHistogram = SGDiagramHistogram(self.model)
        sgDiagramHistogram.show()
        return sgDiagramHistogram
