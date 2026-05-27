from PyQt6.QtWidgets import QMessageBox, QWidget, QGridLayout

from .SGBaseGraphWindow import SGBaseGraphWindow


class SGGraphWindow(QWidget):
    """Factory that opens a typed graph window after checking data availability."""

    def __init__(self, model):
        super().__init__()
        self.model = model

    def open_graph_type(self, graph_type):
        if len(self.model.dataRecorder.getStats_ofEntities()) > 2:
            graph = SGBaseGraphWindow(self.model, graph_type)
            graph.show()
            return graph
        else:
            self._show_error()
            return None

    def _show_error(self):
        dlg = QMessageBox()
        dlg.setIcon(QMessageBox.Warning)
        dlg.setWindowTitle("Unable to display the window")
        dlg.setText(
            "Please start by playing two rounds or two phases before selecting the type of graph.\n\n"
            "Example: Click the play button (>) at least twice"
        )
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.exec()
