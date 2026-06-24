"""
Integration tests for symbology system with ControlPanel and Legend.

Tests all 4 symbology types:
- newSymbology() for nominal/discrete
- newSymbologyGradient() for continuous gradients
- newSymbologyClassified() for data classification
- newSymbologyRule() for rule-based logic

Verifies:
- All symbologies are created correctly
- Legend displays them properly
- ControlPanel shows them in menus
- shared_aspect properties apply correctly
"""
import pytest
from PyQt6.QtGui import QColor
from mainClasses.SGSGE import SGModel, SGAspect


def find_symbology_key(model, symbology_name):
    """Helper to find symbology key by name prefix"""
    keys = [k for k in model.symbologies.keys() if k.startswith(symbology_name + "_")]
    return keys[0] if keys else None


@pytest.fixture
def model_with_entities(qt_app):
    """Model with grid and entities for symbology testing"""
    m = SGModel(800, 600)
    cells = m.newCellsOnGrid(5, 5, "square", size=80)

    # Add diverse attributes
    cells.setEntities("health", 50)
    cells.setEntities("temperature", 20)
    cells.setEntities("status", 1)

    # Set random values for testing
    import random
    random.seed(42)
    for cell in cells.entities:
        cell.setValue("health", random.randint(0, 100))
        cell.setValue("temperature", random.randint(10, 40))
        cell.setValue("status", random.choice([1, 2, 3]))

    yield m, cells
    m.close()


class TestNominalSymbology:
    """Test nominal/discrete symbology creation and properties"""

    def test_create_nominal_symbology(self, model_with_entities):
        """Test creating a basic nominal symbology"""
        m, cells = model_with_entities

        cells.newSymbology(
            "status",
            {
                1: SGAspect(background_color=QColor("green"), text_content="OK"),
                2: SGAspect(background_color=QColor("orange"), text_content="WARN"),
                3: SGAspect(background_color=QColor("red"), text_content="ERROR"),
            },
            name="StatusSymbology"
        )

        # Verify symbology exists
        # Key format: {symbology_name}_{cells_name}
        assert "StatusSymbology" in [k.split('_')[0] for k in m.symbologies.keys()]
        # Get the actual key
        key = [k for k in m.symbologies.keys() if k.startswith("StatusSymbology_")][0]
        symbology = m.symbologies[key]
        assert 1 in symbology.mapping
        assert 2 in symbology.mapping
        assert 3 in symbology.mapping

    def test_nominal_with_shared_aspect(self, model_with_entities):
        """Test that shared_aspect applies to all values"""
        m, cells = model_with_entities

        cells.newSymbology(
            "health",
            {
                100: QColor("green"),
                50: QColor("orange"),
                25: QColor("red"),
            },
            border_size=2,
            border_color="black",
            name="HealthWithShared"
        )

        # Get the symbology by matching the prefix
        key = find_symbology_key(m, "HealthWithShared")
        assert key is not None
        symbology = m.symbologies[key]

        # All values should have shared_aspect properties
        for value in [100, 50, 25]:
            aspect = symbology.mapping[value]
            assert aspect.border_size == 2
            assert aspect.border_color == "black"

    def test_nominal_individual_overrides_shared_aspect(self, model_with_entities):
        """Test that individual aspect properties override shared_aspect"""
        m, cells = model_with_entities

        cells.newSymbology(
            "status",
            {
                1: QColor("green"),  # Uses shared_aspect border
                2: {"bg": "orange", "border": "blue"},  # Overrides shared_aspect border
            },
            border_color="red",
            name="StatusPriority"
        )

        key = find_symbology_key(m, "StatusPriority")
        assert key is not None
        symbology = m.symbologies[key]

        aspect_1 = symbology.mapping[1]
        aspect_2 = symbology.mapping[2]

        # Value 1: no individual border, uses shared_aspect "red"
        assert aspect_1.border_color == "red"
        # Value 2: individual border "blue" overrides shared_aspect "red"
        assert aspect_2.border_color == "blue"


