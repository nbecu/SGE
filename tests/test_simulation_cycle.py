"""
Simulation cycle integration tests.

These tests run full simulation cycles (nextPhase loop) with the Qt event loop.
They are excluded from the default test run — use:

    pytest -m simulation          # run only simulation tests
    pytest -m "not simulation"    # run everything except simulation tests (default)
    pytest                        # same as above (configured in pytest.ini)
"""
import pytest
from mainClasses.SGSGE import SGModel, Qt


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
def model_with_tiles(qt_app):
    m = SGModel(400, 300)
    cell_type = m.newCellsOnGrid(4, 4, "square", size=40, gap=2)
    tile_type = m.newTileType("Card", shape="rectTile", defaultSize=20)
    tile_type.setDefaultValues({"value": 0})
    yield m, cell_type, tile_type
    m.close()


@pytest.fixture
def model_with_agents(qt_app):
    m = SGModel(400, 300)
    cell_type = m.newCellsOnGrid(4, 4, "square", size=40, gap=2)
    agent_type = m.newAgentType("Walker", "circleAgent", defaultColor=Qt.blue)
    agent_type.setDefaultValues({"energy": 10})
    yield m, cell_type, agent_type
    m.close()


def advance(m, qt_app, n):
    """Call nextPhase n times, flushing Qt events between each call."""
    for _ in range(n):
        m.timeManager.nextPhase()
        qt_app.processEvents()


# ---------------------------------------------------------------------------
# Round / phase counter
# ---------------------------------------------------------------------------

@pytest.mark.simulation
def test_round_counter_advances_with_one_phase(model, qt_app):
    model.newModelPhase(name="turn")
    assert model.timeManager.currentRoundNumber == 0
    advance(model, qt_app, 3)
    assert model.timeManager.currentRoundNumber == 3


@pytest.mark.simulation
def test_phase_counter_cycles_with_two_phases(model, qt_app):
    model.newModelPhase(name="phase_A")
    model.newModelPhase(name="phase_B")
    advance(model, qt_app, 4)  # 2 full rounds
    assert model.timeManager.currentRoundNumber == 2
    assert model.timeManager.currentPhaseNumber == 2


@pytest.mark.simulation
def test_phase_number_within_round(model, qt_app):
    model.newModelPhase(name="P1")
    model.newModelPhase(name="P2")
    model.newModelPhase(name="P3")
    advance(model, qt_app, 1)
    assert model.timeManager.currentPhaseNumber == 1
    advance(model, qt_app, 1)
    assert model.timeManager.currentPhaseNumber == 2
    advance(model, qt_app, 1)
    assert model.timeManager.currentPhaseNumber == 3
    advance(model, qt_app, 1)  # starts round 2
    assert model.timeManager.currentRoundNumber == 2
    assert model.timeManager.currentPhaseNumber == 1


# ---------------------------------------------------------------------------
# Model phase action execution
# ---------------------------------------------------------------------------

@pytest.mark.simulation
def test_model_phase_action_executes_each_round(model, qt_app):
    calls = []
    model.newModelPhase(actions=lambda: calls.append(1), name="counter")
    advance(model, qt_app, 5)
    assert len(calls) == 5


@pytest.mark.simulation
def test_two_model_phases_execute_in_order(model, qt_app):
    log = []
    model.newModelPhase(actions=lambda: log.append("A"), name="A")
    model.newModelPhase(actions=lambda: log.append("B"), name="B")
    advance(model, qt_app, 4)  # 2 full rounds: A, B, A, B
    assert log == ["A", "B", "A", "B"]


# ---------------------------------------------------------------------------
# Attribute changes during simulation
# ---------------------------------------------------------------------------

@pytest.mark.simulation
def test_attribute_accumulates_over_rounds(model_with_grid, qt_app):
    m, cell_type = model_with_grid
    cell_type.setEntities("count", 0)

    def increment():
        for cell in cell_type.entities:
            cell.incValue("count", 1)

    m.newModelPhase(actions=increment, name="inc")
    advance(m, qt_app, 3)

    for cell in cell_type.entities:
        assert cell.getValue("count") == 3


