"""
Player and GameAction tests.

Tests the game action system (ActivateAction, ModifyAction, MoveAction, FlipAction,
CreateAction, DeleteAction) via direct perform_with() calls (no UI clicks needed),
and BotPlayer with a random strategy.

Tests that call advance() are marked @pytest.mark.simulation (Qt event loop required).
Other tests create Qt objects but do not run simulation cycles.
"""
import pytest
from mainClasses.SGSGE import SGModel, Qt
from mainClasses.SGBotPlayer import SGBotPlayer, SGBotGameAdapter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def advance(m, qt_app, n):
    """Call nextPhase n times, flushing Qt events between each call."""
    for _ in range(n):
        m.timeManager.nextPhase()
        qt_app.processEvents()


class SimpleAdapter(SGBotGameAdapter):
    """Minimal adapter: returns all entities of the action's target type as targets."""

    def get_valid_targets(self, action, player):
        return list(action.targetType.entities)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def model(qt_app):
    m = SGModel(400, 300)
    yield m
    m.close()


@pytest.fixture
def model_with_grid(qt_app):
    m = SGModel(400, 300)
    cell_type = m.newCellsOnGrid(4, 4, "square", size=40, gap=2)
    yield m, cell_type
    m.close()


@pytest.fixture
def model_with_agents(qt_app):
    m = SGModel(400, 300)
    cell_type = m.newCellsOnGrid(4, 4, "square", size=40, gap=2)
    agent_type = m.newAgentType("Walker", "circleAgent", defaultColor=Qt.blue)
    agent_type.setDefaultValues({"energy": 10})
    yield m, cell_type, agent_type
    m.close()


@pytest.fixture
def model_with_tiles(qt_app):
    m = SGModel(400, 300)
    cell_type = m.newCellsOnGrid(4, 4, "square", size=40, gap=2)
    tile_type = m.newTileType("Card", shape="rectTile", defaultSize=20)
    tile_type.setDefaultValues({"value": 0})
    yield m, cell_type, tile_type
    m.close()


# ---------------------------------------------------------------------------
# Player attributes
# ---------------------------------------------------------------------------

def test_player_has_attributes(model):
    m = model
    player = m.newPlayer("Alice", attributesAndValues={"score": 0})
    assert player.getValue("score") == 0
    player.setValue("score", 42)
    assert player.getValue("score") == 42


@pytest.mark.simulation
def test_player_attribute_changes_during_simulation(model, qt_app):
    m = model
    player = m.newPlayer("Alice", attributesAndValues={"score": 0})
    m.newModelPhase(actions=lambda: player.incValue("score", 1), name="score")
    advance(m, qt_app, 5)
    assert player.getValue("score") == 5


# ---------------------------------------------------------------------------
# ActivateAction
# ---------------------------------------------------------------------------

def test_activate_action_executes_method_on_cell(model_with_grid):
    m, cell_type = model_with_grid
    cell_type.setEntities("activated", False)
    player = m.newPlayer("Alice")
    action = player.newActivateAction(
        object_type=cell_type,
        method=lambda e: e.setValue("activated", True)
    )
    cell = cell_type.getCell(1, 1)
    action.perform_with(cell, serverUpdate=False)
    assert cell.getValue("activated") is True


@pytest.mark.simulation
def test_activate_action_respects_uses_per_round(model_with_grid, qt_app):
    m, cell_type = model_with_grid
    cell_type.setEntities("count", 0)
    player = m.newPlayer("Alice")
    action = player.newActivateAction(
        object_type=cell_type,
        method=lambda e: e.incValue("count", 1),
        uses_per_round=2
    )
    m.newPlayPhase("turn", activePlayers=[player])
    advance(m, qt_app, 1)  # enter PlayPhase — uses_per_round now enforced

    cell = cell_type.getCell(1, 1)
    action.perform_with(cell, serverUpdate=False)
    action.perform_with(cell, serverUpdate=False)
    action.perform_with(cell, serverUpdate=False)  # should be blocked

    assert cell.getValue("count") == 2


def test_activate_action_condition_blocks_execution(model_with_grid):
    m, cell_type = model_with_grid
    cell_type.setEntities("state", "idle")
    player = m.newPlayer("Alice")
    action = player.newActivateAction(
        object_type=cell_type,
        method=lambda e: e.setValue("state", "active"),
        conditions=[lambda e: e.getValue("state") == "idle"]
    )
    cell = cell_type.getCell(1, 1)
    action.perform_with(cell, serverUpdate=False)  # state is idle → executes
    assert cell.getValue("state") == "active"

    action.perform_with(cell, serverUpdate=False)  # state is active → blocked
    assert cell.getValue("state") == "active"  # unchanged


