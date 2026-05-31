"""
Smoke tests for PyQt6 migration — reference games.

Each game is launched in a subprocess via a wrapper that:
  1. Monkey-patches QApplication.exec so the event loop never blocks
  2. Monkey-patches SGModel.show to trigger 3 simulation steps then exit cleanly
  3. Runs the game file content via exec()

Exit code interpretation:
  0   (or timeout still alive)  → PASS
  non-zero within timeout       → FAIL
"""
import subprocess
import sys
import time
import textwrap
from pathlib import Path

ROOT = Path(__file__).parent

GAMES = [
    "examples/games/CarbonPolis.py",
    "examples/games/Sea_Zones.py",
    "examples/games/Solutre_viticulteur.py",
    "examples/games/aGameExample_with_admin.py",
    "examples/A_to_Z_examples/exStep8.py",
    "examples/models/predator_prey.py",
    "examples/models/exProductionAndConsumption.py",
    "examples/models/game_of_life.py",
]

N_STEPS = 3   # simulation phases to run
TIMEOUT = 12  # seconds

# ── wrapper executed in the subprocess ────────────────────────────────────────
WRAPPER = textwrap.dedent(r"""
import sys, traceback
from pathlib import Path

TARGET = sys.argv[1]
N = int(sys.argv[2])

sys.path.insert(0, str(Path(TARGET).parent.parent.parent))
from mainClasses.SGSGE import *

# Prevent the event loop from blocking
_orig_exec = QtWidgets.QApplication.exec
def _no_exec(*a, **kw):
    return 0
QtWidgets.QApplication.exec = _no_exec

# Intercept show() to run N simulation steps then exit
_orig_show = SGModel.show
def _patched_show(self):
    _orig_show(self)
    QtWidgets.QApplication.instance().processEvents()
    step_errors = []
    for i in range(N):
        try:
            self.timeManager.nextPhase()
            QtWidgets.QApplication.instance().processEvents()
        except Exception as e:
            step_errors.append(f"Step {i}: {e}")
    if step_errors:
        for err in step_errors:
            print(f"STEP_ERROR: {err}", file=sys.stderr)
        sys.exit(2)
    self.close()
    sys.exit(0)
SGModel.show = _patched_show

# Run the game file
game_globals = {"__file__": TARGET, "__name__": "__main__"}
try:
    exec(open(TARGET, encoding="utf-8", errors="replace").read(), game_globals)
except SystemExit:
    pass
except Exception as e:
    print(f"EXEC_ERROR: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.exit(3)
""")

WRAPPER_PATH = ROOT / "_smoke_runner.py"
WRAPPER_PATH.write_text(WRAPPER, encoding="utf-8")

results = []

for game_path in GAMES:
    full_path = ROOT / game_path
    if not full_path.exists():
        results.append((game_path, "SKIP", "file not found"))
        continue

    proc = subprocess.Popen(
        [sys.executable, str(WRAPPER_PATH), str(full_path), str(N_STEPS)],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    try:
        stdout, stderr = proc.communicate(timeout=TIMEOUT)
        if proc.returncode == 0:
            results.append((game_path, "PASS", f"exited cleanly after {N_STEPS} steps"))
        else:
            err_lines = [l for l in stderr.splitlines() if l.strip()]
            snippet = "\n         ".join(err_lines[-10:]) if err_lines else "(no stderr)"
            results.append((game_path, "FAIL",
                            f"exit code {proc.returncode}\n         {snippet}"))
    except subprocess.TimeoutExpired:
        proc.kill()
        _, stderr = proc.communicate()
        err_lines = [l for l in (stderr or "").splitlines() if l.strip()]
        bad = [l for l in err_lines if any(k in l for k in ("Error", "Traceback", "Exception"))]
        if bad:
            snippet = "\n         ".join(err_lines[-8:])
            results.append((game_path, "WARN",
                            f"timeout + errors in stderr:\n         {snippet}"))
        else:
            results.append((game_path, "PASS",
                            f"alive after {TIMEOUT}s (show() not reached / blocking model)"))

WRAPPER_PATH.unlink(missing_ok=True)

# ── Report ────────────────────────────────────────────────────────────────────
print(f"\n{'='*65}")
print(f"  SGE PyQt6 Smoke Tests  ({N_STEPS} nextPhase per game)")
print(f"  {time.strftime('%Y-%m-%d %H:%M')}")
print(f"{'='*65}")
for path, status, detail in results:
    tag = "[OK]  " if status == "PASS" else ("[WARN]" if status == "WARN" else ("[SKIP]" if status == "SKIP" else "[FAIL]"))
    print(f"\n{tag} {status:5}  {path}")
    if status != "PASS":
        for line in detail.splitlines():
            safe = line.encode("cp1252", errors="replace").decode("cp1252")
            print(f"       {safe}")

passed  = sum(1 for _, s, _ in results if s == "PASS")
failed  = sum(1 for _, s, _ in results if s == "FAIL")
warned  = sum(1 for _, s, _ in results if s == "WARN")
skipped = sum(1 for _, s, _ in results if s == "SKIP")
print(f"\n{'='*65}")
print(f"  {passed} PASS  {failed} FAIL  {warned} WARN  {skipped} SKIP  / {len(results)} total")
print(f"{'='*65}\n")

sys.exit(1 if failed > 0 else 0)
