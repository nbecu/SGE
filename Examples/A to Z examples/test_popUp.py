import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QPushButton

class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 900, 700)
        self.setWindowTitle('Popup Example')

        btn_show_popup = QPushButton('Next Phase', self)
        btn_show_popup.clicked.connect(self.showPopup)
        btn_show_popup.setGeometry(50, 50, 200, 30)

    def showPopup(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle("SGE Time Manager Message")
        msg_box.setText("Attention ! A Automatic Model Phase will be trigger.")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setDefaultButton(QMessageBox.Ok)

        result = msg_box.exec_()

        if result == QMessageBox.Ok:
            print("Bouton OK a été cliqué.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    my_app = MyApp()
    my_app.show()
    sys.exit(app.exec_())
