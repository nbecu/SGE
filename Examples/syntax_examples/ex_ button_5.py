import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from mainClasses.SGSGE import *
import random

monApp = QtWidgets.QApplication([])


myModel = SGModel(550, 250)

   

# myModel.newButton((lambda: print(10)),'Click me',(200,100),border_size=4, border_radius=10, min_width=200, min_height=70,background_color='yellow',background_image='icon/settings.png')
# myModel.newButton((lambda: print(10)),'Click me',(50,100),border_color= 'red', border_style='dashed',font_weight='bold' )
# myModel.newButton((lambda: print(10)),'Click me',(50,50),border_color= 'red', border_style='dashed',font_size=20 ) #font_family='Helvetica'
 #font_family='Helvetica'

myModel.newButton((lambda: button2Clicked()),'Click me 3',(70,80),
                  background_color='pink',
                  font_family='Times New Roman',
                  font_weight='bold',
                  text_color='magenta')
myModel.newButton((lambda: button2Clicked()),'Click me 2',(150,110),
                border_color='green',
                padding=10,
                border_size=3,
                border_radius=10,
                background_color='yellow',
                hover_text_color='red',
                hover_background_color='blue'
                  )
myModel.newButton((lambda: button2Clicked()),'Click me 2',(70,140))

def button2Clicked():
    print(20)



myModel.launch()
sys.exit(monApp.exec_())

