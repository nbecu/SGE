import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test simple pour vérifier que les imports fonctionnent
print("Testing imports...")

try:
    from mainClasses.SGModel import SGModel
    print("✓ SGModel import successful")
except Exception as e:
    print(f"✗ SGModel import failed: {e}")

try:
    from mainClasses.SGAdminPlayer import SGAdminPlayer
    print("✓ SGAdminPlayer import successful")
except Exception as e:
    print(f"✗ SGAdminPlayer import failed: {e}")

try:
    from PyQt5 import QtWidgets
    print("✓ PyQt5 import successful")
except Exception as e:
    print(f"✗ PyQt5 import failed: {e}")

print("Import test completed.")
