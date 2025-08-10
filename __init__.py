import sys
from pathlib import Path

# Auto-configure Python path so front-end examples can simply `from SGE import *`
root = Path(__file__).parent
sys.path.insert(0, str(root))

from mainClasses.SGSGE import *
