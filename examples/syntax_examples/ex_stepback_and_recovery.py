"""
Example / test model for the Step Backward and Recovery chantier (world state recording).

Based on aGameExample. Used to:
- Test and verify the implementation of world state snapshot, backward/forward, recovery, replay.
- Exemplify the functionality once implemented.

This example includes both PlayPhases and a ModelPhase so that all event types
(game actions and nextStep, including automatic phase changes) are present and testable.
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *


monApp = QtWidgets.QApplication([])


# STEP1 Model

myModel = SGModel(1100, 820, windowTitle="Step backward and recovery example")


# STEP2 Grid and Cells

Cell = myModel.newCellsOnGrid(7, 7, "square", size=60)
Cell.setEntities("Resource", 2)
Cell.setEntities("ProtectionLevel", "Free")
Cell.setRandomEntities("Resource", 3, 7)
Cell.setRandomEntities("Resource", 1, 3)
Cell.setRandomEntities("Resource", 0, 8)
Cell.setRandomEntities("ProtectionLevel", "Reserve", 1)

Cell.newPov("Resource", "Resource", {3: Qt.darkGreen, 2: Qt.green, 1: Qt.yellow, 0: Qt.white})
Cell.newBorderPovColorAndWidth("ProtectionLevel", "ProtectionLevel", {"Reserve": [Qt.magenta, 5], "Free": [Qt.black, 1]})
Cell.displayBorderPov("ProtectionLevel")


# STEP3 Agents

Workers = myModel.newAgentType("Workers", "rectAgent1", defaultColor=Qt.gray)
Birds = myModel.newAgentType("Birds", "triangleAgent2", defaultColor=Qt.yellow)
Sheeps = myModel.newAgentType("Sheeps", "triangleAgent1")
Sheeps.setDefaultValues({
    "health": (lambda: random.choice(["good", "bad"])),
    "hunger": (lambda: random.choice(["good", "bad"]))
})
Sheeps.newPov("Health", "health", {"good": Qt.blue, "bad": Qt.red})
Sheeps.newPov("Hunger", "hunger", {"good": Qt.green, "bad": Qt.yellow})
Sheeps.setDefaultValue("hunger", "bad")

aSecondBird = Birds.newAgentAtCoords(Cell, 4, 5)
aWorker = Workers.newAgentAtCoords(Cell, 2, 2)
aSheep = Sheeps.newAgentAtCoords(Cell, 3, 3)
aSecondSheep = Sheeps.newAgentAtCoords(Cell, 1, 5)
aThirdSheep = Sheeps.newAgentAtCoords(Cell, 3, 5)


# STEP3b Tiles (for testing snapshot with tiles: create/delete/flip) — with images if available
image_paths = listImagePaths([Path(__file__).parent / "images", Path(__file__).parent.parent.parent / "images", "./images"])

def get_pixmap_at_index(i):
    """Image déterministe : index i (cyclé si i >= len(image_paths))."""
    if not image_paths:
        return None
    return QPixmap(str(image_paths[i % len(image_paths)]))

# Tile type: imageTile if we have images, else rectTile with colors
has_images = bool(image_paths)
CardTiles = myModel.newTileType(
    name="StepbackCards",
    shape="imageTile" if has_images else "rectTile",
    defaultSize=45,
    positionOnCell="center",
    defaultFace="back",
    frontColor=Qt.blue,
    backColor=Qt.darkCyan
)
# Place 5 tuiles : dos = même image (index 0), face = image par index (1, 2, 3, …)
back_pixmap = get_pixmap_at_index(0) if has_images else None
for idx, (x, y) in enumerate([(1, 1), (2, 2), (3, 3), (4, 4), (5, 1)]):
    front_pix = get_pixmap_at_index(idx + 1) if has_images else None
    CardTiles.newTileOnCell(Cell.getCell(x, y), face="back", frontImage=front_pix, backImage=back_pixmap)


# STEP4 Admin Players and GameActions

globalLegend = myModel.newLegend("Global Legend", alwaysDisplayDefaultAgentSymbology=True)

Player1 = myModel.newPlayer("Player 1")
createA1 = myModel.newCreateAction(Workers, uses_per_round=20)
Player1.addGameAction(createA1)
Player1.addGameAction(myModel.newDeleteAction(Workers, inf))
Player1.addGameAction(myModel.newDeleteAction(Cell, "infinite"))
aGameAction = Player1.addGameAction(myModel.newModifyAction(Cell, {"Resource": 3}, 3))
Player1.addGameAction(myModel.newMoveAction(Workers, 10))
Player1.addGameAction(myModel.newModifyAction(Sheeps, {"health": "good"}))
Player1.addGameAction(myModel.newModifyAction(Sheeps, {"health": "bad"}))
# Tile actions: create (on cell), delete, flip
Player1.addGameAction(myModel.newCreateAction(CardTiles, uses_per_round=5))
Player1.addGameAction(myModel.newDeleteAction(CardTiles, inf))
Player1.addGameAction(myModel.newFlipAction(CardTiles, uses_per_round=10))
Player1ControlPanel = Player1.newControlPanel("Player 1 Actions", defaultActionSelected=aGameAction)

Player2 = myModel.newPlayer("Player 2")
Player2.addGameAction(myModel.newCreateAction(Birds, uses_per_round=4))
Player2.addGameAction(myModel.newCreateAction(Sheeps, {"health": "good"}, 4))
Player2.addGameAction(myModel.newMoveAction(Birds, 10))
aGameAction = Player2.addGameAction(myModel.newModifyAction(Cell, {"ProtectionLevel": "Reserve"}, 3))
Player2.addGameAction(myModel.newModifyAction(Cell, {"ProtectionLevel": "Free"}))
Player2ControlPanel = Player2.newControlPanel("Player 2 Actions", defaultActionSelected=aGameAction)

userSelector = myModel.newUserSelector()


# STEP5 Time management (PlayPhases + ModelPhase for full coverage)

myModel.newPlayPhase("Player 1 to play", [Player1])
myModel.newPlayPhase("Your turn player 2", [Player2])
# ModelPhase: move all sheeps (1 cell), all birds (2 cells), and set 3 cells with Resource=3 to Resource=2
moveAllSheeps = Sheeps.newModelAction(actions=[lambda agent: agent.moveAgent(method="random")])
moveAllBirds = Birds.newModelAction(actions=[lambda agent: agent.moveAgent(method="random", numberOfMovement=2)])
# Cell.setRandomEntities_withValue(attribute_to_set, value_to_set, nb_entities, condition_attr, condition_val)
setThreeResource3CellsTo2 = lambda: Cell.setRandomEntities_withValue("Resource", 2, 3, "Resource", 3)
myModel.newModelPhase(
    actions=[moveAllSheeps, moveAllBirds, setThreeResource3CellsTo2],
    name="Automatic sheep and birds move",
    # auto_forward=True
)

GameRounds = myModel.newTimeLabel(None, Qt.white, Qt.black, Qt.black)
myModel.setCurrentPlayer("Player 1")


# STEP6 DashBoard and EndGameRule

score1 = myModel.newSimVariable("Global Score", 0)
DashBoard = myModel.newDashBoard(borderColor=Qt.black, textColor=Qt.black)
i1 = DashBoard.addIndicator(Cell, "sumAtt", attribute="Resource", color=Qt.black)
i2 = DashBoard.addIndicator(Cell, "avgAtt", attribute="Resource", color=Qt.black)
i3 = DashBoard.addIndicator([Workers, Birds, Sheeps], "nb", color=Qt.black)
i4 = DashBoard.addIndicator(Workers, "nb", color=Qt.black)
i5 = DashBoard.addIndicatorOnSimVariable(score1)

endGameRule = myModel.newEndGameRule(numberRequired=2)
endGameRule.addEndGameCondition_onIndicator(
    i1, "greater", 100, name="Resource greater than 100")
endGameRule.addEndGameCondition_onEntity(
    Cell.getEntity(1, 5), "Resource", "greater", 2,
    name="Cell(1-5) Resource is greater than 2", aGrid=Cell.grid)
endGameRule.displayEndGameConditions()

# Auto-save whole simulation when the window is closed (user is asked to confirm)
myModel.enableAutoSaveSimulationOnClose(confirm=True)
# Recovery: save state to disk at each phase (_recovery_states/) so it can be restored after a crash
myModel.enableRecoverySystem(True)


# STEP7 TextBox

TextBox = myModel.newTextBox(
    title="Your game is starting...",
    textToWrite="Welcome! Use backward/forward and recovery once the chantier is implemented.",
    titleAlignment="center"
)

myModel.setCurrentPlayer("Player 1")


# ----- Task 1 validation: snapshot build / write / read / apply (run with: python ex_stepback_and_recovery.py validate) -----
def _validate_task1_snapshot():
    """Validate snapshot round-trip and apply. Returns True if OK."""
    try:
        tm = myModel.timeManager
        r0, p0 = tm.currentRoundNumber, tm.currentPhaseNumber
        cur_player0 = getattr(myModel, "currentPlayerName", None) or ""
        # Build without history_value (disk-like)
        snap = build_snapshot_from_model(myModel)
        assert snap.get("round") == r0 and snap.get("phase") == p0
        assert snap.get("current_player_name") == cur_player0
        assert "players" in snap and len(snap["players"]) >= 2
        assert "entities" in snap and "agents" in snap["entities"] and "tiles" in snap["entities"]
        assert len(snap["entities"]["tiles"]) >= 5, "snapshot should contain tiles"
        # Write / read
        fd, path = tempfile.mkstemp(suffix=".json", prefix="sge_validate_")
        os.close(fd)
        try:
            write_snapshot_to_file(snap, path, use_gzip=False)
            snap2 = read_snapshot_from_file(path)
            assert snap2.get("round") == r0 and snap2.get("phase") == p0
            # Apply (restore same state)
            apply_snapshot_to_model(myModel, snap2)
            assert tm.currentRoundNumber == r0 and tm.currentPhaseNumber == p0
            assert (getattr(myModel, "currentPlayerName", None) or "") == cur_player0
        finally:
            if os.path.exists(path):
                os.remove(path)
        # Build with history_value (backward/redo stack-like)
        snap_h = build_snapshot_from_model(myModel, include_history_value=True)
        assert any("history_value" in p for p in snap_h["players"]), "players should have history_value key"
        # Apply snapshot with history_value (simulate redo)
        apply_snapshot_to_model(myModel, snap_h)
        assert tm.currentRoundNumber == r0 and tm.currentPhaseNumber == p0
        return True
    except Exception as e:
        print(f"Task 1 validation FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if "validate" in sys.argv:
    ok = _validate_task1_snapshot()
    print("Task 1 (snapshot) validation: OK" if ok else "Task 1 validation: FAILED")
    sys.exit(0 if ok else 1)


myModel.launch()


sys.exit(monApp.exec_())
