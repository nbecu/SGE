import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt

from .SGGraphDataProvider import SGGraphDataProvider
from .SGIndicatorSpec import SGIndicatorSpec


class SGMultiGraphPanel:
    """
    Descriptor for one sub-graph in a multi-graph window.
    Created by SGMultiGraphWindow.addPanel().
    """

    _X_AXIS_MAP = {
        "Rounds":          "per round",
        "Rounds & Phases": "per step",
        "Specified phase": "specified phase",
    }

    def __init__(self, graph_type, indicator_tuples, x_axis=None):
        self.graph_type = graph_type
        self.indicator_keys = [
            self._tuple_to_key(t) for t in indicator_tuples
            if self._tuple_to_key(t)
        ]
        if x_axis is not None and x_axis not in self._X_AXIS_MAP:
            raise ValueError(f"addPanel: invalid x_axis '{x_axis}'. "
                             f"Must be one of {list(self._X_AXIS_MAP.keys())}.")
        self.x_axis = self._X_AXIS_MAP.get(x_axis, "per round")

    @staticmethod
    def _tuple_to_key(t):
        if not t:
            return None
        kind = t[0].lower()
        if kind == "entity":
            if len(t) == 3:
                return f"entity-:{t[1]}-:{t[2]}"
            elif len(t) == 4:
                return f"entity-:{t[1]}-:{t[2]}-:{t[3]}"
        elif kind == "simvar":
            return f"simVariable-:{t[1]}"
        elif kind == "player":
            return f"player-:{t[1]}-:{t[2]}"
        elif kind == "gameaction":
            return f"gameActions-:{t[1]}"
        return None


