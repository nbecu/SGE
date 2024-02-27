from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
from PyQt5.QtWidgets import QMenu, QAction

from mainClasses.SGGameSpace import SGGameSpace


# Class who is responsible of the Legend creation
class SGTextBox(SGGameSpace):
    def __init__(self, parent, textToWrite, title, sizeX=None, sizeY=None, borderColor=Qt.black, backgroundColor=Qt.lightGray):
        super().__init__(parent, 0, 60, 0, 0, true, backgroundColor)
        self.title = title
        self.id = title
        self.model = parent
        self.borderColor = borderColor
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.y1 = 0
        self.labels = 0
        self.moveable = True
        self.haveToBeClose = False
        self.isDisplay = True
        self.history = []
        self.textToWrite = textToWrite
        self.new_text = None
        self.theLayout = None
        self.initUI()

    def initUI(self):
        # Create a title
        self.labelTitle = QtWidgets.QLabel(self.title)
        font = QFont()
        font.setPixelSize(14)
        font.setBold(True)
        self.labelTitle.setFont(font)

        # Create a QTextEdit
        self.textEdit = QtWidgets.QTextEdit()
        self.textEdit.setPlainText(self.textToWrite)
        self.textEdit.setReadOnly(True)
        self.textEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textEdit.setStyleSheet(
            "border: none;background-color: lightgray;")

        # Create a QVBoxLayout to hold the QTextEdit and QPushButton
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.labelTitle)
        layout.addWidget(self.textEdit)

        # Set the QVBoxLayout as the main layout for the widget
        self.setLayout(layout)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)
        self.history.append(self.textEdit.toPlainText())

    # Function to have the global size of a gameSpace

    def getSizeXGlobal(self):
        return 160

    def getSizeYGlobal(self):
        return 150

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setBrush(QBrush(self.backgroudColor, Qt.SolidPattern))
        painter.setPen(QPen(self.borderColor, 1))
        # Draw the corner of the Legend
        if self.sizeX == None or self.sizeY == None:
            self.setMinimumSize(self.getSizeXGlobal()+3,
                                self.getSizeYGlobal()+3)
            painter.drawRect(0, 0, self.getSizeXGlobal(),
                             self.getSizeYGlobal())

        else:
            painter.drawRect(0, 0, self.sizeX, self.sizeY)

        painter.end()

    def show_menu(self, point):
        menu = QMenu(self)

        option1 = QAction("Inspect", self)
        option1.triggered.connect(lambda: print(
            "One day this will inspected something"))
        menu.addAction(option1)

        option2 = QAction("Close", self)
        option2.triggered.connect(self.close)
        menu.addAction(option2)

        if self.rect().contains(point):
            menu.exec_(self.mapToGlobal(point))

    def addText(self, text, toTheLine=False):
        """
        Add text in a text box.

        args:
            - text (str) : displayed text
            - toTheLine (bool) : if true, skip a line before adding
        """
        self.textForHistory = text
        if toTheLine == True:
            self.new_text = "\n\n"+text
        else:
            self.new_text = text
        self.updateText()

    def updateText(self):
        # Update the QTextEdit content
        newText = self.textEdit.toPlainText() + self.new_text
        self.textEdit.setPlainText(newText)
        self.history.append(self.textForHistory)

    def setNewText(self, text):
        """
        Replace the text by a new text.

        args :
            - text (str) : new text
        """
        self.new_text = text
        self.textEdit.setPlainText(text)

    def setTitle(self, title):
        """
        Replace the title by a new title.

        args:
            -title (str) : new title
        """
        self.title = title

    def setSize(self, x, y):
        self.sizeX = x
        self.sizeY = y

    def setTextFormat(self, fontName='Verdana', size=12):
        """
        Customize the font and the size of the text

        args :
            - fontName (str) : desired font
            - size (int) : desired size of the text
        """
        font = QFont(fontName, size)
        self.textEdit.setFont(font)

    def setTitleColor(self, color='red'):
        """
        Set the color

        args:
            - color (str) : desired color
        """
        self.labelTitle.setStyleSheet("color: "+color+';')

    def setTitleSize(self, size="20px"):
        """Set the size
        
        args:
            - size (int) : desired size
        """
        self.labelTitle.setStyleSheet("color: "+size+';')

    def deleteTitle(self):
        del self.labelTitle

    def deleteText(self):
        del self.textEdit
