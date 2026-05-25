"""
Unit tests for the graph data layer — SGIndicatorSpec and SGMultiGraphPanel.

No Qt or model required: all tests operate on pure Python objects.
"""
import pytest
from mainClasses.graph.SGIndicatorSpec import SGIndicatorSpec
from mainClasses.graph.SGMultiGraphWindow import SGMultiGraphPanel


# ===========================================================================
# SGIndicatorSpec — key parsing
# ===========================================================================

def test_parse_entity_population():
    spec = SGIndicatorSpec("entity-:Wolf-:population")
    assert spec.component == ("entity", "Wolf")
    assert spec.indicator_type == "population"
    assert spec.indicator == "population"


def test_parse_entity_simple_attr():
    # 3-part entity key → entDefAttributes
    spec = SGIndicatorSpec("entity-:Wolf-:age")
    assert spec.component == ("entity", "Wolf")
    assert spec.indicator_type == "entDefAttributes"
    assert spec.indicator == "age"


def test_parse_entity_quanti_stat():
    spec = SGIndicatorSpec("entity-:Wolf-:energy-:mean", is_quantitative=True)
    assert spec.component == ("entity", "Wolf")
    assert spec.indicator_type == "quantiAttributes"
    assert spec.indicator == ("energy", "mean")


def test_parse_entity_quali_attr():
    spec = SGIndicatorSpec("entity-:Sheep-:status-:adult", is_quantitative=False)
    assert spec.component == ("entity", "Sheep")
    assert spec.indicator_type == "qualiAttributes"
    assert spec.indicator == ("status", "adult")


def test_parse_simvar():
    spec = SGIndicatorSpec("simVariable-:Score")
    assert spec.component == "simVariable"
    assert spec.indicator_type is None
    assert spec.indicator == "Score"


def test_parse_player():
    spec = SGIndicatorSpec("player-:Alice-:energy")
    assert spec.component == ("player", "Alice")
    assert spec.indicator_type == "dictAttributes"
    assert spec.indicator == "energy"


def test_parse_gameaction():
    spec = SGIndicatorSpec("gameActions-:Build")
    assert spec.component == "gameActions"
    assert spec.indicator_type == "actions_performed"
    assert spec.indicator == "Build"


# ===========================================================================
# SGIndicatorSpec — get_label
# ===========================================================================

def test_label_entity_population():
    assert SGIndicatorSpec("entity-:Wolf-:population").get_label() == "Wolf - Population"


def test_label_entity_stat():
    label = SGIndicatorSpec("entity-:Wolf-:energy-:mean", is_quantitative=True).get_label()
    assert label == "Wolf - mean of energy"


def test_label_entity_simple_attr():
    label = SGIndicatorSpec("entity-:Wolf-:age").get_label()
    assert label == "Wolf - age"


def test_label_simvar():
    assert SGIndicatorSpec("simVariable-:Score").get_label() == "Score"


def test_label_player():
    assert SGIndicatorSpec("player-:Alice-:energy").get_label() == "Alice - energy"


# ===========================================================================
# SGIndicatorSpec — get_line_style
# ===========================================================================

@pytest.mark.parametrize("stat,expected", [
    ("mean",  "solid"),
    ("sum",   "dashdot"),
    ("max",   "dashed"),
    ("min",   "dashed"),
    ("stdev", "dotted"),
])
def test_line_style_quanti_stats(stat, expected):
    spec = SGIndicatorSpec(f"entity-:Wolf-:energy-:{stat}", is_quantitative=True)
    assert spec.get_line_style() == expected


def test_line_style_population_is_solid():
    # population is not quantiAttributes → default solid
    assert SGIndicatorSpec("entity-:Wolf-:population").get_line_style() == "solid"


def test_line_style_simvar_is_solid():
    assert SGIndicatorSpec("simVariable-:Score").get_line_style() == "solid"


# ===========================================================================
# SGIndicatorSpec — get_data
# ===========================================================================

