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
