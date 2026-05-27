import sys
import random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# ============================================================
# Example: newMultiGraphWindow
#
# A multi-graph window displays several sub-charts in a single
# window, defined once by the modeler before launch().
# Panels are arranged automatically in a 2-column grid.
# The window auto-refreshes at each simulation step while visible.
# It appears at the top of the Graphs menu (above presets).
#
# mg = myModel.newMultiGraphWindow(title)
# mg.addPanel(graph_type, indicators, x_axis=None)
#
#   graph_type : "linear" | "hist" | "pie" | "stackplot"
#   indicators : list of tuples — same format as addGraphPreset:
#       ("entity",     entity_name, attribute)           # population or quali attr
#       ("entity",     entity_name, attribute, stat)     # stat: sum/mean/min/max/stdev
#       ("simvar",     simvar_name)
#       ("player",     player_name, attribute)
#       ("gameaction", action_type)
#   x_axis (optional, linear/stackplot only):
#       "Rounds"           — one point per round (default)
#       "Rounds & Phases"  — one point per phase; vertical lines mark round starts
#       "Specified phase"  — data for a single phase only (requires x_axis_phase)
# ============================================================

monApp = QtWidgets.QApplication([])

myModel = SGModel(700, 550, windowTitle="MultiGraphWindow — Syntax Example")

# --- Grid & agents ---
Terrain = myModel.newCellsOnGrid(8, 8, "square", size=55, gap=2, name="Terrain")
Terrain.setEntities("fertility", lambda: random.randint(1, 10))

Wolves = myModel.newAgentType("Wolf", "circleAgent", defaultColor=Qt.gray, defaultSize=18)
Wolves.setDefaultValues({"energy": 50})
Wolves.newAgentsAtRandom(8, Terrain, {"status": lambda: random.choice(["fed", "hungry"])})

Sheep = myModel.newAgentType("Sheep", "circleAgent", defaultColor=Qt.white, defaultSize=14)
Sheep.setDefaultValues({"energy": 30})
Sheep.newAgentsAtRandom(20, Terrain, {"status": lambda: random.choice(["adult", "young"])})

score = myModel.newSimVariable("Score", 0)

def step():
    for wolf in Wolves.getEntities():
        wolf.moveRandomly()
        wolf.decValue("energy", random.randint(2, 8), 0)
        wolf.setValue("status", "fed" if wolf.value("energy") > 30 else "hungry")
    for sheep in Sheep.getEntities():
        sheep.moveRandomly()
        sheep.incValue("energy", random.randint(1, 5), 100)
        sheep.setValue("status", "adult" if sheep.value("energy") > 50 else "young")
    score.incValue(len(Sheep.getEntities()))

myModel.newModelPhase(actions=step, name="Move")
myModel.newTimeLabel("Rounds")

# =============================================================
# Multi-graph window 1: "Overview" — 4 panels in a 2×2 grid
# =============================================================

overview = myModel.newMultiGraphWindow("Overview")

# Panel 1 — populations (linear, top-left)
overview.addPanel("linear",
    indicators=[
        ("entity", "Wolf",  "population"),
        ("entity", "Sheep", "population"),
    ])

# Panel 2 — Wolf status over rounds (stackplot, top-right)
overview.addPanel("stackplot",
    indicators=[("entity", "Wolf", "status")])

# Panel 3 — Sheep energy histogram (bottom-left)
overview.addPanel("hist",
    indicators=[("entity", "Sheep", "energy")])

# Panel 4 — Sheep status, most recent round (pie, bottom-right)
overview.addPanel("pie",
    indicators=[("entity", "Sheep", "status")])

# =============================================================
# Multi-graph window 2: "Energy details" — phase-level granularity
# =============================================================

details = myModel.newMultiGraphWindow("Energy details")

# Panel 1 — Wolf energy with mean & max, one point per phase
details.addPanel("linear",
    indicators=[
        ("entity", "Wolf", "energy", "mean"),
        ("entity", "Wolf", "energy", "max"),
    ],
    x_axis="Rounds & Phases")

# Panel 2 — Score evolution
details.addPanel("linear",
    indicators=[("simvar", "Score")])

myModel.launch()
sys.exit(monApp.exec())