_WOLF_POP_ENTRY   = {"category": "Agent", "name": "Wolf", "population": 5}
_WOLF_QUANTI_ENTRY = {
    "category": "Agent", "name": "Wolf",
    "quantiAttributes": {"energy": {"mean": 42.5, "max": 80.0}},
}
_SCORE_ENTRY = {"simVarName": "Score", "value": 10}
_SHEEP_POP_ENTRY  = {"category": "Agent", "name": "Sheep", "population": 12}


def test_get_data_population():
    spec = SGIndicatorSpec("entity-:Wolf-:population")
    assert spec.get_data([_WOLF_POP_ENTRY, _SHEEP_POP_ENTRY]) == [5]


def test_get_data_population_filters_by_name():
    spec = SGIndicatorSpec("entity-:Sheep-:population")
    assert spec.get_data([_WOLF_POP_ENTRY, _SHEEP_POP_ENTRY]) == [12]


def test_get_data_quanti_mean():
    spec = SGIndicatorSpec("entity-:Wolf-:energy-:mean", is_quantitative=True)
    assert spec.get_data([_WOLF_QUANTI_ENTRY]) == [42.5]


def test_get_data_quanti_max():
    spec = SGIndicatorSpec("entity-:Wolf-:energy-:max", is_quantitative=True)
    assert spec.get_data([_WOLF_QUANTI_ENTRY]) == [80.0]


def test_get_data_simvar():
    spec = SGIndicatorSpec("simVariable-:Score")
    assert spec.get_data([_SCORE_ENTRY, _WOLF_POP_ENTRY]) == [10]


def test_get_data_returns_empty_when_no_match():
    spec = SGIndicatorSpec("entity-:Tiger-:population")
    assert spec.get_data([_WOLF_POP_ENTRY, _SHEEP_POP_ENTRY]) == []


def test_get_data_multiple_rounds():
    entries = [
        {"category": "Agent", "name": "Wolf", "population": 5},
        {"category": "Agent", "name": "Wolf", "population": 8},
    ]
    spec = SGIndicatorSpec("entity-:Wolf-:population")
    assert spec.get_data(entries) == [5, 8]


# ===========================================================================
# SGMultiGraphPanel — _tuple_to_key
# ===========================================================================

def test_tuple_to_key_entity_3():
    assert SGMultiGraphPanel._tuple_to_key(("entity", "Wolf", "population")) == "entity-:Wolf-:population"


def test_tuple_to_key_entity_4():
    assert SGMultiGraphPanel._tuple_to_key(("entity", "Wolf", "energy", "mean")) == "entity-:Wolf-:energy-:mean"


def test_tuple_to_key_simvar():
    assert SGMultiGraphPanel._tuple_to_key(("simvar", "Score")) == "simVariable-:Score"


def test_tuple_to_key_player():
    assert SGMultiGraphPanel._tuple_to_key(("player", "Alice", "score")) == "player-:Alice-:score"


def test_tuple_to_key_gameaction():
    assert SGMultiGraphPanel._tuple_to_key(("gameaction", "Build")) == "gameActions-:Build"


def test_tuple_to_key_empty_returns_none():
    assert SGMultiGraphPanel._tuple_to_key(()) is None


def test_tuple_to_key_unknown_kind_returns_none():
    assert SGMultiGraphPanel._tuple_to_key(("unknown", "foo")) is None


# ===========================================================================
# SGMultiGraphPanel — x_axis mapping and validation
# ===========================================================================

def _make_panel(x_axis):
    return SGMultiGraphPanel("linear", [("entity", "Wolf", "population")], x_axis=x_axis)


def test_x_axis_default_is_per_round():
    panel = SGMultiGraphPanel("linear", [("entity", "Wolf", "population")])
    assert panel.x_axis == "per round"


def test_x_axis_rounds():
    assert _make_panel("Rounds").x_axis == "per round"


def test_x_axis_rounds_and_phases():
    assert _make_panel("Rounds & Phases").x_axis == "per step"


def test_x_axis_specified_phase():
    assert _make_panel("Specified phase").x_axis == "specified phase"


def test_x_axis_invalid_raises():
    with pytest.raises(ValueError, match="invalid x_axis"):
        _make_panel("Weekly")
