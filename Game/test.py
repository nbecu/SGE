from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create a QTextEdit
        self.textEdit = QTextEdit()

        # Create a QPushButton to update the text
        self.button = QPushButton("Update Text")
        self.button.clicked.connect(self.updateText)

        # Create a QVBoxLayout to hold the QTextEdit and QPushButton
        layout = QVBoxLayout()
        layout.addWidget(self.textEdit)
        layout.addWidget(self.button)

        # Set the QVBoxLayout as the main layout for the widget
        self.setLayout(layout)

    def updateText(self):
        # Update the QTextEdit content
        new_text = "New text with formatting <b>bold</b> and <font color='red'>red color</font>"
        self.textEdit.setHtml(new_text)

if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    widget.show()
    app.exec()