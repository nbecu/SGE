"""
Tests for addEndGameCondition_onSimVar and getLastArrivedAgent.

addEndGameCondition_onSimVar: direct method on SGEndGameRule that takes a SimVar
instead of requiring the modeler to go through an Indicator.

getLastArrivedAgent: method on SGCell returning the most recently arrived agent.

Tests that call advance() are marked @pytest.mark.simulation (Qt event loop required).
Other tests create Qt objects but do not run simulation cycles.
"""
import pytest
from mainClasses.SGSGE import SGModel, Qt


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def advance(m, qt_app, n):
    """Call nextPhase n times, flushing Qt events between each call."""
    for _ in range(n):
        m.timeManager.nextPhase()
        qt_app.processEvents()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def model_with_grid(qt_app):
    m = SGModel(400, 300)
    cell_type = m.newCellsOnGrid(4, 4, "square", size=40, gap=2)
    yield m, cell_type
    m.close()


@pytest.fixture
def model_with_simvar(qt_app):
    m = SGModel(400, 300)
    sim_var = m.newSimVariable("score", 0, color=Qt.black)
    end_rule = m.newEndGameRule(numberRequired=1)
    yield m, sim_var, end_rule
    m.close()


# ---------------------------------------------------------------------------
# addEndGameCondition_onSimVar tests
# ---------------------------------------------------------------------------

class TestAddEndGameConditionOnSimVar:

    @pytest.mark.simulation
    def test_condition_not_met_below_threshold(self, model_with_simvar, qt_app):
        """Condition 'equal 10' not met when simVar is 0."""
        m, sim_var, end_rule = model_with_simvar
        end_rule.addEndGameCondition_onSimVar(sim_var, "equal", 10, name="Score == 10")
        m.newModelPhase(name="setup")
        advance(m, qt_app, 1)
        cond = end_rule.endGameConditions[0]
        assert cond.checkStatus is False

    @pytest.mark.simulation
    def test_condition_met_on_equal(self, model_with_simvar, qt_app):
        """Condition 'equal 10' met when simVar is incremented to 10."""
        m, sim_var, end_rule = model_with_simvar
        end_rule.addEndGameCondition_onSimVar(sim_var, "equal", 10, name="Score == 10")
        sim_var.incValue(10)
        m.newModelPhase(name="setup")
        advance(m, qt_app, 1)
        cond = end_rule.endGameConditions[0]
        assert cond.checkStatus is True

    @pytest.mark.simulation
    def test_condition_met_on_greater(self, model_with_simvar, qt_app):
        """Condition 'greater 5' met when simVar is incremented to 8."""
        m, sim_var, end_rule = model_with_simvar
        end_rule.addEndGameCondition_onSimVar(sim_var, "greater", 5, name="Score > 5")
        sim_var.incValue(8)
        m.newModelPhase(name="setup")
        advance(m, qt_app, 1)
        cond = end_rule.endGameConditions[0]
        assert cond.checkStatus is True

    @pytest.mark.simulation
    def test_condition_not_met_then_met(self, model_with_simvar, qt_app):
        """Condition starts unmet, then becomes met after simVar increases."""
        m, sim_var, end_rule = model_with_simvar
        end_rule.addEndGameCondition_onSimVar(sim_var, "greater or equal", 10, name="Score >= 10")
        m.newModelPhase(name="setup")
        advance(m, qt_app, 1)
        cond = end_rule.endGameConditions[0]
        assert cond.checkStatus is False
        sim_var.incValue(10)
        advance(m, qt_app, 1)
        assert cond.checkStatus is True

    def test_condition_registered_in_time_manager(self, model_with_simvar):
        """Condition is correctly registered in the time manager."""
        m, sim_var, end_rule = model_with_simvar
        end_rule.addEndGameCondition_onSimVar(sim_var, "less or equal", 100)
        assert len(m.timeManager.conditionOfEndGame) == 1

    @pytest.mark.simulation
    def test_condition_less(self, model_with_simvar, qt_app):
        """Condition 'less 5' met when simVar is 3."""
        m, sim_var, end_rule = model_with_simvar
        sim_var.incValue(3)
        end_rule.addEndGameCondition_onSimVar(sim_var, "less", 5, name="Score < 5")
        m.newModelPhase(name="setup")
        advance(m, qt_app, 1)
        cond = end_rule.endGameConditions[0]
        assert cond.checkStatus is True


# ---------------------------------------------------------------------------
# getLastArrivedAgent tests
# ---------------------------------------------------------------------------

class TestGetLastArrivedAgent:

    def test_empty_cell_returns_none(self, model_with_grid):
        """getLastArrivedAgent returns None on a cell with no agents."""
        _, cell_type = model_with_grid
        cell = cell_type.getCell(1, 1)
        assert cell.getLastArrivedAgent() is None

    @pytest.mark.simulation
    def test_single_agent_returns_it(self, model_with_grid, qt_app):
        """getLastArrivedAgent returns the single agent present."""
        m, cell_type = model_with_grid
        agent_type = m.newAgentType("Worker", "circleAgent")
        cell = cell_type.getCell(1, 1)
        agent = agent_type.newAgentOnCell(cell)
        assert cell.getLastArrivedAgent() is agent

    @pytest.mark.simulation
    def test_second_agent_is_last_arrived(self, model_with_grid, qt_app):
        """When two agents arrive on the same cell, the second one is last."""
        m, cell_type = model_with_grid
        agent_type = m.newAgentType("Worker", "circleAgent")
        cell = cell_type.getCell(1, 1)
        a1 = agent_type.newAgentOnCell(cell)
        a2 = agent_type.newAgentOnCell(cell)
        assert cell.getLastArrivedAgent() is a2

    @pytest.mark.simulation
    def test_last_arrived_after_move(self, model_with_grid, qt_app):
        """After an agent moves to a cell, it becomes the last arrived on that cell."""
        m, cell_type = model_with_grid
        agent_type = m.newAgentType("Worker", "circleAgent")
        cell_origin = cell_type.getCell(1, 1)
        cell_dest = cell_type.getCell(2, 1)
        a1 = agent_type.newAgentOnCell(cell_origin)
        a2 = agent_type.newAgentOnCell(cell_dest)
        # a1 moves to cell_dest — becomes last arrived there
        a1.moveTo(cell_dest)
        assert cell_dest.getLastArrivedAgent() is a1
