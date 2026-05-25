"""
Tests for the graph API exposed to modelers:
  - addGraphPreset (ValueError guards + happy path)
  - hideDefaultGraphMenuItems (guards + visibility)
  - SGGraphDataProvider.available_groups (category-aware combobox content)
  - SGGraphDataProvider.is_flat (safety guard on non-linear types)

Tests that require a full simulation cycle are marked @pytest.mark.simulation.
"""
import pytest
from mainClasses.SGSGE import SGModel, Qt
from mainClasses.graph.SGGraphDataProvider import SGGraphDataProvider


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def model(qt_app):
    m = SGModel(400, 300)
    yield m
    m.close()


@pytest.fixture
def model_with_cells_only(qt_app):
    """Model with a cell type only; advances 2 rounds to populate the dataRecorder."""
    m = SGModel(400, 300)
    cells = m.newCellsOnGrid(4, 4, "square", size=40, gap=2, name="Patch")
    cells.setEntities("fertility", 5)
    m.newModelPhase(actions=lambda: None, name="step")
    for _ in range(2):
        m.timeManager.nextPhase()
        qt_app.processEvents()
    yield m
    m.close()


@pytest.fixture
def model_with_cells_agents_simvar(qt_app):
    """Model with cells, agents, and a SimVar; advances 2 rounds."""
    m = SGModel(400, 300)
    cells = m.newCellsOnGrid(4, 4, "square", size=40, gap=2, name="Patch")
    cells.setEntities("fertility", 5)
    wolves = m.newAgentType("Wolf", "circleAgent")
    wolves.setDefaultValues({"energy": 10})
    wolves.newAgentsAtRandom(3, cells)
    score = m.newSimVariable("Score", 0)
    m.newModelPhase(actions=lambda: score.incValue(1), name="step")
    for _ in range(2):
        m.timeManager.nextPhase()
        qt_app.processEvents()
    yield m
    m.close()


# ===========================================================================
# addGraphPreset — ValueError guards
# ===========================================================================

def test_addGraphPreset_invalid_graph_type_raises(model):
    with pytest.raises(ValueError, match="invalid graph_type"):
        model.addGraphPreset("circular", "Test",
                             indicators=[("entity", "Wolf", "population")])


def test_addGraphPreset_invalid_stat_raises(model):
    with pytest.raises(ValueError, match="invalid stat"):
        model.addGraphPreset("linear", "Test",
                             indicators=[("entity", "Wolf", "energy", "average")])


def test_addGraphPreset_invalid_x_axis_raises(model):
    with pytest.raises(ValueError, match="invalid x_axis"):
        model.addGraphPreset("linear", "Test",
                             indicators=[("entity", "Wolf", "population")],
                             x_axis="Weekly")


def test_addGraphPreset_x_axis_phase_without_specified_phase_raises(model):
    with pytest.raises(ValueError, match="x_axis_phase requires"):
        model.addGraphPreset("linear", "Test",
                             indicators=[("entity", "Wolf", "population")],
                             x_axis="Rounds",
                             x_axis_phase=2)


def test_addGraphPreset_x_axis_phase_with_specified_phase_does_not_raise(model):
    # Should not raise
    model.addGraphPreset("linear", "Test",
                         indicators=[("entity", "Wolf", "population")],
                         x_axis="Specified phase",
                         x_axis_phase=2)


# ===========================================================================
# addGraphPreset — happy path
# ===========================================================================

def test_addGraphPreset_adds_action_to_list(model):
    assert len(model._graph_preset_actions) == 0
    model.addGraphPreset("linear", "Wolves",
                         indicators=[("entity", "Wolf", "population")])
    assert len(model._graph_preset_actions) == 1


def test_addGraphPreset_separator_becomes_visible(model):
    assert not model._graph_preset_separator.isVisible()
    model.addGraphPreset("linear", "Wolves",
                         indicators=[("entity", "Wolf", "population")])
    assert model._graph_preset_separator.isVisible()


def test_addGraphPreset_action_has_correct_text(model):
    model.addGraphPreset("pie", "Wolf status",
                         indicators=[("entity", "Wolf", "status")])
    action = model._graph_preset_actions[-1]
    assert action.text() == "Wolf status"


def test_addGraphPreset_multiple_presets_accumulate(model):
    model.addGraphPreset("linear", "A", indicators=[("entity", "Wolf", "population")])
    model.addGraphPreset("hist",   "B", indicators=[("entity", "Wolf", "energy")])
    assert len(model._graph_preset_actions) == 2


# ===========================================================================
# hideDefaultGraphMenuItems
# ===========================================================================

def test_default_actions_all_visible_initially(model):
    for action in model._graph_default_actions.values():
        assert action.isVisible()


def test_hideDefaultGraphMenuItems_all(model):
    model.hideDefaultGraphMenuItems()
    for action in model._graph_default_actions.values():
        assert not action.isVisible()


def test_hideDefaultGraphMenuItems_specific(model):
    model.hideDefaultGraphMenuItems("hist", "pie")
    assert not model._graph_default_actions["hist"].isVisible()
    assert not model._graph_default_actions["pie"].isVisible()
    assert model._graph_default_actions["linear"].isVisible()
    assert model._graph_default_actions["stackplot"].isVisible()


def test_hideDefaultGraphMenuItems_invalid_type_raises(model):
    with pytest.raises(ValueError, match="invalid graph_type"):
        model.hideDefaultGraphMenuItems("radar")


# ===========================================================================
# SGGraphDataProvider.is_flat — safety guard for categorical types
# ===========================================================================

def test_is_flat_returns_false_for_pie(model):
    dp = SGGraphDataProvider(model, "pie")
    assert dp.is_flat("entity-:Wolf-:status") is False


def test_is_flat_returns_false_for_stackplot(model):
    dp = SGGraphDataProvider(model, "stackplot")
    assert dp.is_flat("entity-:Sheep-:type") is False


# ===========================================================================
# SGGraphDataProvider.available_groups
# ===========================================================================

@pytest.mark.simulation
def test_available_groups_always_starts_with_all(model_with_cells_only):
    dp = SGGraphDataProvider(model_with_cells_only, "linear")
    assert dp.available_groups()[0] == "All"


@pytest.mark.simulation
def test_available_groups_includes_entities_and_cells(model_with_cells_only):
    dp = SGGraphDataProvider(model_with_cells_only, "linear")
    groups = dp.available_groups()
    assert "Entities" in groups
    assert "Cells" in groups


@pytest.mark.simulation
def test_available_groups_no_agents_when_absent(model_with_cells_only):
    dp = SGGraphDataProvider(model_with_cells_only, "linear")
    assert "Agents" not in dp.available_groups()


@pytest.mark.simulation
def test_available_groups_includes_agents_when_present(model_with_cells_agents_simvar):
    dp = SGGraphDataProvider(model_with_cells_agents_simvar, "linear")
    groups = dp.available_groups()
    assert "Agents" in groups
    assert "Cells" in groups


@pytest.mark.simulation
def test_available_groups_includes_simvars_when_present(model_with_cells_agents_simvar):
    dp = SGGraphDataProvider(model_with_cells_agents_simvar, "linear")
    assert "SimVars" in dp.available_groups()


@pytest.mark.simulation
def test_available_groups_no_gameactions_when_no_actions_performed(model_with_cells_agents_simvar):
    dp = SGGraphDataProvider(model_with_cells_agents_simvar, "linear")
    assert "GameActions" not in dp.available_groups()
