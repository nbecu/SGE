import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMenu, QAction, QInputDialog, QMessageBox

class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Menu Contextuel')

        self.show()

    def contextMenuEvent(self, event):
        cmenu = QMenu(self)

        newAct = cmenu.addAction('Gear')

        action = cmenu.exec_(self.mapToGlobal(event.pos()))

        if action == newAct:
            self.showGearMenu()

    def showGearMenu(self):
        items = ['Option 1', 'Option 2', 'Option 3']

        item, ok = QInputDialog.getItem(self, 'Sélectionnez une option', 'Options:', items, 0, False)

        if ok and item:
            self.showPopup(item)

    def showPopup(self, selected_option):
        QMessageBox.information(self, 'Option sélectionnée', f'Vous avez sélectionné : {selected_option}', QMessageBox.Ok)


def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
