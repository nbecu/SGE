"""
Regression tests for SGE core model setup.
These tests validate the basic behavior of SGModel, entities, attributes and game spaces.
They serve as a safety net for architectural refactoring.
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
    cell_def = m.newCellsOnGrid(5, 5, "square", size=40, gap=2)
    yield m, cell_def
    m.close()


@pytest.fixture
def model_with_agents(qt_app):
    m = SGModel(400, 300)
    cell_def = m.newCellsOnGrid(5, 5, "square", size=40, gap=2)
    agent_def = m.newAgentType("Sheep", "circleAgent", defaultColor=Qt.blue)
    agent_def.setDefaultValues({"health": "good", "energy": 100})
    yield m, cell_def, agent_def
    m.close()


# ---------------------------------------------------------------------------
# Model initialization
# ---------------------------------------------------------------------------

def test_model_creates_gamespaces_dict(model):
    assert isinstance(model.gameSpaces, dict)


def test_model_creates_empty_agent_types(model):
    assert isinstance(model.agentTypes, dict)
    assert len(model.agentTypes) == 0


def test_model_creates_empty_cell_types(model):
    assert isinstance(model.cellTypes, dict)
    assert len(model.cellTypes) == 0


def test_model_admin_player_exists_by_default(model):
    admin = model.getAdminPlayer()
    assert admin is not None
    assert admin.isAdmin


# ---------------------------------------------------------------------------
# Grid and cell creation
# ---------------------------------------------------------------------------

def test_cell_type_registered_in_model(model_with_grid):
    m, cell_def = model_with_grid
    assert len(m.cellTypes) == 1


def test_grid_has_correct_cell_count(model_with_grid):
    m, cell_def = model_with_grid
    assert len(cell_def.entities) == 25  # 5x5


def test_cell_coordinates_are_one_based(model_with_grid):
    m, cell_def = model_with_grid
    coords = [(c.xCoord, c.yCoord) for c in cell_def.entities]
    assert (1, 1) in coords
    assert (5, 5) in coords
    assert (0, 0) not in coords


def test_get_cell_by_coords(model_with_grid):
    m, cell_def = model_with_grid
    cell = cell_def.getCell(3, 3)
    assert cell is not None
    assert cell.xCoord == 3
    assert cell.yCoord == 3


def test_cell_id_from_coords_consistency(model_with_grid):
    m, cell_def = model_with_grid
    cell = cell_def.getCell(2, 4)
    assert cell.getId() == cell_def.cellIdFromCoords(2, 4)


# ---------------------------------------------------------------------------
# GameSpaces registration
# ---------------------------------------------------------------------------

def test_dashboard_registered_in_gamespaces(model):
    dashboard = model.newDashBoard("Scores")
    assert dashboard in model.gameSpaces.values()


def test_legend_registered_in_gamespaces(model_with_grid):
    m, cell_def = model_with_grid
    legend = m.newLegend("Legend")
    assert legend in m.gameSpaces.values()


def test_textbox_registered_in_textboxes(model):
    tb = model.newTextBox("Hello")
    assert tb in model.TextBoxes


# ---------------------------------------------------------------------------
# Entity attribute system
# ---------------------------------------------------------------------------

def test_set_and_get_value(model_with_grid):
    m, cell_def = model_with_grid
    cell = cell_def.getCell(1, 1)
    cell.setValue("terrain", "forest")
    assert cell.getValue("terrain") == "forest"


def test_isValue(model_with_grid):
    m, cell_def = model_with_grid
    cell = cell_def.getCell(1, 1)
    cell.setValue("terrain", "water")
    assert cell.isValue("terrain", "water")
    assert not cell.isValue("terrain", "forest")


def test_incValue(model_with_grid):
    m, cell_def = model_with_grid
    cell = cell_def.getCell(1, 1)
    cell.setValue("count", 10)
    cell.incValue("count", 5)
    assert cell.getValue("count") == 15


def test_decValue(model_with_grid):
    m, cell_def = model_with_grid
    cell = cell_def.getCell(1, 1)
    cell.setValue("count", 10)
    cell.decValue("count", 3)
    assert cell.getValue("count") == 7


def test_setEntities_sets_all_cells(model_with_grid):
    m, cell_def = model_with_grid
    cell_def.setEntities("biome", "desert")
    for cell in cell_def.entities:
        assert cell.getValue("biome") == "desert"


# ---------------------------------------------------------------------------
# Agent type and creation
# ---------------------------------------------------------------------------

def test_agent_type_registered_in_model(model_with_agents):
    m, cell_def, agent_def = model_with_agents
    assert len(m.agentTypes) == 1


def test_agent_created_at_correct_coords(model_with_agents):
    m, cell_def, agent_def = model_with_agents
    agent = agent_def.newAgentAtCoords(cell_def, 2, 3)
    assert agent.cell.xCoord == 2
    assert agent.cell.yCoord == 3


def test_agent_has_default_attributes(model_with_agents):
    m, cell_def, agent_def = model_with_agents
    agent = agent_def.newAgentAtCoords(cell_def, 1, 1)
    assert agent.getValue("health") == "good"
    assert agent.getValue("energy") == 100


def test_agent_has_view(model_with_agents):
    m, cell_def, agent_def = model_with_agents
    agent = agent_def.newAgentAtCoords(cell_def, 1, 1)
    assert agent.view is not None


# ---------------------------------------------------------------------------
# SimVariable
# ---------------------------------------------------------------------------

def test_simvariable_created(model):
    sv = model.newSimVariable("Score", 0)
    assert sv is not None
    assert sv.getValue() == 0


def test_simvariable_inc(model):
    sv = model.newSimVariable("Score", 10)
    sv.incValue(5)
    assert sv.getValue() == 15
