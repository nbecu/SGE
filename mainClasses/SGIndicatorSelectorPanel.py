from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget, QListWidgetItem, QCheckBox,
    QPushButton, QLabel,
)
from PyQt5.QtCore import Qt


class SGIndicatorSelectorPanel(QDockWidget):
    """
    Collapsible side panel (QDockWidget) for selecting graph indicators.

    Replaces the cascading toolbar menu with:
      - A real-time search field
      - A scrollable list of all available indicators with checkboxes
      - A "Hide flat indicators" checkbox (Feature 2)
      - An "Apply" button that triggers graph refresh

    Usage:
        panel = SGIndicatorSelectorPanel(graph_window, data_provider, on_apply_callback)
        graph_window.addDockWidget(Qt.RightDockWidgetArea, panel)
    """

    def __init__(self, parent_window, data_provider, on_apply):
        super().__init__("Indicators", parent_window)
        self.data_provider = data_provider
        self.on_apply = on_apply

        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFeatures(
            QDockWidget.DockWidgetClosable |
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetFloatable
        )

        container = QWidget()
        self.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Search field
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search indicators…")
        self._search.textChanged.connect(self._filter_list)
        layout.addWidget(self._search)

        # Hide-flat checkbox (Feature 2)
        self._hide_flat = QCheckBox("Hide flat indicators (no variation)")
        self._hide_flat.stateChanged.connect(self._filter_list)
        layout.addWidget(self._hide_flat)

        # Indicator list
        self._list = QListWidget()
        self._list.setSelectionMode(QListWidget.NoSelection)
        layout.addWidget(self._list)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_clear = QPushButton("Clear all")
        btn_clear.clicked.connect(self._clear_all)
        btn_apply = QPushButton("Apply")
        btn_apply.setDefault(True)
        btn_apply.clicked.connect(self._apply)
        btn_row.addWidget(btn_clear)
        btn_row.addWidget(btn_apply)
        layout.addLayout(btn_row)

        # All indicator keys, built once per reload
        self._all_keys = []
        self._items = {}   # key -> QListWidgetItem

        self.reload()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reload(self):
        """Rebuild the list from fresh data (call after data_provider.reload())."""
        self.data_provider.reload()
        self._all_keys = self.data_provider.available_indicator_keys()
        self._rebuild_list()

    def get_selected_keys(self):
        """Return the list of indicator keys currently checked."""
        return [
            key for key, item in self._items.items()
            if item.checkState() == Qt.Checked
        ]

    def set_selected_keys(self, keys):
        """Pre-select a set of indicator keys (used by presets)."""
        for key, item in self._items.items():
            item.setCheckState(Qt.Checked if key in keys else Qt.Unchecked)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _rebuild_list(self):
        self._list.clear()
        self._items.clear()
        for key in self._all_keys:
            from mainClasses.SGIndicatorSpec import SGIndicatorSpec
            spec = SGIndicatorSpec(key)
            item = QListWidgetItem(spec.get_display_name())
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, key)
            self._list.addItem(item)
            self._items[key] = item

    def _filter_list(self):
        text = self._search.text().lower()
        hide_flat = self._hide_flat.isChecked()
        for key, item in self._items.items():
            label = item.text().lower()
            visible = text in label
            if hide_flat and visible:
                visible = not self.data_provider.is_flat(key)
            item.setHidden(not visible)

    def _clear_all(self):
        for item in self._items.values():
            item.setCheckState(Qt.Unchecked)

    def _apply(self):
        self.on_apply(self.get_selected_keys())
