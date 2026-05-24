from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTreeWidget, QTreeWidgetItem, QCheckBox,
    QPushButton, QLabel, QComboBox,
)
from PyQt5.QtCore import Qt

QUANTI_STATS = ["mean", "sum", "min", "max", "stdev"]


class SGStatSelectorWidget(QWidget):
    """
    Compact row of mini-checkboxes for choosing stats of one quantitative attribute.
    Displayed as a child row under the attribute checkbox — no label needed here.

        [✓mean] [sum] [min] [✓max] [stdev]
    """

    def __init__(self, base_key, on_change):
        super().__init__()
        self.base_key = base_key   # e.g. "entity-:Wolf-:age"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 2, 0)   # left indent to align under parent text
        layout.setSpacing(4)

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

    def set_default(self):
        """Select 'mean' when attribute is first checked."""
        self._checkboxes["mean"].blockSignals(True)
        self._checkboxes["mean"].setChecked(True)
        self._checkboxes["mean"].blockSignals(False)

    def has_selection(self):
        return any(cb.isChecked() for cb in self._checkboxes.values())

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
            ☐ age                         ← checking this…
              [✓mean] [sum] [min] [max] [stdev]   ← …reveals stat row (default: mean)
            ☐ some_quali_attr
        SimVars
          ☐ score
        Players  /  GameActions  …

    Behaviour:
    - Checking a quanti attribute → reveals stat row, selects mean by default.
    - Unchecking → hides stat row, clears stats.
    - No Apply button: graph updates immediately on every change.
    - Group combobox + search field for filtering.
    - "Hide flat" checkbox.
    - reload() preserves the current selection.
    """

    def __init__(self, parent_window, data_provider, on_apply, single_select=False):
        super().__init__("Indicators", parent_window)
        self.data_provider = data_provider
        self.on_apply = on_apply
        self._single_select = single_select

        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFeatures(
            QDockWidget.DockWidgetClosable |
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetFloatable
        )
        self.setMinimumWidth(300)

        container = QWidget()
        self.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Search
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search…")
        self._search.textChanged.connect(self._filter_tree)
        layout.addWidget(self._search)

        # Group filter (populated dynamically in reload)
        row = QHBoxLayout()
        row.addWidget(QLabel("Group:"))
        self._group_combo = QComboBox()
        self._group_combo.currentTextChanged.connect(self._filter_tree)
        row.addWidget(self._group_combo, 1)
        layout.addLayout(row)

        # Hide flat
        self._hide_flat = QCheckBox("Hide flat indicators (no variation)")
        self._hide_flat.stateChanged.connect(self._filter_tree)
        layout.addWidget(self._hide_flat)

        # Tree
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setColumnCount(1)
        self._tree.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self._tree)

        # Clear
        btn_clear = QPushButton("Clear all")
        btn_clear.clicked.connect(self._clear_all)
        layout.addWidget(btn_clear)

        # Internal maps
        self._simple_items = {}          # key -> QTreeWidgetItem  (simple checkbox)
        self._item_to_key = {}           # id(item) -> key
        self._attr_items = {}            # base_key -> QTreeWidgetItem  (quanti attr checkbox)
        self._attr_item_to_base_key = {} # id(attr_item) -> base_key
        self._stat_widgets = {}          # base_key -> SGStatSelectorWidget
        self._stat_items = {}            # base_key -> QTreeWidgetItem  (hidden child row)
        self._entity_item_category = {}  # id(entity_item) -> 'Cell'|'Agent'|'Tile'
        self._all_keys = []

        self.reload()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def reload(self):
        """Rebuild tree preserving current selection."""
        selected = self.get_selected_keys()
        self.data_provider.reload()
        self._all_keys = self.data_provider.available_indicator_keys()
        self._entity_categories = {
            e["name"]: e["category"]
            for e in self.data_provider.data_entities
            if "category" in e and "name" in e and not isinstance(e.get("name"), dict)
        }
        self._rebuild_tree()
        self._refresh_groups_combo()
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
        # Simple items
        for key, item in self._simple_items.items():
            item.setCheckState(0, Qt.Checked if key in keys else Qt.Unchecked)
        # Quanti attribute items
        for base_key, widget in self._stat_widgets.items():
            widget.set_selected_keys(keys)
            has_sel = widget.has_selection()
            attr_item = self._attr_items[base_key]
            stat_item = self._stat_items[base_key]
            attr_item.setCheckState(0, Qt.Checked if has_sel else Qt.Unchecked)
            stat_item.setHidden(not has_sel)
            attr_item.setExpanded(has_sel)
        self._tree.blockSignals(False)

    # ------------------------------------------------------------------
    # Group combobox
    # ------------------------------------------------------------------

    def _refresh_groups_combo(self):
        """Repopulate the group combobox based on data actually present."""
        current = self._group_combo.currentText()
        self._group_combo.blockSignals(True)
        self._group_combo.clear()
        self._group_combo.addItems(self.data_provider.available_groups())
        # Restore previous selection if it still exists, else fall back to "All"
        idx = self._group_combo.findText(current)
        self._group_combo.setCurrentIndex(max(idx, 0))
        self._group_combo.blockSignals(False)

    # ------------------------------------------------------------------
    # Tree construction
    # ------------------------------------------------------------------

    def _rebuild_tree(self):
        self._tree.blockSignals(True)
        self._tree.clear()
        self._simple_items.clear()
        self._item_to_key.clear()
        self._attr_items.clear()
        self._attr_item_to_base_key.clear()
        self._stat_widgets.clear()
        self._stat_items.clear()
        self._entity_item_category.clear()

        entities = {}
        sim_vars = []
        players = {}
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
                entity_cat = self._entity_categories.get(ename, "")
                self._entity_item_category[id(ent_item)] = entity_cat
                e = entities[ename]
                if e["population"]:
                    self._add_simple(ent_item, "population", e["population"])
                for attr, key in sorted(e["entDef"].items()):
                    self._add_simple(ent_item, attr, key)
                for attr, base_key in sorted(e["quanti"].items()):
                    self._add_quanti(ent_item, attr, base_key)

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

    def _add_quanti(self, parent, attr_name, base_key):
        # Row 1 — attribute checkbox (full name, no truncation issue)
        attr_item = QTreeWidgetItem(parent, [attr_name])
        attr_item.setFlags(attr_item.flags() | Qt.ItemIsUserCheckable)
        attr_item.setCheckState(0, Qt.Unchecked)
        self._attr_items[base_key] = attr_item
        self._attr_item_to_base_key[id(attr_item)] = base_key

        # Row 2 — stat selector (child, hidden until attribute is checked)
        stat_item = QTreeWidgetItem(attr_item)
        stat_item.setFlags(stat_item.flags() & ~Qt.ItemIsSelectable)
        widget = SGStatSelectorWidget(base_key, self._trigger_update)
        self._tree.setItemWidget(stat_item, 0, widget)
        stat_item.setHidden(True)
        attr_item.setExpanded(False)

        self._stat_widgets[base_key] = widget
        self._stat_items[base_key] = stat_item

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def _on_item_changed(self, item, _column):
        item_id = id(item)

        if item_id in self._attr_item_to_base_key:
            # Quantitative attribute checkbox toggled
            base_key = self._attr_item_to_base_key[item_id]
            widget = self._stat_widgets[base_key]
            stat_item = self._stat_items[base_key]

            if item.checkState(0) == Qt.Checked:
                if self._single_select:
                    self._uncheck_all_except(item)
                stat_item.setHidden(False)
                item.setExpanded(True)
                if not widget.has_selection():
                    widget.set_default()   # auto-select mean
            else:
                stat_item.setHidden(True)
                item.setExpanded(False)
                widget.clear()

            self._trigger_update()

        elif item_id in self._item_to_key:
            # Simple indicator checkbox toggled
            if self._single_select and item.checkState(0) == Qt.Checked:
                self._uncheck_all_except(item)
            self._trigger_update()

    def _uncheck_all_except(self, keep_item):
        """Uncheck every indicator except keep_item (for single_select mode)."""
        self._tree.blockSignals(True)
        for item in self._simple_items.values():
            if item is not keep_item:
                item.setCheckState(0, Qt.Unchecked)
        for base_key, attr_item in self._attr_items.items():
            if attr_item is not keep_item:
                attr_item.setCheckState(0, Qt.Unchecked)
                self._stat_items[base_key].setHidden(True)
                attr_item.setExpanded(False)
                self._stat_widgets[base_key].clear()
        self._tree.blockSignals(False)

    def _trigger_update(self):
        self.on_apply(self.get_selected_keys())

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def _filter_tree(self):
        text = self._search.text().lower()
        hide_flat = self._hide_flat.isChecked()
        group = self._group_combo.currentText()

        # Map group label → which tree-category labels and entity categories to show
        # "Cells" means: show Entities category but only Cell-type entity items
        entity_cat_filter = None   # None = show all entity categories
        if group in ("Cells", "Agents", "Tiles"):
            wanted_cat = group[:-1]   # "Cells" -> "Cell"
            entity_cat_filter = wanted_cat

        root = self._tree.invisibleRootItem()
        for ci in range(root.childCount()):
            cat = root.child(ci)
            cat_label = cat.text(0)

            # Determine whether this tree category node should be visible at all
            if group == "All":
                cat_node_visible = True
            elif group == "Entities":
                cat_node_visible = (cat_label == "Entities")
            elif entity_cat_filter is not None:
                # Cells / Agents / Tiles → only the Entities category node
                cat_node_visible = (cat_label == "Entities")
            else:
                # SimVars / Players / GameActions
                cat_node_visible = (cat_label == group)

            if not cat_node_visible:
                cat.setHidden(True)
                continue

            cat_visible = False
            for ei in range(cat.childCount()):
                ent = cat.child(ei)

                # For entity sub-items, apply optional category filter
                if entity_cat_filter is not None and cat_label == "Entities":
                    item_cat = self._entity_item_category.get(id(ent), "")
                    if item_cat != entity_cat_filter:
                        ent.setHidden(True)
                        continue

                ent_visible = self._filter_entity_or_leaf(ent, text, hide_flat)
                ent.setHidden(not ent_visible)
                if ent_visible:
                    cat_visible = True
            cat.setHidden(not cat_visible)

    def _filter_entity_or_leaf(self, item, text, hide_flat):
        """
        If item has children that are attribute rows: filter those children.
        If item is itself a leaf (SimVar, GameAction): filter the item directly.
        """
        # Leaf item (SimVar name, GameAction name, or player attr)
        if id(item) in self._item_to_key and item.childCount() == 0:
            label = item.text(0).lower()
            visible = not text or text in label
            if visible and hide_flat:
                key = self._item_to_key[id(item)]
                visible = not self.data_provider.is_flat(key)
            return visible

        # Entity/player item: filter its attribute children
        parent_label = item.text(0).lower()
        has_visible = False

        for ai in range(item.childCount()):
            attr_item = item.child(ai)
            attr_label = attr_item.text(0).lower()
            combined = parent_label + " " + attr_label
            visible = not text or text in combined

            if visible and hide_flat:
                # For quanti attrs use mean key; for simple use direct key
                if id(attr_item) in self._attr_item_to_base_key:
                    base_key = self._attr_item_to_base_key[id(attr_item)]
                    key_for_flat = f"{base_key}-:mean"
                else:
                    key_for_flat = self._item_to_key.get(id(attr_item))
                if key_for_flat:
                    visible = not self.data_provider.is_flat(key_for_flat)

            # Never touch the stat_item child of attr_item here — its visibility
            # is controlled solely by the attribute checkbox state.
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
        for base_key, attr_item in self._attr_items.items():
            attr_item.setCheckState(0, Qt.Unchecked)
            self._stat_items[base_key].setHidden(True)
            attr_item.setExpanded(False)
            self._stat_widgets[base_key].clear()
        self._tree.blockSignals(False)
        self._trigger_update()
