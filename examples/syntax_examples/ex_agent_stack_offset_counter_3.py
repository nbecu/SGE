import sys
from pathlib import Path
import random
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *

monApp = QtWidgets.QApplication([])

myModel = SGModel(700, 450, windowTitle="Stack offset and counter demo (dynamic)")

# Create a small grid
Cells = myModel.newCellsOnGrid(2, 2, "square", size=120, gap=6)

# Agent type with stack offset and stack counter
Agent = myModel.newAgentType(
    "Agent",
    "squareAgent",
    defaultSize=40,
    defaultColor=Qt.lightBlue,
    locationInEntity="topRight",
    stackOffset=(-22, 14),
    stackCounter={"format": "{n}", "min_count": 2, "position": "center"}
)

# Load random images from ./images (same as ex_image_on_entities.py)
image_paths = listImagePaths([Path(__file__).parent / "images", "./images"])

def get_random_pixmap():
    if not image_paths:
        return None
    return QPixmap(str(random.choice(image_paths)))

# Seed some agents to show static stacking (random images)
for _ in range(3):
    Agent.newAgentAtCoords(x=1, y=1, image=get_random_pixmap())

## ---------------------------------------------------------------------------
## Admin control panel and create action with random images
admin_player = myModel.getAdminPlayer()

create_action = myModel.newCreateAction(
    Agent,
    uses_per_round="infinite",
    feedbacks=[lambda cell: cell.getYoungestAgent().setImage(get_random_pixmap())],
    label="Create Agent (random image)",
    action_controler={"controlPanel": True}
)
admin_player.addGameAction(create_action)
# ---------------------------------------------------------------------------

myModel.displayAdminControlPanel()


myModel.launch()

sys.exit(monApp.exec())
