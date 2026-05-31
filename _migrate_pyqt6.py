"""
Script de migration PyQt5 → PyQt6 pour mainClasses/.
Passe 1 : remplacements purement mécaniques.
"""
import re
from pathlib import Path

ROOT = Path(__file__).parent
TARGET_DIRS = [ROOT / "mainClasses"]

REPLACEMENTS = [
    # Imports
    (r"from PyQt5\.", "from PyQt6."),
    (r"import PyQt5\.", "import PyQt6."),
    (r"from PyQt5 import", "from PyQt6 import"),
    # exec_() → exec()
    (r"\.exec_\(\)", ".exec()"),
    # Matplotlib backend
    (r"backend_qt5agg", "backend_qtagg"),
]

def migrate_file(path: Path) -> tuple[bool, list[str]]:
    original = path.read_text(encoding="utf-8", errors="replace")
    modified = original
    changes = []
    for pattern, replacement in REPLACEMENTS:
        new = re.sub(pattern, replacement, modified)
        if new != modified:
            count = len(re.findall(pattern, modified))
            changes.append(f"  {pattern!r} → {replacement!r}  ({count}x)")
            modified = new
    if modified != original:
        path.write_text(modified, encoding="utf-8")
        return True, changes
    return False, []

changed_files = []
for target_dir in TARGET_DIRS:
    for py_file in sorted(target_dir.rglob("*.py")):
        # Skip already-migrated files
        if py_file.name in ("SGSGE.py", "SGExtensions.py"):
            continue
        changed, details = migrate_file(py_file)
        if changed:
            changed_files.append((py_file.relative_to(ROOT), details))

print(f"\n{'='*60}")
print(f"Files modified: {len(changed_files)}")
print(f"{'='*60}")
for f, details in changed_files:
    print(f"\n{f}")
    for d in details:
        print(d)
