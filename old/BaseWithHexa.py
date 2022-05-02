import sys 

from win32api import GetSystemMetrics



from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *


            
class MyMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        #Definition of the title of the window ( temporary) 
        self.setWindowTitle("A grid Test")
        #Definition the size of the window ( temporary here)
        screensize = GetSystemMetrics(0),GetSystemMetrics(1)
        self.setGeometry(int((screensize[0]/2)-800/2),int((screensize[1]/2)-400/2),1080,960)
        #self.grid=SGGrid()
        self.initUI()
        
    def initUI(self):
        self.window = QtWidgets.QWidget() 
        self.layout = QtWidgets.QGridLayout() 
        self.setCentralWidget(self.window) 
        self.window.setLayout(self.layout)
        
        self.Grid_widget = SGGrid() 
        self.layout.addWidget(self.Grid_widget) 
        
#Class who is responsible of the grid creation
class SGGrid(QtWidgets.QWidget):
    def __init__(self, rows=8, columns=8,format="hexagon",size=32,gap=3, parent=None):
        super().__init__()
        self.layout = QtWidgets.QGridLayout() 
        self.setLayout(self.layout) 
        #Definition of variables
        self.rows = rows
        self.columns = columns
        self.format=format
        self.size = size
        self.gap=gap
        
        
        #Cells
        self.cells=[]
        for i in range(self.columns):
            for j in range(self.rows):
                self.cells.append(Cell(j,i,self.format,self.size))
        #self.initUI()
        
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(Qt.gray, Qt.SolidPattern))
        #Base of the gameBoard
        startXbase=int((self.width()/2)-(self.rows*self.size+self.rows*self.gap)/2)
        startYbase=int((self.height()/2)-(self.columns*self.size+self.columns*self.gap/2)/2)
        painter.drawRect(startXbase,startYbase, self.rows*self.size+(self.rows+1)*self.gap+1,self.columns*self.size+(self.columns+1)*self.gap)
        #Drawing each cells
        
        painter.setBrush(QBrush(Qt.blue, Qt.SolidPattern))


        for cell in self.cells:
            painter.setBrush(QBrush(Qt.blue, Qt.SolidPattern))
            if(self.format=="square"):
                painter.drawRect(startXbase+self.gap*(cell.x)+self.size*(cell.x)+self.gap, startYbase+self.gap*(cell.y)+self.size*(cell.y)+self.gap, self.size,self.size)
            
            if(self.format=="hexagon") :
                partSize=int(cell.size/3)
                points = QPolygon([
                    QPoint(startXbase+cell.size*cell.x+partSize+self.gap*cell.x+self.gap,                   startYbase+self.gap*cell.y+self.gap+cell.size*cell.y),
                    QPoint(startXbase+(partSize*2)+cell.size*cell.x+self.gap*cell.x+self.gap,             startYbase+self.gap*cell.y+self.gap+cell.size*cell.y),
                    QPoint(startXbase+(partSize*3)+cell.size*cell.x+self.gap*cell.x+self.gap,             startYbase+partSize+self.gap*cell.y+self.gap+cell.size*cell.y),
                    QPoint(startXbase+(partSize*3)++cell.size*cell.x+self.gap*cell.x+self.gap,            startYbase+(partSize*2)+self.gap*cell.y+self.gap+cell.size*cell.y),
                    QPoint(startXbase+(partSize*2)+cell.size*cell.x+self.gap*cell.x+self.gap,             startYbase+(partSize*3)+self.gap*cell.y+self.gap+cell.size*cell.y),
                    QPoint(startXbase+partSize+cell.size*cell.x+self.gap*cell.x+self.gap,                 startYbase+(partSize*3)+self.gap*cell.y+self.gap+cell.size*cell.y),
                    QPoint(startXbase+cell.size*cell.x+self.gap*cell.x+self.gap,                          startYbase+(partSize*2)+self.gap*cell.y+self.gap+cell.size*cell.y),
                    QPoint(startXbase+cell.size*cell.x+self.gap*cell.x+self.gap,                          startYbase+partSize+self.gap*cell.y+self.gap+cell.size*cell.y)
                ])
                painter.drawPolygon(points)

        painter.end()
        
#Class who is responsible of the declaration a cell
class Cell(QtWidgets.QWidget):
    def __init__(self,x, y,format="square",size=32,color="blue", parent=None):
        super().__init__()
        self.layout = QtWidgets.QGridLayout() 
        self.setLayout(self.layout) 
        #Definition of variables
        self.x = x
        self.y = y
        self.format=format
        self.size = size
        
        
            
if __name__ == '__main__':
    monApp=QtWidgets.QApplication([])
    win=MyMainWindow()
    win.show() 
    sys.exit(monApp.exec_())