# ---------------------------------------------------------------------------
# ModifyAction
# ---------------------------------------------------------------------------

def test_modify_action_sets_attribute_on_cell(model_with_grid):
    m, cell_type = model_with_grid
    cell_type.setEntities("terrain", "grass")
    player = m.newPlayer("Alice")
    action = player.newModifyAction(
        entity_type=cell_type,
        dictAttributes={"terrain": "water"}
    )
    cell = cell_type.getCell(2, 2)
    action.perform_with(cell, serverUpdate=False)
    assert cell.getValue("terrain") == "water"


# ---------------------------------------------------------------------------
# MoveAction
# ---------------------------------------------------------------------------

def test_move_action_moves_agent(model_with_agents):
    m, cell_type, agent_type = model_with_agents
    start_cell = cell_type.getCell(1, 1)
    target_cell = cell_type.getCell(2, 2)
    agent = agent_type.newAgentOnCell(start_cell)
    player = m.newPlayer("Alice")
    action = player.newMoveAction(agent_type)

    action.perform_with(agent, target_cell, serverUpdate=False)

    assert agent.cell is target_cell
    assert agent in target_cell.agents
    assert agent not in start_cell.agents


# ---------------------------------------------------------------------------
# FlipAction
# ---------------------------------------------------------------------------

def test_flip_action_flips_tile(model_with_tiles):
    m, cell_type, tile_type = model_with_tiles
    tile = tile_type.newTileOnCell(cell_type.getCell(1, 1))
    player = m.newPlayer("Alice")
    action = player.newFlipAction(tile_type)

    assert tile.face == "front"
    action.perform_with(tile, serverUpdate=False)
    assert tile.face == "back"
    action.perform_with(tile, serverUpdate=False)
    assert tile.face == "front"


# ---------------------------------------------------------------------------
# CreateAction
# ---------------------------------------------------------------------------

def test_create_action_creates_agent_on_cell(model_with_agents):
    m, cell_type, agent_type = model_with_agents
    player = m.newPlayer("Alice")
    action = player.newCreateAction(entity_type=agent_type)

    cell = cell_type.getCell(1, 1)
    count_before = len(agent_type.entities)
    action.perform_with(cell, serverUpdate=False)
    assert len(agent_type.entities) == count_before + 1
    assert any(a.cell is cell for a in agent_type.entities)


# ---------------------------------------------------------------------------
# DeleteAction
# ---------------------------------------------------------------------------

def test_delete_action_removes_agent(model_with_agents):
    m, cell_type, agent_type = model_with_agents
    agent = agent_type.newAgentOnCell(cell_type.getCell(1, 1))
    player = m.newPlayer("Alice")
    action = player.newDeleteAction(entity_type=agent_type)

    count_before = len(agent_type.entities)
    action.perform_with(agent, serverUpdate=False)
    assert len(agent_type.entities) == count_before - 1
    assert agent not in agent_type.entities


# ---------------------------------------------------------------------------
# BotPlayer
# ---------------------------------------------------------------------------

def test_bot_player_executes_activate_action(model_with_grid):
    m, cell_type = model_with_grid
    cell_type.setEntities("touched", False)
    player = m.newPlayer("Bot")
    player.newActivateAction(
        object_type=cell_type,
        method=lambda e: e.setValue("touched", True)
    )

    bot = SGBotPlayer(player, SimpleAdapter(m), strategy="random")
    bot.execute_turn()

    touched = [c for c in cell_type.entities if c.getValue("touched") is True]
    assert len(touched) == 1


@pytest.mark.simulation
def test_bot_player_stays_within_uses_per_round(model_with_grid, qt_app):
    m, cell_type = model_with_grid
    cell_type.setEntities("count", 0)
    player = m.newPlayer("Bot")
    player.newActivateAction(
        object_type=cell_type,
        method=lambda e: e.incValue("count", 1),
        uses_per_round=3
    )
    m.newPlayPhase("turn", activePlayers=[player])
    advance(m, qt_app, 1)  # enter PlayPhase — uses_per_round now enforced

    bot = SGBotPlayer(player, SimpleAdapter(m), strategy="random")
    for _ in range(6):  # try 6 times, only 3 should execute
        bot.execute_turn()

    total = sum(c.getValue("count") for c in cell_type.entities)
    assert total == 3