@pytest.mark.simulation
def test_agent_attribute_changes_during_simulation(model_with_agents, qt_app):
    m, cell_type, agent_type = model_with_agents
    agent = agent_type.newAgentOnCell(cell_type.getCell(2, 2))

    def drain():
        agent.decValue("energy", 1)

    m.newModelPhase(actions=drain, name="drain")
    advance(m, qt_app, 4)
    assert agent.getValue("energy") == 6  # 10 - 4


# ---------------------------------------------------------------------------
# Watcher behavior during simulation
# ---------------------------------------------------------------------------

@pytest.mark.simulation
def test_type_watcher_fires_on_attribute_change_during_simulation(model_with_grid, qt_app):
    m, cell_type = model_with_grid
    cell_type.setEntities("state", 0)
    cell = cell_type.getCell(1, 1)

    fired = []
    cell_type.doWhenAttributeChanges("state", lambda e, a: fired.append(e))

    def update():
        cell.incValue("state", 1)  # value changes every round → watcher fires

    m.newModelPhase(actions=update, name="update")
    advance(m, qt_app, 3)
    assert len(fired) == 3
    assert all(e is cell for e in fired)


# ---------------------------------------------------------------------------
# History recording during simulation
# ---------------------------------------------------------------------------

@pytest.mark.simulation
def test_history_records_values_across_rounds(model_with_grid, qt_app):
    m, cell_type = model_with_grid
    cell_type.setEntities("temp", 0)
    cell = cell_type.getCell(1, 1)
    cell.clearHistory()  # discard initialization entry, keep only simulation rounds

    def heat():
        cell.incValue("temp", 10)

    m.newModelPhase(actions=heat, name="heat")
    advance(m, qt_app, 3)

    history = cell.history["value"]["temp"]
    assert len(history) == 3
    recorded_values = [entry[2] for entry in history]
    assert recorded_values == [10, 20, 30]


# ---------------------------------------------------------------------------
# Agent movement during simulation
# ---------------------------------------------------------------------------

@pytest.mark.simulation
def test_agent_moves_between_cells_during_simulation(model_with_agents, qt_app):
    m, cell_type, agent_type = model_with_agents
    start_cell = cell_type.getCell(1, 1)
    target_cell = cell_type.getCell(2, 2)
    agent = agent_type.newAgentOnCell(start_cell)

    assert agent.cell is start_cell
    assert agent in start_cell.agents

    def move():
        if agent.cell is start_cell:
            agent.moveTo(target_cell)

    m.newModelPhase(actions=move, name="move")
    advance(m, qt_app, 1)

    assert agent.cell is target_cell
    assert agent in target_cell.agents
    assert agent not in start_cell.agents


@pytest.mark.simulation
def test_agent_moves_each_round_along_path(model_with_agents, qt_app):
    m, cell_type, agent_type = model_with_agents
    cells = [cell_type.getCell(1, 1), cell_type.getCell(2, 1), cell_type.getCell(3, 1)]
    agent = agent_type.newAgentOnCell(cells[0])

    step = [0]

    def move():
        if step[0] < len(cells) - 1:
            step[0] += 1
            agent.moveTo(cells[step[0]])

    m.newModelPhase(actions=move, name="walk")
    advance(m, qt_app, 2)

    assert agent.cell is cells[2]
    assert agent in cells[2].agents
    assert agent not in cells[0].agents
    assert agent not in cells[1].agents


@pytest.mark.simulation
def test_agent_moves_randomly_during_simulation(model_with_agents, qt_app):
    m, cell_type, agent_type = model_with_agents
    start_cell = cell_type.getCell(2, 2)  # center of 4x4 grid — has neighbors on all sides
    agent = agent_type.newAgentOnCell(start_cell)

    def move():
        agent.moveRandomly()

    m.newModelPhase(actions=move, name="wander")
    advance(m, qt_app, 5)

    # After 5 random moves the agent must still be on exactly one cell
    occupied = [c for c in cell_type.entities if agent in c.agents]
    assert len(occupied) == 1
    assert agent.cell is occupied[0]


