# --- Standard library imports ---
import socket

# --- Third-party imports ---
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QDialogButtonBox,
    QMessageBox,
)


class SGDistributedBrokerSettingsDialog(QDialog):
    """
    Dialog for selecting broker or using a custom broker.
    """

    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Broker Parameters")
        self.setModal(True)
        self.resize(420, 240)

        self._buildUI()
        self._loadFromConfig()

    def _buildUI(self):
        layout = QVBoxLayout()

        info_label = QLabel("Select a broker or use a custom broker.")
        info_label.setStyleSheet("color: #666;")
        layout.addWidget(info_label)

        broker_row = QHBoxLayout()
        broker_row.addWidget(QLabel("Broker:"))
        self.broker_combo = QComboBox()
        broker_row.addWidget(self.broker_combo)
        layout.addLayout(broker_row)

        self.custom_group = QGroupBox("Custom Broker")
        custom_layout = QFormLayout()
        self.custom_host_edit = QLineEdit()
        self.custom_host_edit.setPlaceholderText("Host (e.g., localhost)")
        self.custom_port_spin = QSpinBox()
        self.custom_port_spin.setRange(1, 65535)
        custom_layout.addRow("Host", self.custom_host_edit)
        custom_layout.addRow("Port", self.custom_port_spin)
        self.custom_group.setLayout(custom_layout)
        layout.addWidget(self.custom_group)

        actions_row = QHBoxLayout()
        actions_row.addStretch()
        self.test_button = QPushButton("Test")
        self.test_button.clicked.connect(self._onTestClicked)
        actions_row.addWidget(self.test_button)
        layout.addLayout(actions_row)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self._onAccept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def _loadFromConfig(self):
        self.broker_combo.clear()
        for entry in self.config.broker_servers:
            self.broker_combo.addItem(entry.get("name"), entry)
        self.broker_combo.addItem("Custom broker", {"custom": True})
        custom_index = self.broker_combo.count() - 1
        self.broker_combo.setItemData(
            custom_index,
            "Use a custom broker address and port.",
            Qt.ToolTipRole
        )

        if self.config.use_custom_broker:
            self._selectCustom()
        else:
            self._selectByName(self.config.selected_broker_name)

        self.custom_host_edit.setText(self.config.custom_broker_host or "")
        if self.config.custom_broker_port is not None:
            self.custom_port_spin.setValue(self.config.custom_broker_port)
        else:
            self.custom_port_spin.setValue(self.config.broker_port or 1883)

        self.broker_combo.currentIndexChanged.connect(self._onBrokerSelectionChanged)
        self._onBrokerSelectionChanged()

    def _selectByName(self, name):
        for index in range(self.broker_combo.count()):
            data = self.broker_combo.itemData(index)
            if isinstance(data, dict) and data.get("name") == name:
                self.broker_combo.setCurrentIndex(index)
                return
        self.broker_combo.setCurrentIndex(0)

    def _selectCustom(self):
        for index in range(self.broker_combo.count()):
            data = self.broker_combo.itemData(index)
            if isinstance(data, dict) and data.get("custom"):
                self.broker_combo.setCurrentIndex(index)
                return

    def _onBrokerSelectionChanged(self):
        data = self.broker_combo.currentData()
        is_custom = bool(isinstance(data, dict) and data.get("custom"))
        self.custom_group.setEnabled(is_custom)
        if is_custom:
            self.custom_group.setStyleSheet("")
        else:
            self.custom_group.setStyleSheet("QGroupBox { color: #888; }")

    def _isLocalhostHost(self, host):
        return host in ["localhost", "127.0.0.1", "::1"]

    def _formatBrokerDisplay(self, name, host, port):
        if self._isLocalhostHost(host):
            return f"{name} ({host}:{port})"
        return name

    def _getSelectedBrokerTarget(self):
        data = self.broker_combo.currentData()
        if isinstance(data, dict) and data.get("custom"):
            host = self.custom_host_edit.text().strip()
            port = int(self.custom_port_spin.value())
            return "Custom broker", host, port

        name = data.get("name") if isinstance(data, dict) else "main"
        host = data.get("host") if isinstance(data, dict) else None
        port = data.get("port") if isinstance(data, dict) else None
        return name, host, port

    def _onTestClicked(self):
        name, host, port = self._getSelectedBrokerTarget()
        if not host:
            QMessageBox.warning(self, "Invalid Broker", "Please enter a valid host for the custom broker.")
            return

        display = self._formatBrokerDisplay(name, host, port)
        try:
            socket.create_connection((host, port), timeout=2).close()
            QMessageBox.information(self, "Test Successful", f"Broker test successful for {display}.")
        except Exception as e:
            QMessageBox.warning(self, "Test Failed", f"Broker test failed for {display}.\n\n{str(e)}")

    def _onAccept(self):
        name, host, port = self._getSelectedBrokerTarget()
        if not host:
            QMessageBox.warning(self, "Invalid Broker", "Please enter a valid host for the custom broker.")
            return

        if name == "Custom broker":
            self.config.use_custom_broker = True
            self.config.custom_broker_host = host
            self.config.custom_broker_port = port
            self.config.selected_broker_name = "custom"
        else:
            self.config.use_custom_broker = False
            self.config.selected_broker_name = name
            self.config.custom_broker_host = self.config.custom_broker_host or ""
            self.config.custom_broker_port = self.config.custom_broker_port

        self.config.broker_host = host
        self.config.broker_port = port

        self.accept()
