import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QBoxLayout, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class LineChartWidget(QWidget):
    def __init__(self, parent=None):
        super(LineChartWidget, self).__init__(parent)

        self.setWindowTitle("Linéaire")
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.plot_data()

    def plot_data(self):
        # Exemple de données pour les graphiques
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)

        # Diagramme linéaire avec 2 lignes
        self.ax.plot(x, y1, label='')
        self.ax.plot(x, y2, label='')

        self.ax.legend()
        self.canvas.draw()


class StackPlotWidget(QWidget):
    def __init__(self, parent=None):
        super(StackPlotWidget, self).__init__(parent)
        self.setWindowTitle("Stack Plot")
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.plot_data()

    def plot_data(self):
        # Exemple de données pour le stackplot
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)
        y3 = np.sin(x+180)

        # Stackplot
        self.ax.stackplot(x, y1, y2, y3, labels=['', '', ''])

        self.ax.legend()
        self.canvas.draw()


class BarChartWidget(QWidget):
    def __init__(self, parent=None):
        super(BarChartWidget, self).__init__(parent)
        self.setWindowTitle("Histogramme")
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        self.plot_data()

    def plot_data(self):
        # Exemple de données pour le diagramme en bar
        categories = ['Grass', 'Shrub', 'Forest']
        values = [23, 7, 5]

        # Diagramme en bar
        self.ax.bar(categories, values)

        self.canvas.draw()


class PieChartWidget(QWidget):
    def __init__(self, parent=None):
        super(PieChartWidget, self).__init__(parent)

        self.figure1, self.ax1 = plt.subplots()
        self.canvas1 = FigureCanvas(self.figure1)
        self.figure2, self.ax2 = plt.subplots()
        self.canvas2 = FigureCanvas(self.figure2)
        layoutM = QHBoxLayout()
        layout = QVBoxLayout()
        layout.addWidget(self.canvas1)
        layoutM.addLayout(layout)
        self.setWindowTitle("Circulaire/Histogramme")
        #self.plot_data()

        #self.figure, self.ax = plt.subplots()
        #self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas2)
        layoutM.addLayout(layout)
        self.setLayout(layoutM)
        self.plot_data()

    def plot_data(self):
        # Exemple de données pour le diagramme circulaire
        labels = ['', '', '']
        sizes = [30, 40, 30]

        # Diagramme circulaire
        self.ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        self.canvas1.draw()

        categories = ['Grass', 'Shrub', 'Forest']
        values = [23, 7, 5]

        # Diagramme en bar
        self.ax2.bar(categories, values)
        self.canvas2.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        central_widget = QWidget()
        layout = QVBoxLayout()

        line_chart_widget = LineChartWidget()
        stack_plot_widget = StackPlotWidget()
        bar_chart_widget = BarChartWidget()
        pie_chart_widget = PieChartWidget()

        layout.addWidget(line_chart_widget)
        layout.addWidget(stack_plot_widget)
        layout.addWidget(bar_chart_widget)
        layout.addWidget(pie_chart_widget)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    #main_window.show()
    pieW = PieChartWidget()
    pieW.show()
    linerW = LineChartWidget()
    linerW.show()
    stackW = StackPlotWidget()
    stackW.show()
    #barW = BarChartWidget()
    #barW.show()
    sys.exit(app.exec_())
