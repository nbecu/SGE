import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt5 import QtWidgets
from mainClasses.SGModel import SGModel
from examples.A_to_Z_examples.exStep3_2 import ExStep2_4  

@pytest.fixture(scope="module")
def app():
    return QtWidgets.QApplication([])

def test_exStep2_4_execution():
    ex_step = ExStep2_4()
    try:
        app = ex_step.run()
        app.close()  #`close()` ne permet pas de fermer la fenêtre
        # possible que  l'instruction soit    QApplication.quit()
    except Exception as e:
        pytest.fail(f"ExStep2_4 a échoué à l'exécution : {str(e)}")
    assert True
    
