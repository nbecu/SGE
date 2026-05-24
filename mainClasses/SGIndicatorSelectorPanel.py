from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QCheckBox,
    QPushButton, QLabel, QComboBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

QUANTI_STATS = ["mean", "sum", "min", "max", "stdev"]


class SGStatSelectorWidget(QWidget):
    """
    Inline row of mini-checkboxes for one quantitative attribute.
    Replaces the 5 separate lines (mean/sum/min/max/stdev) with a single compact row:

        age:  [✓mean] [sum] [min] [✓max] [stdev]
    """

    def __init__(self, attr_name, base_key, on_change):
        super().__init__()
        self.attr_name = attr_name
        self.base_key = base_key   # e.g. "entity-:Wolf-:age"
        self._on_change = on_change

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(4)

        lbl = QLabel(attr_name + ":")
        lbl.setFixedWidth(100)
        layout.addWidget(lbl)

        self._checkboxes = {}
        for stat in QUANTI_STATS:
            cb = QCheckBox(stat)
            cb.setStyleSheet("QCheckBox { font-size: 8pt; }")
            cb.stateChanged.connect(on_change)
            layout.addWidget(cb)
            self._checkboxes[stat] = cb
        layout.addStretch()

    def get_selected_keys(self):
        return [
            f"{self.base_key}-:{stat}"
            for stat, cb in self._checkboxes.items()
            if cb.isChecked()
        ]

    def set_selected_keys(self, active_keys):
        for stat, cb in self._checkboxes.items():
            cb.blockSignals(True)
            cb.setChecked(f"{self.base_key}-:{stat}" in active_keys)
            cb.blockSignals(False)

    def clear(self):
        for cb in self._checkboxes.values():
            cb.blockSignals(True)
            cb.setChecked(False)
            cb.blockSignals(False)


