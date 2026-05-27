import sys
import random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

# ============================================================
# Example: addGraphPreset, hideDefaultGraphMenuItems
#
# addGraphPreset registers a named chart accessible from the
# Graphs menu. Each preset opens a pre-configured window.
#
# myModel.addGraphPreset(graph_type, name, indicators,
#                        x_axis=None, x_axis_phase=None)
#
#   graph_type : "linear" | "hist" | "pie" | "stackplot"
#   name       : label in the Graphs menu AND matplotlib chart title
#   indicators : list of tuples:
#       ("entity",     entity_name, attribute)           # population or quali attr
#       ("entity",     entity_name, attribute, stat)     # stat: sum/mean/min/max/stdev
#       ("simvar",     simvar_name)
#       ("player",     player_name, attribute)
#       ("gameaction", action_type)
#   x_axis (optional, linear/stackplot only):
#       "Rounds"           — one point per round (default)
#       "Rounds & Phases"  — one point per phase; vertical lines mark round starts
#       "Specified phase"  — data for a single phase only (requires x_axis_phase)
#   x_axis_phase (int): phase index, required when x_axis="Specified phase"
#
# myModel.hideDefaultGraphMenuItems()              — hide all 4 default entries
# myModel.hideDefaultGraphMenuItems("hist", "pie") — hide specific types only
# ============================================================

monApp = QtWidgets.QApplication([])

myModel = SGModel(700, 550, windowTitle="Graph Preset — Syntax Example")

# --- Grid ---
Terrain = myModel.newCellsOnGrid(8, 8, "square", size=55, gap=2, name="Terrain")
Terrain.setEntities("fertility", lambda: random.randint(1, 10))

# --- Agent types ---
Wolves = myModel.newAgentType("Wolf", "circleAgent", defaultColor=Qt.gray, defaultSize=18)
Wolves.setDefaultValues({"energy": 50})
Wolves.newAgentsAtRandom(8, Terrain, {"status": lambda: random.choice(["fed", "hungry"])})

Sheep = myModel.newAgentType("Sheep", "circleAgent", defaultColor=Qt.white, defaultSize=14)
Sheep.setDefaultValues({"energy": 30})
Sheep.newAgentsAtRandom(20, Terrain, {"status": lambda: random.choice(["adult", "young"])})

# --- SimVariable ---
score = myModel.newSimVariable("Score", 0)

# --- Simulation logic ---
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
# Graph presets
# =============================================================

# Linear chart — multiple quantitative indicators
myModel.addGraphPreset("linear", "Wolf & Sheep populations",
    indicators=[
        ("entity", "Wolf",  "population"),
        ("entity", "Sheep", "population"),
    ])

# Linear chart — explicit stat (mean / sum / min / max / stdev)
myModel.addGraphPreset("linear", "Wolf energy (mean & max)",
    indicators=[
        ("entity", "Wolf", "energy", "mean"),
        ("entity", "Wolf", "energy", "max"),
    ])

# Linear chart — SimVariable
myModel.addGraphPreset("linear", "Score over time",
    indicators=[("simvar", "Score")])

# Linear chart — phase-level granularity (vertical lines at round boundaries)
myModel.addGraphPreset("linear", "Sheep energy per phase",
    indicators=[("entity", "Sheep", "energy", "mean")],
    x_axis="Rounds & Phases")

# Histogram — quantitative attribute distribution
myModel.addGraphPreset("hist", "Sheep energy distribution",
    indicators=[("entity", "Sheep", "energy")])

# Pie chart — qualitative attribute, current round (single indicator)
myModel.addGraphPreset("pie", "Wolf status",
    indicators=[("entity", "Wolf", "status")])

# Stack plot — qualitative attribute over rounds
myModel.addGraphPreset("stackplot", "Sheep status over rounds",
    indicators=[("entity", "Sheep", "status")])

# Hide all four default menu entries so only the named presets appear.
myModel.hideDefaultGraphMenuItems()
# To hide specific types only:
# myModel.hideDefaultGraphMenuItems("hist", "pie")

myModel.launch()
sys.exit(monApp.exec())