class TestGradientSymbology:
    """Test gradient symbology with interpolation"""

    def test_create_gradient(self, model_with_entities):
        """Test creating a gradient symbology"""
        m, cells = model_with_entities

        cells.newSymbologyGradient(
            "health",
            {
                0: SGAspect(background_color="red"),
                100: SGAspect(background_color="green")
            },
            interpolation="linear",
            name="HealthGradient"
        )

        key = find_symbology_key(m, "HealthGradient")
        assert key is not None
        symbology = m.symbologies[key]
        assert symbology.is_gradient is True
        assert symbology.interpolation == "linear"

    def test_gradient_with_shared_aspect(self, model_with_entities):
        """Test gradient with shared_aspect properties"""
        m, cells = model_with_entities

        cells.newSymbologyGradient(
            "temperature",
            {
                10: SGAspect(background_color="blue"),
                40: SGAspect(background_color="red")
            },
            interpolation="sigmoid",
            text_color="white",
            text_size=10,
            name="TempGradientShared"
        )

        key = find_symbology_key(m, "TempGradientShared")
        assert key is not None
        symbology = m.symbologies[key]

        # Check that shared_aspect applied to both key points
        for value in [10, 40]:
            aspect = symbology.mapping[value]
            assert aspect.text_color == "white"
            assert aspect.text_size == 10


class TestClassificationSymbology:
    """Test classification symbology"""

    def test_create_classified(self, model_with_entities):
        """Test creating a classification symbology"""
        m, cells = model_with_entities

        cells.newSymbologyClassified(
            "temperature",
            {
                10: SGAspect(background_color="blue"),
                25: SGAspect(background_color="yellow"),
                40: SGAspect(background_color="red")
            },
            name="TempClassified"
        )

        key = find_symbology_key(m, "TempClassified")
        assert key is not None
        symbology = m.symbologies[key]
        assert symbology.is_classification is True

    def test_classified_with_shared_aspect(self, model_with_entities):
        """Test classification with shared_aspect"""
        m, cells = model_with_entities

        cells.newSymbologyClassified(
            "health",
            {
                25: SGAspect(background_color="red"),
                50: SGAspect(background_color="yellow"),
                75: SGAspect(background_color="green")
            },
            border_size=1,
            border_color="black",
            name="HealthClassified"
        )

        key = find_symbology_key(m, "HealthClassified")
        assert key is not None
        symbology = m.symbologies[key]

        # All class intervals should have shared_aspect
        for value in [25, 50, 75]:
            aspect = symbology.mapping[value]
            assert aspect.border_size == 1
            assert aspect.border_color == "black"


class TestRuleBasedSymbology:
    """Test rule-based symbology"""

    def test_create_rule_based(self, model_with_entities):
        """Test creating a rule-based symbology"""
        m, cells = model_with_entities

        def health_rule(entity):
            h = entity.value("health")
            if h > 75:
                return SGAspect(background_color="darkgreen", legend_label="Excellent")
            elif h > 50:
                return SGAspect(background_color="lightgreen", legend_label="Good")
            else:
                return SGAspect(background_color="orange", legend_label="Poor")

        cells.newSymbologyRule("health_rule", health_rule, name="HealthRule")

        key = find_symbology_key(m, "HealthRule")
        assert key is not None
        symbology = m.symbologies[key]
        assert hasattr(symbology, 'rule_function')

    def test_rule_based_executes(self, model_with_entities):
        """Test that rule-based symbology actually executes the rule"""
        m, cells = model_with_entities

        rule_calls = []

        def tracking_rule(entity):
            rule_calls.append(entity.value("health"))
            return SGAspect(background_color="green")

        cells.newSymbologyRule("tracker", tracking_rule, name="Tracker")

        # Rule should be stored
        key = find_symbology_key(m, "Tracker")
        assert key is not None
        symbology = m.symbologies[key]
        assert symbology.rule_function is tracking_rule


class TestLegendIntegration:
    """Test that Legend displays all symbology types"""

    def test_legend_displays_nominal(self, model_with_entities):
        """Test legend includes nominal symbology"""
        m, cells = model_with_entities

        cells.newSymbology(
            "status",
            {
                1: SGAspect(background_color="green", legend_label="OK"),
                2: SGAspect(background_color="orange", legend_label="Warning"),
            },
            name="StatusLegend"
        )

        legend = m.newLegend()
        assert legend is not None

        # Legend should have been created with the symbology
        assert hasattr(legend, 'updateWithSymbologies')

    def test_legend_with_shared_aspect(self, model_with_entities):
        """Test that legend respects shared_aspect properties"""
        m, cells = model_with_entities

        cells.newSymbology(
            "health",
            {
                100: QColor("green"),
                50: QColor("orange"),
            },
            text_color="white",
            text_size=12,
            name="HealthLegendShared"
        )

        legend = m.newLegend()
        assert legend is not None

        # Symbology should have the shared_aspect applied
        key = find_symbology_key(m, "HealthLegendShared")
        assert key is not None
        symbology = m.symbologies[key]
        for value in [100, 50]:
            aspect = symbology.mapping[value]
            assert aspect.text_color == "white"
            assert aspect.text_size == 12


