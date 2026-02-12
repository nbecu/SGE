"""
SGE global parameters.

Central place for SGE configuration values. Used by SGModel and other mainClasses.
Modify these values to change default behaviour (e.g. simulation replay capacity).
"""

# Maximum number of simulation snapshots kept in memory for "Save whole simulation" / replay.
# When exceeded, only the last SIMULATION_SNAPSHOTS_MAX states are retained (sliding window).
SIMULATION_SNAPSHOTS_MAX = 10000

# Number of recovery state files to keep on disk (rotation). When exceeded, oldest is removed.
RECOVERY_STATES_MAX = 3

# Optional: dict form for code that prefers key-based access or future loading from file.
SGE_PARAMETERS = {
    "simulation_snapshots_max": SIMULATION_SNAPSHOTS_MAX,
    "recovery_states_max": RECOVERY_STATES_MAX,
}
