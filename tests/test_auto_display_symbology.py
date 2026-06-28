"""Test auto-display of first symbology per attribute."""
import pytest
from PyQt6.QtGui import QColor
from mainClasses.SGSGE import SGModel, SGAspect


@pytest.fixture
def model_with_grid(qt_app):
    """Model with a simple grid for testing"""
    m = SGModel(800, 600)
    cells = m.newCellsOnGrid(3, 3, "square", size=50)
    cells.setEntities("health", 100)

    yield m, cells
    m.close()


class TestAutoDisplaySymbology:
    """Test auto-display of first symbology per attribute"""

    def test_first_symbology_auto_displays(self, model_with_grid):
        """First symbology created for an attribute should auto-display"""
        m, cells = model_with_grid

        # Create first symbology for 'health' attribute
        cells.newSymbology(
            "health",
            {100: QColor("green"), 50: QColor("red")},
            name="HealthGreen"
        )

        # Verify it's automatically set as active
        active = m.active_symbologies_by_type.get(cells.name, set())
        assert "HealthGreen" in active, f"Expected HealthGreen to be active, got {active}"

    def test_second_symbology_does_not_auto_display(self, model_with_grid):
        """Second symbology created for same attribute should NOT auto-display"""
        m, cells = model_with_grid

        # Create first symbology
        cells.newSymbology(
            "health",
            {100: QColor("green"), 50: QColor("red")},
            name="HealthGreen"
        )

        # Create second symbology for same attribute
        cells.newSymbology(
            "health",
            {100: QColor("blue"), 50: QColor("orange")},
            name="HealthBlue"
        )

        # Only the FIRST should be active
        active = m.active_symbologies_by_type.get(cells.name, set())
        assert "HealthGreen" in active, "First symbology should still be active"
        assert "HealthBlue" not in active, "Second symbology should NOT be auto-displayed"

    def test_different_attributes_independent(self, model_with_grid):
        """First symbology for different attributes should independently auto-display"""
        m, cells = model_with_grid
        cells.setEntities("energy", 50)

        # Create first symbology for 'health'
        cells.newSymbology(
            "health",
            {100: QColor("green"), 50: QColor("red")},
            name="HealthSymbology"
        )

        # Create first symbology for 'energy' (different attribute)
        cells.newSymbology(
            "energy",
            {50: QColor("yellow"), 25: QColor("gray")},
            name="EnergySymbology"
        )

        # Both should be auto-displayed (first for each attribute)
        active = m.active_symbologies_by_type.get(cells.name, set())
        assert "HealthSymbology" in active, "Health's first symbology should be active"
        assert "EnergySymbology" in active, "Energy's first symbology should be active"

    def test_gradient_symbology_auto_displays(self, model_with_grid):
        """First gradient symbology should also auto-display"""
        m, cells = model_with_grid
        cells.setEntities("temperature", 20)

        # Create first gradient symbology
        cells.newSymbologyGradient(
            "temperature",
            {10: QColor("blue"), 30: QColor("red")},
            name="TempGradient"
        )

        # Verify it's automatically set as active
        active = m.active_symbologies_by_type.get(cells.name, set())
        assert "TempGradient" in active, f"Expected TempGradient to be active, got {active}"

    def test_classified_symbology_auto_displays(self, model_with_grid):
        """First classified symbology should also auto-display"""
        m, cells = model_with_grid
        cells.setEntities("income", 50000)

        # Create first classified symbology
        cells.newSymbologyClassified(
            "income",
            {
                0: QColor("red"),
                40000: QColor("yellow"),
                80000: QColor("green"),
                "__max_value__": 100000
            },
            name="IncomeClassified"
        )

        # Verify it's automatically set as active
        active = m.active_symbologies_by_type.get(cells.name, set())
        assert "IncomeClassified" in active, f"Expected IncomeClassified to be active, got {active}"