class SGMultiGraphWindow(QMainWindow):
    """
    A window containing multiple matplotlib sub-graphs arranged in a grid.

    Modeler API (called before myModel.launch()):
        mg = myModel.newMultiGraphWindow("Vue d'ensemble")
        mg.addPanel("linear", indicators=[
            ("entity", "Wolf", "population"),
            ("entity", "Sheep", "population"),
            ("entity", "Wolf", "age", "mean"),
        ])
        mg.addPanel("stackplot", indicators=[
            ("entity", "Sheep", "type"),
        ])

    The user opens this window from the graph menu at runtime.
    """

    COLORS = ["gray", "green", "blue", "red", "black", "orange",
              "purple", "pink", "cyan", "magenta"]

    def __init__(self, model, title):
        super().__init__()
        self.model = model
        self.title = title
        self._panel_specs = []     # list of SGMultiGraphPanel, filled by addPanel()
        self._built = False
        self.toolbar = self       # duck-type shim: SGTimeManager calls aGraph.toolbar.refresh_data()

    # ------------------------------------------------------------------
    # Modeler API
    # ------------------------------------------------------------------

    def addPanel(self, graph_type, indicators=None, x_axis=None):
        """
        Register one sub-graph panel.

        Args:
            graph_type (str): "linear", "hist", "pie", or "stackplot"
            indicators (list of tuple): each tuple follows the same convention
                as addGraphPreset:
                    ("entity",    entity_name, attribute)
                    ("entity",    entity_name, attribute, stat)
                    ("simvar",    simvar_name)
                    ("player",    player_name, attribute)
                    ("gameaction", action_type)
            x_axis (str, optional): "Rounds", "Rounds & Phases", or
                "Specified phase". Applies to "linear" and "stackplot" only.
        Returns:
            self  (for fluent chaining if desired)
        """
        panel = SGMultiGraphPanel(graph_type, indicators or [], x_axis=x_axis)
        self._panel_specs.append(panel)
        return self

    # ------------------------------------------------------------------
    # Called at runtime when the user opens the window from the menu
    # ------------------------------------------------------------------

    def open(self):
        """Build the window (first open) or refresh it, then show."""
        if not self._panel_specs:
            return
        self._build()
        self.show()
        self.raise_()

    def _build(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 1000, 700)

        n = len(self._panel_specs)
        ncols = min(n, 2)
        nrows = (n + ncols - 1) // ncols

        self._fig, self._axes = plt.subplots(nrows=nrows, ncols=ncols,
                                             figsize=(8 * ncols, 5 * nrows),
                                             squeeze=False)
        self._fig.suptitle(self.title, fontsize=14)
        self._fig.tight_layout(rect=[0, 0, 1, 0.95])

        canvas = FigureCanvas(self._fig)

        btn_refresh = QPushButton("↺ refresh")
        btn_refresh.setFixedHeight(20)
        btn_refresh.setMaximumWidth(80)
        btn_refresh.setToolTip("Refresh")
        btn_refresh.setStyleSheet("QPushButton { font-size: 9pt; color: gray; }"
                                  "QPushButton:hover { color: black; }")
        btn_refresh.clicked.connect(self._refresh)

        top_bar = QHBoxLayout()
        top_bar.addStretch()
        top_bar.addWidget(btn_refresh)
        top_bar.setContentsMargins(0, 2, 4, 0)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(top_bar)
        layout.addWidget(canvas)
        self.setCentralWidget(central)
        self._canvas = canvas
        self._built = True

        self._draw_all()

    def refresh_data(self):
        """Called automatically by SGTimeManager on each nextTurn."""
        if self._built and self.isVisible():
            self._draw_all()
            self._canvas.draw()

    def _refresh(self):
        self._draw_all()
        self._canvas.draw()

    def _draw_all(self):
        n = len(self._panel_specs)
        ncols = min(n, 2)
        for idx, spec in enumerate(self._panel_specs):
            row, col = divmod(idx, ncols)
            ax = self._axes[row][col]
            ax.clear()
            dp = SGGraphDataProvider(self.model, spec.graph_type)
            dp.reload()
            self._draw_panel(ax, dp, spec)

        # Hide unused axes
        total_cells = self._axes.shape[0] * self._axes.shape[1]
        for extra in range(n, total_cells):
            row, col = divmod(extra, ncols)
            self._axes[row][col].set_visible(False)

        self._fig.tight_layout(rect=[0, 0, 1, 0.95])

    def _draw_panel(self, ax, dp, spec):
        if not spec.indicator_keys or not dp.data_entities:
            ax.set_title("No data")
            return

        is_quanti = spec.graph_type in ("linear", "hist")
        x_value, nb_complete = dp.compute_x_axis(spec.x_axis)

        if spec.graph_type == "linear":
            for pos, key in enumerate(spec.indicator_keys):
                ispec = SGIndicatorSpec(key, is_quantitative=True)
                data = dp.all_quantitative()
                nb_phases = dp.nb_phases()
                data_y = []
                for r in range(nb_complete + 1):
                    phase_idx = nb_phases if r != 0 else 0
                    subset = [e for e in data
                              if e.get("round") == r and e.get("phase") == phase_idx]
                    data_y.extend(ispec.get_data(subset))
                if data_y:
                    color = self.COLORS[pos % len(self.COLORS)]
                    if len(x_value) > len(data_y):
                        data_y.extend([0] * (len(x_value) - len(data_y)))
                    ax.plot(x_value, data_y[:len(x_value)],
                            label=ispec.get_label(), color=color,
                            linestyle=ispec.get_line_style())
            ax.legend(fontsize=7)
            ax.set_xlabel("Round")
            self.__draw_round_lines (ax, x_value, dp, spec.x_axis)

        elif spec.graph_type in ("pie", "stackplot", "hist"):
            # Single-indicator types: use only the first key
            if not spec.indicator_keys:
                return
            key = spec.indicator_keys[0]
            data = dp.data_entities
            if not data:
                return
            rounds = {e["round"] for e in data}
            max_round = max(rounds)

            if spec.graph_type == "hist":
                parts = key.split("-:")
                if len(parts) < 3:
                    return
                entity, attrib = parts[1], parts[2]
                hist_data = next(
                    (e["quantiAttributes"][attrib]["histo"]
                     for e in data
                     if e["name"] == entity and e["round"] == max_round
                     and "quantiAttributes" in e
                     and attrib in e["quantiAttributes"]
                     and "histo" in e["quantiAttributes"][attrib]),
                    None
                )
                if hist_data:
                    x_intervals = hist_data[1]
                    x_centers = np.average([x_intervals[1:], x_intervals[:-1]], axis=0)
                    heights = hist_data[0]
                    ax.hist(x_centers, weights=heights, bins=x_intervals, edgecolor="black")
                    ax.set_xticks(x_intervals)
                    ax.set_xlabel(attrib)
                    ax.set_ylabel("Occurrences")

            elif spec.graph_type == "pie":
                parts = key.split("-:")
                if len(parts) < 3:
                    return
                entity, attrib = parts[1], parts[2]
                pie_data = next(
                    (e["qualiAttributes"][attrib]
                     for e in data
                     if e["round"] == max_round and e["name"] == entity
                     and attrib in e.get("qualiAttributes", {})),
                    None
                )
                if pie_data:
                    ax.pie(list(pie_data.values()), labels=list(pie_data.keys()),
                           autopct="%1.0f%%", startangle=90)
                    ax.axis("equal")

            elif spec.graph_type == "stackplot":
                parts = key.split("-:")
                if len(parts) < 3:
                    return
                entity, attrib = parts[1], parts[2]
                list_data = []
                for r in range(nb_complete + 1):
                    phase_idx = dp.nb_phases() if r != 0 else 0
                    entries = [e["qualiAttributes"][attrib]
                               for e in data
                               if e["name"] == entity
                               and attrib in e.get("qualiAttributes", {})
                               and e["round"] == r and e["phase"] == phase_idx]
                    if entries:
                        list_data.append(entries[-1])
                if list_data:
                    labels = sorted(set(
                        k for d in list_data for k in d.keys()
                    ))
                    values = [[d.get(lbl, 0) for d in list_data] for lbl in labels]
                    xv = list(range(len(list_data)))
                    if len(xv) > 1:
                        ax.stackplot(xv, values, labels=labels)
                    ax.legend(fontsize=7)

        # Panel title from first indicator
        if spec.indicator_keys:
            ispec0 = SGIndicatorSpec(spec.indicator_keys[0], is_quantitative=is_quanti)
            ax.set_title(ispec0.get_label(), fontsize=9)

    def __draw_round_lines (self, ax, x_value, dp, x_axis):
        if x_axis != "per step" or dp.nb_phases() < 2:
            return
        nb_phases = dp.nb_phases()
        round_label = 1
        for x in x_value:
            if (x - 1) % nb_phases == 0 and x != 0:
                ax.axvline(x, color="r", ls=":")
                ax.text(x, 1, f"Round {round_label} ↓",
                        color="r", ha="left", va="top", rotation=90,
                        fontsize=7, transform=ax.get_xaxis_transform())
                round_label += 1

    def closeEvent(self, event):
        if self in self.model.openedGraphs:
            self.model.openedGraphs.remove(self)
        super().closeEvent(event)