class SGIndicatorSelectorPanel(QDockWidget):
    """
    Collapsible side panel (QDockWidget) for selecting graph indicators.

    Tree structure:
        Entities  (bold)
          Wolf
            ☐ population
            age:  [✓mean][sum][min][max][stdev]   ← SGStatSelectorWidget
            ☐ some_quali_or_entDef_attr
          Sheep
            ...
        SimVars
          ☐ score
        Players
          Alice
            ☐ energy
        GameActions
          ☐ Build

    - No Apply button: selection changes update the graph immediately.
    - Group combobox: filter by category.
    - Search field: filter by entity/attribute name.
    - "Hide flat" checkbox: hide indicators whose value never changed.
    - reload() preserves the current selection.
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
        self.setMinimumWidth(340)

        container = QWidget()
        self.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Search field
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search…")
        self._search.textChanged.connect(self._filter_tree)
        layout.addWidget(self._search)

        # Group filter
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Group:"))
        self._group_combo = QComboBox()
        self._group_combo.addItems(
            ["All", "Entities", "SimVars", "Players", "GameActions"]
        )
        self._group_combo.currentTextChanged.connect(self._filter_tree)
        filter_row.addWidget(self._group_combo, 1)
        layout.addLayout(filter_row)

        # Hide-flat checkbox
        self._hide_flat = QCheckBox("Hide flat indicators (no variation)")
        self._hide_flat.stateChanged.connect(self._filter_tree)
        layout.addWidget(self._hide_flat)

        # Tree
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setColumnCount(1)
        self._tree.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self._tree)

        # Clear button
        btn_clear = QPushButton("Clear all")
        btn_clear.clicked.connect(self._clear_all)
        layout.addWidget(btn_clear)

        # Internal state
        self._simple_items = {}   # key -> QTreeWidgetItem
        self._item_to_key = {}    # QTreeWidgetItem id -> key  (reverse map for filtering)
        self._stat_widgets = {}   # base_key -> SGStatSelectorWidget
        self._stat_items = {}     # base_key -> QTreeWidgetItem
        self._all_keys = []

        self.reload()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reload(self):
        """Rebuild the tree preserving the current selection."""
        selected = self.get_selected_keys()
        self.data_provider.reload()
        self._all_keys = self.data_provider.available_indicator_keys()
        self._rebuild_tree()
        self.set_selected_keys(selected)
        self._filter_tree()

    def get_selected_keys(self):
        keys = []
        for key, item in self._simple_items.items():
            if item.checkState(0) == Qt.Checked:
                keys.append(key)
        for widget in self._stat_widgets.values():
            keys.extend(widget.get_selected_keys())
        return keys

    def set_selected_keys(self, keys):
        self._tree.blockSignals(True)
        for key, item in self._simple_items.items():
            item.setCheckState(0, Qt.Checked if key in keys else Qt.Unchecked)
        for widget in self._stat_widgets.values():
            widget.set_selected_keys(keys)
        self._tree.blockSignals(False)

    # ------------------------------------------------------------------
    # Tree construction
    # ------------------------------------------------------------------

    def _rebuild_tree(self):
        self._tree.blockSignals(True)
        self._tree.clear()
        self._simple_items.clear()
        self._item_to_key.clear()
        self._stat_widgets.clear()
        self._stat_items.clear()

        entities = {}   # name -> {population, entDef: {attr: key}, quanti: {attr: base_key}}
        sim_vars = []
        players = {}    # name -> [key, ...]
        game_actions = []

        for key in self._all_keys:
            parts = key.split("-:")
            if key.startswith("entity-:"):
                name = parts[1]
                if name not in entities:
                    entities[name] = {"population": None, "entDef": {}, "quanti": {}}
                if parts[2] == "population":
                    entities[name]["population"] = key
                elif len(parts) == 4:
                    attr = parts[2]
                    entities[name]["quanti"][attr] = f"entity-:{name}-:{attr}"
                else:
                    entities[name]["entDef"][parts[2]] = key
            elif key.startswith("simVariable-:"):
                sim_vars.append(key)
            elif key.startswith("player-:"):
                pname = parts[1]
                players.setdefault(pname, []).append(key)
            elif key.startswith("gameActions-:"):
                game_actions.append(key)

        if entities:
            cat = self._make_category("Entities")
            for ename in sorted(entities.keys()):
                ent_item = QTreeWidgetItem(cat, [ename])
                ent_item.setExpanded(True)
                e = entities[ename]
                if e["population"]:
                    self._add_simple(ent_item, "population", e["population"])
                for attr, key in sorted(e["entDef"].items()):
                    self._add_simple(ent_item, attr, key)
                for attr, base_key in sorted(e["quanti"].items()):
                    self._add_stat(ent_item, attr, base_key)

        if sim_vars:
            cat = self._make_category("SimVars")
            for key in sorted(sim_vars):
                self._add_simple(cat, key.split("-:")[1], key)

        if players:
            cat = self._make_category("Players")
            for pname in sorted(players.keys()):
                pl_item = QTreeWidgetItem(cat, [pname])
                pl_item.setExpanded(True)
                for key in sorted(players[pname]):
                    self._add_simple(pl_item, key.split("-:")[-1], key)

        if game_actions:
            cat = self._make_category("GameActions")
            for key in sorted(game_actions):
                self._add_simple(cat, key.split("-:")[-1], key)

        self._tree.blockSignals(False)

    def _make_category(self, label):
        item = QTreeWidgetItem(self._tree, [label])
        item.setExpanded(True)
        f = item.font(0)
        f.setBold(True)
        item.setFont(0, f)
        return item

    def _add_simple(self, parent, label, key):
        item = QTreeWidgetItem(parent, [label])
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(0, Qt.Unchecked)
        self._simple_items[key] = item
        self._item_to_key[id(item)] = key
        return item

    def _add_stat(self, parent, attr_name, base_key):
        item = QTreeWidgetItem(parent)
        widget = SGStatSelectorWidget(attr_name, base_key, self._trigger_update)
        self._tree.setItemWidget(item, 0, widget)
        self._stat_widgets[base_key] = widget
        self._stat_items[base_key] = item
        return item

    # ------------------------------------------------------------------
    # Update trigger (auto-apply — no Apply button needed)
    # ------------------------------------------------------------------

    def _on_item_changed(self, item, _column):
        self.on_apply(self.get_selected_keys())

    def _trigger_update(self):
        self.on_apply(self.get_selected_keys())

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def _filter_tree(self):
        text = self._search.text().lower()
        hide_flat = self._hide_flat.isChecked()
        group = self._group_combo.currentText()

        root = self._tree.invisibleRootItem()
        for ci in range(root.childCount()):
            cat = root.child(ci)
            cat_name = cat.text(0)

            if group != "All" and cat_name != group:
                cat.setHidden(True)
                continue

            cat_visible = False
            for ei in range(cat.childCount()):
                ent = cat.child(ei)
                ent_visible = self._filter_subtree(ent, text, hide_flat)
                ent.setHidden(not ent_visible)
                if ent_visible:
                    cat_visible = True

            cat.setHidden(not cat_visible)

    def _filter_subtree(self, parent_item, text, hide_flat):
        """
        Filter children of parent_item.
        Returns True if at least one child is visible (or parent itself is a leaf).
        """
        if parent_item.childCount() == 0:
            # Leaf item (SimVar, GameAction, or player attr)
            label = parent_item.text(0).lower()
            visible = not text or text in label
            if visible and hide_flat:
                key = self._item_to_key.get(id(parent_item))
                if key:
                    visible = not self.data_provider.is_flat(key)
            return visible

        has_visible = False
        ent_label = parent_item.text(0).lower()
        for ai in range(parent_item.childCount()):
            attr_item = parent_item.child(ai)
            widget = self._tree.itemWidget(attr_item, 0)

            if widget:
                attr_label = widget.attr_name.lower()
                key_for_flat = f"{widget.base_key}-:mean"
            else:
                attr_label = attr_item.text(0).lower()
                key_for_flat = self._item_to_key.get(id(attr_item))

            combined = ent_label + " " + attr_label
            visible = not text or text in combined

            if visible and hide_flat and key_for_flat:
                visible = not self.data_provider.is_flat(key_for_flat)

            attr_item.setHidden(not visible)
            if visible:
                has_visible = True

        return has_visible

    # ------------------------------------------------------------------
    # Clear all
    # ------------------------------------------------------------------

    def _clear_all(self):
        self._tree.blockSignals(True)
        for item in self._simple_items.values():
            item.setCheckState(0, Qt.Unchecked)
        self._tree.blockSignals(False)
        for widget in self._stat_widgets.values():
            widget.clear()
        self._trigger_update()
