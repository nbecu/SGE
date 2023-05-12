from PyQt5 import QtWidgets 
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from PyQt5.QtWidgets import QMenu, QAction

from SGGameSpace import SGGameSpace


#Class who is responsible of the Legend creation 
class SGTextBox(SGGameSpace):
    def __init__(self,parent,textToWrite,title,sizeX=None,sizeY=None,borderColor=Qt.black,backgroundColor=Qt.lightGray):
        super().__init__(parent,0,60,0,0,true,backgroundColor)
        self.title=title
        self.id=title
        self.model=parent
        self.borderColor=borderColor
        self.sizeX=sizeX
        self.sizeY=sizeY
        self.y=0
        self.labels=0
        self.moveable=True
        self.haveToBeClose=False
        self.isDisplay=True
        self.history=[]
        self.textToWrite=textToWrite
        self.new_text=None
        self.theLayout=None
        self.initUI()

    def initUI(self):
        self.labelTitle = QtWidgets.QLabel(self.title)
        #self.labelTitle.setText(self.title)

        self.text = QtWidgets.QLabel(self.textToWrite)
        #self.text.setText(self.textToWrite)

        self.labels=[self.title,self.textToWrite]
        

        
        self.labelTitle.setFixedHeight(self.labelTitle.fontMetrics().boundingRect(self.labelTitle.text()).height())
        self.labelTitle.setFixedWidth(self.labelTitle.fontMetrics().boundingRect(self.labelTitle.text()).width())
        self.text.setFixedHeight(self.text.fontMetrics().boundingRect(self.text.text()).height())
        self.text.setFixedWidth(self.text.fontMetrics().boundingRect(self.text.text()).width())

        #if self.theLayout is None:
        # Créer un layout vertical
        layout = QtWidgets.QVBoxLayout()
        self.theLayout = layout

        # Ajouter les widgets au layout avec un espace de 10 pixels entre eux
        layout.addWidget(self.labelTitle)
        layout.addSpacing(10)
        layout.addWidget(self.text)

        # Définir le layout pour le widget
        self.setLayout(layout)
        #self.move(0,0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateLabel)
        self.timer.start(1000)
        self.show()

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)
        self.history.append(self.text.text())


    #Function to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        return 300+len(self.getLongest())*5
    
    def getLongest(self):
        longest_word = ''
        for word in self.labels:
            if len(word) > len(longest_word):
                longest_word = word
        return longest_word
    
    def getSizeYGlobal(self):
        somme=150
        for word in self.labels :
            somme= somme+ 2*len(word)
        return somme
    
    def paintEvent(self,event):
        painter = QPainter() 
        painter.begin(self)
        painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
        painter.setPen(QPen(self.borderColor,1))
        #Draw the corner of the Legend
        if self.sizeX == None or self.sizeY ==None:
            self.setMinimumSize(self.getSizeXGlobal()+3, self.getSizeYGlobal()+3)
            painter.drawRect(0,0,self.getSizeXGlobal(), self.getSizeYGlobal())

        else:
            painter.drawRect(0,0,self.sizeX,self.sizeY)     


        painter.end()

    def mouseMoveEvent(self, e):

            if self.moveable==False:
                return
            if e.buttons() != Qt.LeftButton:
                return
            
            mimeData = QMimeData()
            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(e.pos() - self.pos())
            drag.exec_(Qt.MoveAction)


    def show_menu(self, point):
        menu = QMenu(self)

        option1 = QAction("Inspect", self)
        option1.triggered.connect(lambda: print("One day this will inspected something"))
        menu.addAction(option1)

        option2 = QAction("Close", self)
        option2.triggered.connect(self.close)
        menu.addAction(option2)

        if self.rect().contains(point):
            menu.exec_(self.mapToGlobal(point))

    def addText(self, text, toTheLine=False):
        if toTheLine == True:
            current_text = self.text.text()
            self.new_text = current_text + '\n' + text
            #self.textToWrite = new_text
            #self.text.setText(new_text)
        else:
            current_text = self.text.text()
            self.new_text = current_text + ' ' + text
            #self.textToWrite = new_text
            #self.text.setText(new_text)

    def updateLabel(self):
        test="J'espère que vous allez bien!!!"
        if self.new_text is not None:
            self.text.setText(test)
            self.textToWrite=self.new_text
        else:
            self.text(self.textToWrite)
    
    def setNewText(self,text):
        self.textToWrite=text

    def setTitle(self,title):
        self.title=title

    def setSize(self,x,y):
        self.sizeX=x
        self.sizeY=y
    
    def setTextColor(self,color='red'):
        self.text.setStyleSheet("color: "+color+';')

    def setTextSize(self,size="20px"):
        self.text.setStyleSheet("color: "+size+';')

    def setTitleColor(self,color='red'):
        self.labelTitle.setStyleSheet("color: "+color+';')

    def setTitleSize(self,size="20px"):
        self.labelTitle.setStyleSheet("color: "+size+';')

    def deleteTitle(self):
        del self.labelTitle
    
    def deleteText(self):
        del self.text