import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *


# ============================================================================
# Def tic-tac-toe game
# ============================================================================
def tic_tac_toe_game(ui_enabled=True, with_control_panels=True):
    myModel = SGModel(600, 600, windowTitle="tic-tac-toe game")

    # Grid
    Cell = myModel.newCellsOnGrid(3, 3, "square", size=100, gap=5)
    Cell.setEntities("state", "empty")

    # POV
    Cell.newPov("Main_view", "state", {
        "empty": Qt.white,
        "X": Qt.blue,
        "O": Qt.red
    })

    # Players
    Player1 = myModel.newPlayer("Player 1")
    Player2 = myModel.newPlayer("Player 2")
    mark_of_players = {"X":"Player 1" , "O":"Player 2"}


    # Actions (only on empty cells)
    empty_condition = [lambda cell: cell.value("state") == "empty"]
    Player1.addGameAction(myModel.newModifyAction(Cell, {"state": "X"}, 1, conditions=empty_condition))
    Player2.addGameAction(myModel.newModifyAction(Cell, {"state": "O"}, 1, conditions=empty_condition))
    if with_control_panels and ui_enabled:
        Player1.newControlPanel("Player 1")
        Player2.newControlPanel("Player 2")

    # Phases
    myModel.newPlayPhase("Player 1 turn", [Player1], autoForwardWhenAllActionsUsed=True, message_auto_forward=False)
    myModel.newPlayPhase("Player 2 turn", [Player2], autoForwardWhenAllActionsUsed=True, message_auto_forward=False)

    # User selector
    if ui_enabled:
        myModel.newUserSelector()
    myModel.setCurrentPlayer('Admin')

    # End game rule
    endGameRule = myModel.newEndGameRule()
    myModel.winner = None

    def check_victory():
        # Check victory lines, columns and diagonals
        for i in range(1, 4):
            if Cell.getCell(i, 1).value("state") == Cell.getCell(i, 2).value("state") == Cell.getCell(i, 3).value("state") != "empty":
                myModel.winner = mark_of_players[Cell.getCell(i, 1).value("state")]
                print(f"Victory for {myModel.winner}")
                return True
            if Cell.getCell(1, i).value("state") == Cell.getCell(2, i).value("state") == Cell.getCell(3, i).value("state") != "empty":
                myModel.winner = mark_of_players[Cell.getCell(1, i).value("state")]
                print(f"Victory for {myModel.winner}")
                return True
        if Cell.getCell(1, 1).value("state") == Cell.getCell(2, 2).value("state") == Cell.getCell(3, 3).value("state") != "empty":
            myModel.winner = mark_of_players[Cell.getCell(1, 1).value("state")]
            print(f"Victory for {myModel.winner}")
            return True
        if Cell.getCell(1, 3).value("state") == Cell.getCell(2, 2).value("state") == Cell.getCell(3, 1).value("state") != "empty":
            myModel.winner = mark_of_players[Cell.getCell(1, 3).value("state")]
            print(f"Victory for {myModel.winner}")
            return True
        return False

    def check_draw():
        # Draw if no empty cells and no victory
        if len(Cell.getEntities_withValue("state", "empty")) == 0 and myModel.winner is None:
            print(f"Draw")
            return True
        return False

    endGameRule.addEndGameCondition_onLambda(lambda: check_victory(), name="Victory")
    endGameRule.addEndGameCondition_onLambda(lambda: check_draw(), name="Draw")

    if ui_enabled:
        time_label = myModel.newTimeLabel()
        time_label.moveToCoords(390, 300)

    return myModel



if __name__ == "__main__":
    monApp = QtWidgets.QApplication([])
    myModel = tic_tac_toe_game()
    myModel.launch()
    exit_code = monApp.exec()
    if myModel.winner is not None:
        print(f"The winner is: {myModel.winner}")
    else:
        print(f"The game is a draw")
    sys.exit(exit_code)