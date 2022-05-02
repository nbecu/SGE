from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt)
from PyQt5.QtGui import (QBrush, QColor, QPainter,QPen,QFont)
from PyQt5.QtWidgets import (QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton,QWidget, QMainWindow)
 
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        fenetre_widget = QWidget()
        self.view = QGraphicsView()
        self.view.setCacheMode(QGraphicsView.CacheBackground)
        self.pen = QPen()
        self.pen.setWidth(1)
        self.pen2 = QPen()
        self.pen2.setWidth(5)
        self.label1=QLabel("Test")
        self.label1.setFixedWidth(400)
        layouthorizontal1 = QHBoxLayout()
        layouthorizontal1.addWidget(self.view)
        layouthorizontal1.addWidget(self.label1)
        fenetre_widget.setLayout(layouthorizontal1)        
        self.setCentralWidget(fenetre_widget)
        self.view.mousePressEvent = self.on_mousePressEvent
        self.nb_droite=0
        self.scene = None
 
    def build_scene(self):
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.view.width(), self.view.height())
        self.view.setScene(self.scene)
 
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_R:
            self.scene.clear()
        super(MainWindow, self).keyPressEvent(event)
 
    def on_mousePressEvent(self, event):
        if self.scene is None:
            self.build_scene()
        pos = event.pos()
        print(pos)
        taillex=self.width()        # A mon avis tu veux dire self.view.width() ?
        tailley=self.height()       # A mon avis tu veux dire self.view.height() ?
        if self.nb_droite<2:
            if self.nb_droite==0:
                self.pos1x=pos.x()
                self.pos1y=pos.y()
                print(self.pos1x,self.pos1y)
            elif self.nb_droite==1:
                self.pos2x=pos.x()
                self.pos2y=pos.y()
                print(self.pos2x,self.pos2y)
            self.scene.addLine(pos.x(),0,pos.x(),tailley,self.pen)
            self.nb_droite = self.nb_droite+1
            if self.nb_droite==2:
                label=self.scene.addSimpleText (str(abs(self.pos1x-self.pos2x)) + " pixels", QFont('Norasi', 12))
                ligne_legende=self.scene.addLine (20,tailley-15,(abs(self.pos1x-self.pos2x)/2),tailley-15,self.pen2)
                label.setY(tailley-40)
                label.setX(20)
                print(self.pos1x-self.pos2x)
        elif self.nb_droite==2:
            self.scene.clear()
            self.nb_droite=0
 
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())