# ---------------------------------------------------------------------------
# Attribute operations during simulation
# ---------------------------------------------------------------------------

@pytest.mark.simulation
def test_set_value_direct_on_agent(model_with_agents, qt_app):
    m, cell_type, agent_type = model_with_agents
    agent = agent_type.newAgentOnCell(cell_type.getCell(1, 1))

    def flip():
        current = agent.getValue("energy")
        agent.setValue("energy", 99 if current != 99 else 0)

    m.newModelPhase(actions=flip, name="flip")
    advance(m, qt_app, 1)
    assert agent.getValue("energy") == 99
    advance(m, qt_app, 1)
    assert agent.getValue("energy") == 0


@pytest.mark.simulation
def test_calc_value_on_cell(model_with_grid, qt_app):
    m, cell_type = model_with_grid
    cell_type.setEntities("score", 2)
    cell = cell_type.getCell(1, 1)

    def double():
        cell.calcValue("score", lambda x: x * 2)

    m.newModelPhase(actions=double, name="double")
    advance(m, qt_app, 3)  # 2 → 4 → 8 → 16
    assert cell.getValue("score") == 16


@pytest.mark.simulation
def test_agent_attribute_changes_while_moving(model_with_agents, qt_app):
    m, cell_type, agent_type = model_with_agents
    agent = agent_type.newAgentOnCell(cell_type.getCell(1, 1))
    cells = [cell_type.getCell(i, 1) for i in range(1, 5)]
    step = [0]

    def move_and_drain():
        agent.decValue("energy", 1)
        if step[0] < len(cells) - 1:
            step[0] += 1
            agent.moveTo(cells[step[0]])

    m.newModelPhase(actions=move_and_drain, name="move_drain")
    advance(m, qt_app, 3)  # 3 moves, 3 drains

    assert agent.getValue("energy") == 7   # 10 - 3
    assert agent.cell is cells[3]


@pytest.mark.simulation
def test_cell_transfers_value_to_incoming_agent(model_with_agents, qt_app):
    """Agent picks up a resource from the cell it lands on."""
    m, cell_type, agent_type = model_with_agents
    cell_type.setEntities("resource", 0)
    source_cell = cell_type.getCell(2, 2)
    source_cell.setValue("resource", 5)
    agent = agent_type.newAgentOnCell(cell_type.getCell(1, 1))

    def collect():
        if agent.cell is source_cell:
            amount = agent.cell.getValue("resource")
            agent.incValue("energy", amount)
            agent.cell.setValue("resource", 0)
        else:
            agent.moveTo(source_cell)

    m.newModelPhase(actions=collect, name="collect")
    advance(m, qt_app, 2)  # round 1: move to source; round 2: collect

    assert agent.getValue("energy") == 15  # 10 + 5
    assert source_cell.getValue("resource") == 0


# ---------------------------------------------------------------------------
# SimVariable during simulation
# ---------------------------------------------------------------------------

@pytest.mark.simulation
def test_simvariable_increments_each_round(model, qt_app):
    m = model
    counter = m.newSimVariable("counter", 0)

    m.newModelPhase(actions=lambda: counter.incValue(1), name="inc")
    advance(m, qt_app, 4)

    assert counter.getValue() == 4


@pytest.mark.simulation
def test_simvariable_decrements_each_round(model, qt_app):
    m = model
    stock = m.newSimVariable("stock", 10)

    m.newModelPhase(actions=lambda: stock.decValue(2), name="dec")
    advance(m, qt_app, 3)

    assert stock.getValue() == 4  # 10 - 6


@pytest.mark.simulation
def test_simvariable_calc_value(model, qt_app):
    m = model
    pop = m.newSimVariable("pop", 1)

    m.newModelPhase(actions=lambda: pop.calcValue(lambda x: x * 2), name="double")
    advance(m, qt_app, 4)

    assert pop.getValue() == 16  # 1 → 2 → 4 → 8 → 16


@pytest.mark.simulation
def test_simvariable_set_value_silently_skips_history(model):
    m = model
    v = m.newSimVariable("silent", 0)
    history_len_after_init = len(v.history)  # 1 entry from __init__

    v.setValue_silently(42)
    assert v.getValue() == 42
    assert len(v.history) == history_len_after_init + 1  # saveValueInHistory still called


