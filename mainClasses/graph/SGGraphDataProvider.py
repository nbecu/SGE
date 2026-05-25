class SGGraphDataProvider:
    """
    Loads simulation data from the dataRecorder and exposes:
      - the raw data lists (entities, simVars, players, gameActions)
      - the catalogue of available indicator keys for a given graph type
      - a helper to detect "flat" indicators (no value variation)

    This class owns all data-access logic previously scattered across
    SGGraphController.__init__, update_chart, and generate_and_add_indicators_menu.
    """

    QUANTI_STATS = ["mean", "sum", "min", "max", "stdev"]

    def __init__(self, model, graph_type):
        self.model = model
        self.graph_type = graph_type
        self._parent_attrib_key = (
            "quantiAttributes" if graph_type in ("linear", "hist") else "qualiAttributes"
        )
        self.reload()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def reload(self):
        dr = self.model.dataRecorder
        self.data_entities    = dr.getStats_ofEntities()
        self.data_sim_vars    = dr.getStepsData_ofSimVariables()
        self.data_players     = dr.getStepsData_ofPlayers()
        self.data_game_actions = dr.getStepsData_ofGameActions()

    def all_quantitative(self):
        return self.data_entities + self.data_sim_vars + self.data_players + self.data_game_actions

    def all_qualitative(self):
        return self.data_entities

    # ------------------------------------------------------------------
    # Indicator catalogue  (returns flat list of key strings)
    # ------------------------------------------------------------------

    def available_indicator_keys(self):
        """Return all indicator keys appropriate for the current graph type."""
        if self.graph_type == "linear":
            return self._keys_linear()
        else:
            return self._keys_categorical()

    def _keys_linear(self):
        keys = []

        # Entities
        entity_names = sorted({
            e["name"] for e in self.data_entities
            if "name" in e and not isinstance(e["name"], dict)
        })
        for entity in entity_names:
            keys.append(f"entity-:{entity}-:population")
            ent_def_attrs = sorted({
                attr
                for e in self.data_entities
                for attr in e.get("entDefAttributes", {})
                if e["name"] == entity
            })
            for attr in ent_def_attrs:
                keys.append(f"entity-:{entity}-:{attr}")
            quanti_attrs = sorted({
                attr
                for e in self.data_entities
                for attr in e.get("quantiAttributes", {})
                if e["name"] == entity
            })
            for attr in quanti_attrs:
                for stat in self.QUANTI_STATS:
                    keys.append(f"entity-:{entity}-:{attr}-:{stat}")

        # Players
        player_names = sorted({
            e["playerName"] for e in self.data_players
            if "playerName" in e and not isinstance(e["playerName"], dict)
        })
        for player in player_names:
            player_attrs = sorted({
                attr
                for e in self.data_players
                for attr in e.get("dictAttributes", {})
                if e["playerName"] == player
            })
            for attr in player_attrs:
                keys.append(f"player-:{player}-:{attr}")

        # SimVariables
        sim_var_names = sorted(set(
            e["simVarName"] for e in self.data_sim_vars
        ))
        for sv in sim_var_names:
            keys.append(f"simVariable-:{sv}")

        # Game actions
        action_types = sorted(set(
            action["action_type"]
            for e in self.data_game_actions
            for action in e.get("actions_performed", [])
        ))
        for at in action_types:
            keys.append(f"gameActions-:{at}")

        return keys

    def _keys_categorical(self):
        keys = []
        entity_names = sorted({
            e["name"] for e in self.data_entities
            if "name" in e
            and not isinstance(e["name"], dict)
            and isinstance(e.get(self._parent_attrib_key), dict)
            and e[self._parent_attrib_key]
        })
        for entity in entity_names:
            attrs = sorted({
                attr
                for e in self.data_entities
                for attr in e.get(self._parent_attrib_key, {})
                if e.get("name") == entity
                and isinstance(e[self._parent_attrib_key].get(attr), dict)
            })
            for attr in attrs:
                keys.append(f"entity-:{entity}-:{attr}")
        return keys

    # ------------------------------------------------------------------
    # Group / category helpers
    # ------------------------------------------------------------------

    def available_groups(self):
        """
        Return ordered list of group filter labels based on what data is present.
        Always starts with 'All'.
        'Entities' is included if any entities exist, followed by whichever of
        'Cells', 'Agents', 'Tiles' have data (using the 'category' field already
        present in each data_entities entry).
        'SimVars', 'Players', 'GameActions' appended if those datasets are non-empty.
        """
        groups = ["All"]
        cats_present = {
            e["category"]
            for e in self.data_entities
            if "category" in e and not isinstance(e.get("name"), dict)
        }
        if self.data_entities:
            groups.append("Entities")
        for cat in ("Cell", "Agent", "Tile"):
            if cat in cats_present:
                groups.append(cat + "s")   # "Cells", "Agents", "Tiles"

        if self.data_sim_vars:
            groups.append("SimVars")
        if self.data_players:
            groups.append("Players")
        if any(
            action
            for e in self.data_game_actions
            for action in e.get("actions_performed", [])
        ):
            groups.append("GameActions")

        return groups

    # ------------------------------------------------------------------
    # Flat-indicator detection
    # ------------------------------------------------------------------

    def is_flat(self, key):
        """
        Return True if the indicator identified by *key* has never changed
        across all recorded rounds (all values are identical).
        Only meaningful for linear/hist graphs (scalar values).
        Returns False for categorical graph types (pie, stackplot).
        """
        if self.graph_type not in ("linear", "hist"):
            return False
        from .SGIndicatorSpec import SGIndicatorSpec
        spec = SGIndicatorSpec(key, is_quantitative=True)
        values = spec.get_data(self.all_quantitative())
        return len(set(values)) <= 1

    # ------------------------------------------------------------------
    # Time-axis helpers (moved from SGGraphController)
    # ------------------------------------------------------------------

    def compute_x_axis(self, x_scale_option, specified_phase=None):
        """
        Return (xValue list, nbRoundsWithLastPhase) for the given x-axis option.
        x_scale_option: 'per round' | 'per step' | 'specified phase'
        """
        data = self.data_entities
        if not data:
            return [], 0

        rounds = {e["round"] for e in data}
        nb_rounds = max(rounds)
        nb_phases = self.model.timeManager.numberOfPhases()
        phase_of_last_round = max(
            e["phase"] for e in data if e["round"] == nb_rounds
        )

        if x_scale_option in ("per round", "specified phase") or (
            x_scale_option == "per step" and nb_phases == 1
        ):
            x_value = (
                list(rounds)
                if phase_of_last_round == nb_phases
                else list(rounds)[:-1]
            )
            nb_rounds_complete = (
                nb_rounds if phase_of_last_round == nb_phases else nb_rounds - 1
            )
        elif x_scale_option == "per step":
            nb_rounds_complete = (
                nb_rounds if phase_of_last_round == nb_phases else nb_rounds - 1
            )
            x_value = [0] + list(range(1, nb_rounds_complete * nb_phases + 1))
            if phase_of_last_round != nb_phases:
                x_value += [
                    x_value[-1] + i for i in range(1, phase_of_last_round + 1)
                ]
        else:
            x_value = list(rounds)
            nb_rounds_complete = nb_rounds

        return x_value, nb_rounds_complete

    def nb_phases(self):
        return self.model.timeManager.numberOfPhases()

    def current_round_phase(self):
        tm = self.model.timeManager
        return tm.currentRoundNumber, tm.currentPhaseNumber
