import pytest
from PyQt5 import QtWidgets
from mainClasses.SGModel import SGModel
from Examples.A_to_Z_examples.exStep2_4 import ExStep2_4  

@pytest.fixture(scope="module")
def app():
    return QtWidgets.QApplication([])

def test_exStep2_4_execution():
    ex_step = ExStep2_4()
    try:
        app = ex_step.run()
        app.close()  #`close()` ne permet pas de fermer la fenêtre
    except Exception as e:
        pytest.fail(f"ExStep2_4 a échoué à l'exécution : {str(e)}")
    assert True
    