@pytest.mark.simulation
def test_simvariable_history_records_rounds(model, qt_app):
    m = model
    score = m.newSimVariable("score", 0)
    score.history.clear()  # discard init entry

    m.newModelPhase(actions=lambda: score.incValue(5), name="score")
    advance(m, qt_app, 3)

    assert len(score.history) == 3
    assert [entry[2] for entry in score.history] == [5, 10, 15]


@pytest.mark.simulation
def test_simvariable_updated_from_entity_attribute(model_with_agents, qt_app):
    """SimVariable tracks the sum of an agent attribute across all agents."""
    m, cell_type, agent_type = model_with_agents
    agents = [agent_type.newAgentOnCell(cell_type.getCell(i, 1)) for i in range(1, 4)]
    total_energy = m.newSimVariable("total_energy", 30)  # 3 agents × 10

    def drain_and_sync():
        for a in agents:
            a.decValue("energy", 1)
        total_energy.setValue(sum(a.getValue("energy") for a in agents))

    m.newModelPhase(actions=drain_and_sync, name="drain")
    advance(m, qt_app, 3)

    assert total_energy.getValue() == 21  # 3 agents × (10 - 3)


# ---------------------------------------------------------------------------
# Tile during simulation
# ---------------------------------------------------------------------------

@pytest.mark.simulation
def test_tile_placed_on_cell(model_with_tiles):
    _, cell_type, tile_type = model_with_tiles
    cell = cell_type.getCell(1, 1)
    tile = tile_type.newTileOnCell(cell)

    assert tile.cell is cell
    assert tile in cell.tiles


@pytest.mark.simulation
def test_tile_flip_changes_face(model_with_tiles):
    _, cell_type, tile_type = model_with_tiles
    tile = tile_type.newTileOnCell(cell_type.getCell(1, 1))

    assert tile.face == "front"
    tile.flip()
    assert tile.face == "back"
    tile.flip()
    assert tile.face == "front"


@pytest.mark.simulation
def test_tile_flip_during_simulation(model_with_tiles, qt_app):
    m, cell_type, tile_type = model_with_tiles
    tile = tile_type.newTileOnCell(cell_type.getCell(1, 1))

    m.newModelPhase(actions=lambda: tile.flip(), name="flip")
    advance(m, qt_app, 3)  # front → back → front → back

    assert tile.face == "back"


@pytest.mark.simulation
def test_tile_moves_between_cells(model_with_tiles, qt_app):
    m, cell_type, tile_type = model_with_tiles
    start_cell = cell_type.getCell(1, 1)
    target_cell = cell_type.getCell(2, 2)
    tile = tile_type.newTileOnCell(start_cell)

    def move():
        if tile.cell is start_cell:
            tile.moveTo(target_cell)

    m.newModelPhase(actions=move, name="move")
    advance(m, qt_app, 1)

    assert tile.cell is target_cell
    assert tile in target_cell.tiles
    assert tile not in start_cell.tiles


@pytest.mark.simulation
def test_tile_attribute_changes_during_simulation(model_with_tiles, qt_app):
    m, cell_type, tile_type = model_with_tiles
    tile = tile_type.newTileOnCell(cell_type.getCell(1, 1))

    m.newModelPhase(actions=lambda: tile.incValue("value", 3), name="inc")
    advance(m, qt_app, 4)

    assert tile.getValue("value") == 12  # 0 + 3 × 4


@pytest.mark.simulation
def test_multiple_tiles_stack_on_same_cell(model_with_tiles):
    _, cell_type, tile_type = model_with_tiles
    cell = cell_type.getCell(2, 2)
    tile_a = tile_type.newTileOnCell(cell)
    tile_b = tile_type.newTileOnCell(cell)
    tile_c = tile_type.newTileOnCell(cell)

    assert len(cell.getTiles(tile_type)) == 3
    assert tile_a in cell.tiles
    assert tile_b in cell.tiles
    assert tile_c in cell.tiles
