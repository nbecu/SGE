class SGIndicatorSpec:
    """
    Represents a single indicator selected in a graph panel.

    Parses the internal key format used by the graph system:
        "entity-:Wolf-:population"
        "entity-:Wolf-:age-:mean"
        "simVariable-:score"
        "player-:Alice-:energy"
        "gameActions-:ActionType"

    The key format is produced by SGGraphDataProvider and consumed here.
    """

    def __init__(self, menu_indicator_spec, is_quantitative=True):
        self.key = menu_indicator_spec
        self.component, self.indicator_type, self.indicator = self._parse(
            menu_indicator_spec, is_quantitative
        )

    def _parse(self, spec, is_quantitative):
        if "entity" in spec:
            component = tuple(spec.split("-:")[:2])
            if "population" in spec:
                indicator_type = "population"
                indicator = "population"
            elif len(spec.split("-:")) == 3:
                indicator_type = "entDefAttributes"
                indicator = spec.split("-:")[-1]
            else:
                indicator_type = "quantiAttributes" if is_quantitative else "qualiAttributes"
                indicator = tuple(spec.split("-:")[-2:])
        elif "simVariable" in spec:
            component = "simVariable"
            indicator_type = None
            indicator = spec.split("-:")[-1]
        elif "player" in spec:
            component = tuple(spec.split("-:")[:2])
            indicator_type = "dictAttributes"
            indicator = spec.split("-:")[-1]
        elif "gameActions" in spec:
            component = "gameActions"
            indicator_type = "actions_performed"
            indicator = spec.split("-:")[-1]
        else:
            component = spec
            indicator_type = None
            indicator = spec
        return component, indicator_type, indicator

    def get_data(self, data_at_step):
        if isinstance(self.component, tuple) and self.component[0] == "entity":
            if self.indicator_type == "population":
                return [e["population"] for e in data_at_step
                        if "category" in e and e["name"] == self.component[1]]
            elif self.indicator_type == "entDefAttributes":
                return [e[self.indicator_type][self.indicator] for e in data_at_step
                        if "category" in e and e["name"] == self.component[1]]
            elif self.indicator_type in ("quantiAttributes", "qualiAttributes"):
                return [e[self.indicator_type][self.indicator[0]][self.indicator[1]]
                        for e in data_at_step
                        if "category" in e and e["name"] == self.component[1]]
        elif self.component == "simVariable":
            return [e["value"] for e in data_at_step
                    if "simVarName" in e and e["simVarName"] == self.indicator]
        elif isinstance(self.component, tuple) and self.component[0] == "player":
            return [e[self.indicator_type][self.indicator] for e in data_at_step
                    if "playerName" in e and e["playerName"] == self.component[1]]
        elif self.component == "gameActions":
            return [
                action["usage_count"]
                for e in data_at_step
                for action in e.get("actions_performed", [])
                if action["action_type"] == self.indicator
            ]
        return []

    def get_label(self):
        if isinstance(self.component, tuple) and self.component[0] == "entity":
            if self.indicator_type == "population":
                return f"{self.component[1]} - Population"
            elif self.indicator_type == "entDefAttributes":
                return f"{self.component[1]} - {self.indicator}"
            elif self.indicator_type in ("quantiAttributes", "qualiAttributes"):
                return f"{self.component[1]} - {self.indicator[1]} of {self.indicator[0]}"
        elif self.component == "simVariable":
            return self.indicator
        elif isinstance(self.component, tuple) and self.component[0] == "player":
            return f"{self.component[1]} - {self.indicator}"
        elif self.component == "gameActions":
            return self.indicator
        return str(self.key)

    def get_line_style(self):
        if self.indicator_type == "quantiAttributes":
            styles = {"mean": "solid", "max": "dashed", "min": "dashed",
                      "stdev": "dotted", "sum": "dashdot"}
            return styles.get(self.indicator[1], "solid")
        return "solid"

    def get_display_name(self):
        """Human-readable name for the selector panel."""
        parts = self.key.split("-:")
        if "entity" in self.key:
            entity = parts[1]
            if "population" in self.key:
                return f"{entity} · population"
            elif len(parts) == 3:
                return f"{entity} · {parts[2]}"
            else:
                return f"{entity} · {parts[2]} ({parts[3]})"
        elif "simVariable" in self.key:
            return f"SimVar · {parts[-1]}"
        elif "player" in self.key:
            return f"Player {parts[1]} · {parts[-1]}"
        elif "gameActions" in self.key:
            return f"Action · {parts[-1]}"
        return self.key
