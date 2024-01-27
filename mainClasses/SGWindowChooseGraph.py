import sys

import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

from mainClasses.SGLinearDiagram import SGLinearDiagram
from mainClasses.SGMultiGraph import SGMultiGraph
from mainClasses.SGMultiGraphMixte import *
from mainClasses.SGMultiGraphMultiWindow import SGMultiGraphMultiWindow

from mainClasses.SGLinearDiagramTest import SGLinearDiagramTest
from mainClasses.SGDiagramTest import SGDiagramTest



class SGWindowChooseGraph(QWidget):
    def __init__(self, model):
        super(SGWindowChooseGraph, self).__init__()
        layout = QGridLayout(self)
        self.model = model
        self.initView(layout)

    def initView(self, layout):
        path1 = "./icon/linear_diagram.png"
        path2 = "./icon/multi_graph.png"
        path3 = "./icon/multi_graph_and_windows.png"
        path4 = "./icon/multi_graph_mixte.png"
        image_paths = [path1, path2, path3, path4]
        width_img = 320
        self.create_view(layout, image_paths, width_img)

    def create_view(self, layout, image_paths, width_img):
        # Créer des étiquettes pour chaque image
        for i, path in enumerate(image_paths):
            pixmap = QPixmap(path)
            pixmap = pixmap.scaledToWidth(width_img)
            label = QLabel(self)
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)
            if i==0:
                label.mousePressEvent = self.action_one_graph
            elif i == 1:
                label.mousePressEvent = self.action_multi_graph
            elif i == 2:
                label.mousePressEvent = self.action_multi_graph_in_multi_window
            elif i == 3:
                label.mousePressEvent = self.action_mixte_in_multi_graph_in_multi_window
            else:
                print("ACTION NOT FOUND")
            row = i // 2
            col = i % 2
            layout.addWidget(label, row, col)

    def getAllHistoryData(self):
        historyData = []
        for aEntity in self.model.getAllEntities():
            h = aEntity.getHistoryDataJSON()
            historyData.append(h)
        return historyData

    def getAllHistoryData_new(self):
        return self.model.dataRecorder.dictOfData

    def action_one_graph(self, position):
        print("pos : ", position)
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

    def action_multi_graph(self, position):
        #print("multi graph position : ", position)
        #app = QApplication([])
        window = SGMultiGraph()
        window.display()
        #app.exec_()

    def action_multi_graph_in_multi_window(self, position):
        print("multi graph in multi window")
        #app = SGMultiGraphMultiWindow()
        SGMultiGraphMultiWindow()

    def action_mixte_in_multi_graph_in_multi_window(self, position):
        print("mixte in multi graph in multi window")
        #app = QApplication(sys.argv)
        #app = SGMultiGraphMixte()
        SGMultiGraphMixte()
        # barW = BarChartWidget()
        # barW.show()
        #sys.exit(app.exec_())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SGWindowChooseGraph()
    window.show()
    sys.exit(app.exec_())