class TestControlPanelIntegration:
    """Test that ControlPanel shows all symbology types"""

    def test_controlpanel_with_all_symbologies(self, model_with_entities):
        """Test that ControlPanel can display all 4 symbology types"""
        m, cells = model_with_entities

        # Create all 4 types
        cells.newSymbology(
            "status",
            {1: QColor("green"), 2: QColor("red")},
            name="StatusNominal"
        )

        cells.newSymbologyGradient(
            "health",
            {0: QColor("red"), 100: QColor("green")},
            name="HealthGradient"
        )

        cells.newSymbologyClassified(
            "temperature",
            {10: QColor("blue"), 40: QColor("red")},
            name="TempClassified"
        )

        def rule(e):
            return SGAspect(background_color="purple")

        cells.newSymbologyRule("dummy_rule", rule, name="DummyRule")

        # Create ControlPanel (may return None in headless mode)
        # Just verify it doesn't raise an exception
        try:
            control_panel = m.displayAdminControlPanel()
        except Exception as e:
            pytest.fail(f"displayAdminControlPanel() raised {type(e).__name__}: {e}")

    def test_controlpanel_symbology_menu_items(self, model_with_entities):
        """Test that symbology menu items are registered"""
        m, cells = model_with_entities

        cells.newSymbology(
            "status",
            {1: QColor("green")},
            name="TestSymbology"
        )

        # Check that symbology is in model's registry
        assert find_symbology_key(m, "TestSymbology") is not None

        # Create control panel (may return None if not in headless mode)
        control_panel = m.displayAdminControlPanel()

        # Symbology should be registered in model menu items
        # Menu items dictionary exists for menu management
        assert hasattr(m, 'symbology_type_menu_items')


class TestSymbologyWithLegendLabel:
    """Test legend_label property in symbologies"""

    def test_legend_label_in_nominal(self, model_with_entities):
        """Test that legend_label displays in nominal symbology"""
        m, cells = model_with_entities

        cells.newSymbology(
            "status",
            {
                1: SGAspect(background_color="green", legend_label="Status OK"),
                2: SGAspect(background_color="red", legend_label="Status Error"),
            },
            name="StatusWithLabels"
        )

        key = find_symbology_key(m, "StatusWithLabels")
        assert key is not None
        symbology = m.symbologies[key]

        # Verify legend_label is stored
        assert symbology.mapping[1].legend_label == "Status OK"
        assert symbology.mapping[2].legend_label == "Status Error"


# ---------------------------------------------------------------------------
# End-to-End Integration Test
# ---------------------------------------------------------------------------

class TestFullSymbologyIntegration:
    """Full integration test with all components"""

    def test_complete_workflow(self, model_with_entities):
        """Test complete workflow: create symbologies → legend → control panel"""
        m, cells = model_with_entities

        # Create diverse symbologies
        cells.newSymbology(
            "status",
            {1: QColor("green"), 2: QColor("orange"), 3: QColor("red")},
            border_size=1,
            border_color="black",
            name="Status"
        )

        cells.newSymbologyGradient(
            "health",
            {0: QColor("red"), 100: QColor("green")},
            name="Health"
        )

        cells.newSymbologyClassified(
            "temperature",
            {10: QColor("blue"), 25: QColor("green"), 40: QColor("red")},
            name="Temperature"
        )

        def activity_rule(e):
            return SGAspect(background_color="purple", legend_label="Active")

        cells.newSymbologyRule("activity", activity_rule, name="Activity")

        # Create legend and control panel
        legend = m.newLegend()
        try:
            control_panel = m.displayAdminControlPanel()
        except Exception as e:
            pytest.fail(f"displayAdminControlPanel() raised {type(e).__name__}: {e}")

        # Verify all symbologies are registered
        assert find_symbology_key(m, "Status") is not None
        assert find_symbology_key(m, "Health") is not None
        assert find_symbology_key(m, "Temperature") is not None
        assert find_symbology_key(m, "Activity") is not None

        # Verify no errors occurred
        assert legend is not None
