import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QMessageBox, QComboBox, QWidget, QAction,
    QPushButton, QInputDialog,
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from mainClasses.SGGraphDataProvider import SGGraphDataProvider
from mainClasses.SGIndicatorSpec import SGIndicatorSpec
from mainClasses.SGIndicatorSelectorPanel import SGIndicatorSelectorPanel


class SGGraphController(NavigationToolbar):
    """
    Toolbar attached to a graph window.

    Responsibilities (after refactoring):
      - Own the SGGraphDataProvider (data access)
      - Host the SGIndicatorSelectorPanel (indicator selection UX)
      - Provide the x-axis option combobox
      - Drive the matplotlib axes (plotting)

    All data loading is delegated to SGGraphDataProvider.
    All indicator-selection UI is delegated to SGIndicatorSelectorPanel.
    """

    COLORS = ["gray", "green", "blue", "red", "black", "orange",
              "purple", "pink", "cyan", "magenta"]

    def __init__(self, canvas, parent_window, model, graph_type):
        super().__init__(canvas, parent_window)
        self.parent_window = parent_window
        self.graph_type = graph_type
        self.model = model
        self.ax = parent_window.ax
        self.specified_phase = 2

        # Data provider
        self.data_provider = SGGraphDataProvider(model, graph_type)

        # X-axis combobox (linear and stackplot only)
        self._x_axis_options = {
            "Rounds":          "per round",
            "Rounds & Phases": "per step",
            "Specified phase": "specified phase",
        }
        if graph_type in ("linear", "stackplot"):
            self._x_combobox = QComboBox(parent_window)
            self.addWidget(self._x_combobox)
        else:
            self._x_combobox = None

        # Refresh button
        btn = QPushButton("refresh", self)
        btn.clicked.connect(self.refresh_data)
        self.addWidget(btn)

        # Indicator selector panel (QDockWidget, attached after toolbar is built)
        self._selector_panel = None
        self.preset_title = None     # set by _open_graph when opened from a preset
        self.preset_x_axis = None    # set by _open_graph when preset specifies an x-axis mode

        # Selector toggle button
        btn_sel = QPushButton("Indicators ▸", self)
        btn_sel.clicked.connect(self._toggle_selector)
        self.addWidget(btn_sel)

    # ------------------------------------------------------------------
    # Called by SGBaseGraphWindow after __init__
    # ------------------------------------------------------------------

    def set_data(self):
        self.data_provider.reload()
        self._setup_x_combobox()

        # Build and attach the selector panel to the parent QMainWindow
        self._selector_panel = SGIndicatorSelectorPanel(
            self.parent_window,
            self.data_provider,
            on_apply=self._on_indicators_applied,
            single_select=(self.graph_type in ("pie", "stackplot", "hist")),
        )
        self.parent_window.addDockWidget(Qt.RightDockWidgetArea, self._selector_panel)
        self._selector_panel.hide()

        self.update_chart(reload=False)

    # ------------------------------------------------------------------
    # Indicator selection
    # ------------------------------------------------------------------

    def _toggle_selector(self):
        if self._selector_panel is None:
            return
        if self._selector_panel.isHidden():
            self._selector_panel.show()
        else:
            self._selector_panel.hide()

    def _on_indicators_applied(self, selected_keys):
        self.preset_title = None   # user changed selection manually
        self.update_chart(reload=False)

    def _get_selected_keys(self):
        if self._selector_panel is None:
            return []
        return self._selector_panel.get_selected_keys()

    # ------------------------------------------------------------------
    # Chart update
    # ------------------------------------------------------------------

    def refresh_data(self):
        self.data_provider.reload()
        if self._selector_panel:
            self._selector_panel.reload()
        self.update_chart(reload=False)

    def update_chart(self, reload=True):
        if reload:
            self.data_provider.reload()

        selected_keys = self._get_selected_keys()
        x_option = self._get_x_option()
        x_value, nb_rounds_complete = self.data_provider.compute_x_axis(
            x_option, self.specified_phase
        )
        self._x_value = x_value
        self._nb_rounds_complete = nb_rounds_complete

        if self.graph_type == "linear":
            self._plot_linear(selected_keys, x_option)
        elif self.graph_type == "hist":
            self._plot_hist(selected_keys)
        elif self.graph_type == "pie":
            self._plot_pie(selected_keys)
        elif self.graph_type == "stackplot":
            self._plot_stackplot(selected_keys, x_option)

    # ------------------------------------------------------------------
    # X-axis combobox
    # ------------------------------------------------------------------

    def _setup_x_combobox(self):
        if self._x_combobox is None:
            return
        self._x_combobox.clear()
        for label in self._x_axis_options:
            self._x_combobox.addItem(label, self._x_axis_options[label])
        self._x_combobox.currentIndexChanged.connect(self._on_x_option_changed)

    def _on_x_option_changed(self):
        self.preset_x_axis = None   # user overrides the preset x-axis mode
        if self._get_x_option() == "specified phase":
            nb = self.data_provider.nb_phases()
            dialog = QInputDialog(self.parent_window)
            dialog.setWindowTitle("Select Specified Phase")
            dialog.setLabelText(f"Sélectionnez la phase (1-{nb}):")
            dialog.setComboBoxItems([str(i) for i in range(1, nb + 1)])
            dialog.setComboBoxEditable(False)
            if dialog.exec_() == QInputDialog.Accepted:
                self.specified_phase = int(dialog.textValue())
        self.update_chart(reload=False)

    def _get_x_option(self):
        if self.preset_x_axis:
            return self.preset_x_axis
        if self._x_combobox:
            return self._x_combobox.currentData() or "per round"
        return "per round"

    def _sync_x_combobox(self, x_option):
        """Update the combobox to visually reflect x_option without triggering a chart update."""
        if self._x_combobox is None:
            return
        for i in range(self._x_combobox.count()):
            if self._x_combobox.itemData(i) == x_option:
                self._x_combobox.blockSignals(True)
                self._x_combobox.setCurrentIndex(i)
                self._x_combobox.blockSignals(False)
                break

    # ------------------------------------------------------------------
    # Plotting — linear
    # ------------------------------------------------------------------

    def _plot_linear(self, selected_keys, x_option):
        self.ax.clear()
        dp = self.data_provider
        data = dp.all_quantitative()

        for pos, key in enumerate(selected_keys):
            spec = SGIndicatorSpec(key, is_quantitative=True)
            if x_option in ("per round", "specified phase") or (
                x_option == "per step" and dp.nb_phases() == 1
            ):
                phase = self.specified_phase if x_option == "specified phase" else dp.nb_phases()
                self._plot_linear_per_round(data, pos, spec, phase)
            elif x_option == "per step":
                self._plot_linear_per_step(data, pos, spec)

        self.ax.legend()
        entities = ", ".join({
            k.split("-:")[1] for k in selected_keys if "entity" in k
        })
        self.ax.set_title(self.preset_title or self._make_auto_title(selected_keys))
        self.canvas.draw()

    def _plot_linear_per_round(self, data, pos, spec, phase_to_display):
        dp = self.data_provider
        data_y = []
        for r in range(self._nb_rounds_complete + 1):
            phase_idx = phase_to_display if r != 0 else 0
            subset = [e for e in data if e.get("round") == r and e.get("phase") == phase_idx]
            data_y.extend(spec.get_data(subset))
        if data_y:
            self._draw_line(self._x_value, data_y, spec.get_label(),
                            spec.get_line_style(), pos)

    def _plot_linear_per_step(self, data, pos, spec):
        dp = self.data_provider
        current = dp.current_round_phase()
        nb_phases = dp.nb_phases()
        data_y = []
        for r in range(self._nb_rounds_complete + 2):
            for p in range(nb_phases + 1):
                if (r, p) == current:
                    continue
                subset = [e for e in data if e.get("round") == r and e.get("phase") == p]
                data_y.extend(spec.get_data(subset))
        if data_y:
            self._draw_line(self._x_value, data_y, spec.get_label(),
                            spec.get_line_style(), pos)

    def _draw_line(self, x_value, data_y, label, linestyle, pos):
        color = self.COLORS[pos % len(self.COLORS)]
        data_y = [0 if isinstance(v, list) and not v else v for v in data_y]
        if len(x_value) == 1:
            self.ax.plot(x_value * len(data_y), data_y,
                         label=label, color=color, marker="o", linestyle="None")
        else:
            if len(x_value) > len(data_y):
                data_y.extend([0] * (len(x_value) - len(data_y)))
            self.ax.plot(x_value, data_y, label=label, linestyle=linestyle, color=color)
            self._draw_step_lines(x_value)

    # ------------------------------------------------------------------
    # Plotting — histogram
    # ------------------------------------------------------------------

    def _plot_hist(self, selected_keys):
        self.ax.clear()
        dp = self.data_provider
        data = dp.data_entities
        rounds = {e["round"] for e in data}
        max_round = max(rounds) if rounds else 0
        attrib_value = ""
        entity_names = []

        for key in selected_keys:
            if "-:" not in key:
                continue
            parts = key.split("-:")
            entity = parts[1]
            attrib_value = parts[-1]
            entity_names.append(entity)
            hist_data = {
                f"{entity}-{attrib_value}": e["quantiAttributes"][attrib_value]["histo"]
                for e in data
                if e["name"] == entity and "quantiAttributes" in e
                and attrib_value in e["quantiAttributes"]
                and "histo" in e["quantiAttributes"][attrib_value]
                and e["round"] == max_round
            }
            for h in [hist_data]:
                if not h:
                    continue
                x_intervals = list(h.values())[0][1]
                x_centers = np.average([x_intervals[1:], x_intervals[:-1]], axis=0)
                heights = list(h.values())[0][0]
                label = list(h.keys())[0]
                self.ax.hist(x_centers, weights=heights, bins=x_intervals,
                             label=label, edgecolor="black")
                self.ax.set_xticks(x_intervals)

        self.ax.legend()
        self.ax.set_title(self.preset_title or self._make_auto_title(selected_keys))
        self.ax.set_xlabel(attrib_value)
        self.ax.set_ylabel("Number of occurrences")
        self.canvas.draw()

    # ------------------------------------------------------------------
    # Plotting — pie
    # ------------------------------------------------------------------

    def _plot_pie(self, selected_keys):
        if not selected_keys or "-:" not in selected_keys[0]:
            return
        dp = self.data_provider
        data = dp.data_entities
        rounds = {e["round"] for e in data}
        max_round = max(rounds) if rounds else 0

        parts = selected_keys[0].split("-:")
        entity, attrib = parts[1], parts[2]
        self.ax.clear()
        pie_data = next(
            (e["qualiAttributes"][attrib]
             for e in data
             if e["round"] == max_round and e["name"] == entity
             and attrib in e.get("qualiAttributes", {})),
            None
        )
        if pie_data is None:
            return
        labels = list(pie_data.keys())
        values = list(pie_data.values())
        self.ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
        self.ax.axis("equal")
        self.ax.legend()
        self.ax.set_title(self.preset_title or self._make_auto_title(selected_keys))
        self.canvas.draw()

    # ------------------------------------------------------------------
    # Plotting — stackplot
    # ------------------------------------------------------------------

    def _plot_stackplot(self, selected_keys, x_option):
        self.ax.clear()
        if not selected_keys:
            self.canvas.draw()
            return
        dp = self.data_provider
        data = dp.data_entities
        if not data:
            return

        rounds = {e["round"] for e in data}
        nb_rounds = max(rounds)
        nb_phases = dp.nb_phases()
        phase_of_last = max(e["phase"] for e in data if e["round"] == nb_rounds)
        nb_rounds_complete = self._nb_rounds_complete

        list_data = []
        entity_names = []
        attrib_value = ""
        parent_key = "qualiAttributes"

        for key in selected_keys:
            if "-:" not in key:
                continue
            parts = key.split("-:")
            entity, attrib_value = parts[1], parts[-1]
            entity_names.append(entity)

            if x_option != "per step" or nb_phases == 1:
                for r in range(nb_rounds_complete + 1):
                    phase_idx = (
                        self.specified_phase if x_option == "specified phase" else nb_phases
                    ) if r != 0 else 0
                    entries = [
                        e[parent_key][attrib_value]
                        for e in data
                        if e["name"] == entity
                        and attrib_value in e.get(parent_key, {})
                        and e["round"] == r and e["phase"] == phase_idx
                    ]
                    if entries:
                        list_data.append(entries[-1])
            else:
                first = [e[parent_key][attrib_value] for e in data
                         if e["name"] == entity and attrib_value in e.get(parent_key, {})
                         and e["round"] == 0 and e["phase"] == 0]
                if first:
                    list_data.append(first[-1])
                for rr in range(nb_rounds_complete):
                    for pp in range(nb_phases):
                        entries = [e[parent_key][attrib_value] for e in data
                                   if e["name"] == entity
                                   and attrib_value in e.get(parent_key, {})
                                   and e["round"] == rr + 1 and e["phase"] == pp + 1]
                        if entries:
                            list_data.append(entries[-1])
                if phase_of_last != nb_phases:
                    for pp in range(phase_of_last):
                        entries = [e[parent_key][attrib_value] for e in data
                                   if e["name"] == entity
                                   and attrib_value in e.get(parent_key, {})
                                   and e["round"] == nb_rounds and e["phase"] == pp + 1]
                        if entries:
                            list_data.append(entries[-1])

        if not list_data:
            self._show_error("Cannot display data",
                             "No data to display yet. Please advance the simulation.")
            return

        labels = sorted(set(np.concatenate([list(d.keys()) for d in list_data])))
        values = [[d.get(lbl, 0) for d in list_data] for lbl in labels]

        if values and len(values[0]) != len(self._x_value):
            self._show_error("Cannot display data",
                             "No data to display yet. Please advance the simulation.")
            return

        if len(self._x_value) == 1:
            self.ax.stackplot(self._x_value * len(values), values, labels=labels)
        else:
            self.ax.stackplot(self._x_value, values, labels=labels)
            self._draw_step_lines(self._x_value)

        self.ax.legend()
        self.ax.set_xticks(self._x_value)
        self.ax.set_title(self.preset_title or self._make_auto_title(selected_keys))
        self.canvas.draw()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_auto_title(self, selected_keys):
        """Build a chart title from selected indicator keys.
        Format: 'EntityA, EntityB — attr (stat1, stat2), other_attr'
        Multiple stats for the same attribute are grouped: energy (mean, sum).
        """
        entities = []
        attr_stats = {}    # {attr_name: [stat, ...]}  — preserves insertion order
        simple_inds = []   # population, entDef attrs, simvars, players, actions

        for key in selected_keys:
            parts = key.split("-:")
            if key.startswith("entity-:"):
                if parts[1] not in entities:
                    entities.append(parts[1])
                if len(parts) == 4:   # quanti attr with stat
                    attr, stat = parts[2], parts[3]
                    attr_stats.setdefault(attr, [])
                    if stat not in attr_stats[attr]:
                        attr_stats[attr].append(stat)
                else:                 # population or entDef attr
                    if parts[2] not in simple_inds:
                        simple_inds.append(parts[2])
            elif key.startswith("simVariable-:"):
                if parts[1] not in simple_inds:
                    simple_inds.append(parts[1])
            elif key.startswith("player-:"):
                if parts[1] not in entities:
                    entities.append(parts[1])
                if parts[2] not in simple_inds:
                    simple_inds.append(parts[2])
            elif key.startswith("gameActions-:"):
                if parts[1] not in simple_inds:
                    simple_inds.append(parts[1])

        indicators = simple_inds + [
            f"{attr} ({', '.join(stats)})" for attr, stats in attr_stats.items()
        ]
        if entities and indicators:
            return f"{', '.join(entities)} — {', '.join(indicators)}"
        return ', '.join(indicators) if indicators else ""

    def _draw_step_lines(self, x_value):
        if self.data_provider.nb_phases() < 2 or self._get_x_option() != "per step":
            return
        round_label = 1
        for x in x_value:
            if (x - 1) % self.data_provider.nb_phases() == 0 and x != 0:
                self.ax.axvline(x, color="r", ls=":")
                self.ax.text(x, 1, f"Round {round_label} ↓",
                             color="r", ha="left", va="top", rotation=90,
                             transform=self.ax.get_xaxis_transform())
                round_label += 1

    def _show_error(self, title, message):
        dlg = QMessageBox()
        dlg.setIcon(QMessageBox.Warning)
        dlg.setWindowTitle(title)
        dlg.setText(message)
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.exec_()
