"""
Tests for SGE entity / entity-type polymorphism.

Validates:
- isEntity and isEntityType flag values on entities and entity types
- setValue() triggers type-level watchers on entities but NOT on entity types
"""
import pytest
from mainClasses.SGSGE import SGModel, Qt


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def setup(qt_app):
    m = SGModel(400, 300)
    cell_type = m.newCellsOnGrid(3, 3, "square", size=40, gap=2)
    agent_type = m.newAgentType("Robot", "circleAgent", defaultColor=Qt.red)
    cell = cell_type.getCell(1, 1)
    agent = agent_type.newAgentOnCell(cell)
    yield m, cell_type, agent_type, cell, agent
    m.close()


# ---------------------------------------------------------------------------
# isEntity flags
# ---------------------------------------------------------------------------

def test_cell_is_entity(setup):
    _, _, _, cell, _ = setup
    assert cell.isEntity is True


def test_agent_is_entity(setup):
    _, _, _, _, agent = setup
    assert agent.isEntity is True


def test_cell_type_is_not_entity(setup):
    _, cell_type, _, _, _ = setup
    assert cell_type.isEntity is False


def test_agent_type_is_not_entity(setup):
    _, _, agent_type, _, _ = setup
    assert agent_type.isEntity is False


# ---------------------------------------------------------------------------
# isEntityType flags
# ---------------------------------------------------------------------------

def test_cell_type_is_entity_type(setup):
    _, cell_type, _, _, _ = setup
    assert cell_type.isEntityType is True


def test_agent_type_is_entity_type(setup):
    _, _, agent_type, _, _ = setup
    assert agent_type.isEntityType is True


def test_cell_is_not_entity_type(setup):
    _, _, _, cell, _ = setup
    assert cell.isEntityType is False


def test_agent_is_not_entity_type(setup):
    _, _, _, _, agent = setup
    assert agent.isEntityType is False


# ---------------------------------------------------------------------------
# Watcher behavior — setValue on entity triggers type-level watcher
# ---------------------------------------------------------------------------

def test_setValue_on_cell_triggers_type_watcher(setup):
    _, cell_type, _, cell, _ = setup
    triggered = []
    cell_type.doWhenAttributeChanges("terrain", lambda e, a: triggered.append(e))
    cell.setValue("terrain", "forest")
    assert len(triggered) == 1
    assert triggered[0] is cell


def test_setValue_on_agent_triggers_type_watcher(setup):
    _, _, agent_type, _, agent = setup
    triggered = []
    agent_type.doWhenAttributeChanges("energy", lambda e, a: triggered.append(e))
    agent.setValue("energy", 50)
    assert len(triggered) == 1
    assert triggered[0] is agent


# ---------------------------------------------------------------------------
# Watcher behavior — setValue on entity type does NOT trigger type-level watcher
# ---------------------------------------------------------------------------

def test_setValue_on_cell_type_does_not_trigger_watcher(setup):
    _, cell_type, _, _, _ = setup
    triggered = []
    cell_type.doWhenAttributeChanges("terrain", lambda e, a: triggered.append(e))
    cell_type.setValue("terrain", "water")
    assert len(triggered) == 0


def test_setValue_on_agent_type_does_not_trigger_watcher(setup):
    _, _, agent_type, _, _ = setup
    triggered = []
    agent_type.doWhenAttributeChanges("energy", lambda e, a: triggered.append(e))
    agent_type.setValue("energy", 100)
    assert len(triggered) == 0
