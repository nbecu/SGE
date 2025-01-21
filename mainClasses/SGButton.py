from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sqlalchemy import true
# from PyQt5.QtWidgets import QStyleFactory
# from mainClasses.SGGameSpace import SGGameSpace


class SGButton(QtWidgets.QWidget):
    def __init__(self, parent, method, text, 
                 background_color='white',
                 background_image=None,
                 border_size=1,
                 border_style='solid',
                 border_color='lightgray',
                 border_radius=4,
                 text_color=None,
                 font_family=None,
                 font_size=None,
                 font_weight=None,
                 min_width=None,
                 min_height=None,
                 padding=None,
                 hover_text_color= None,
                 hover_background_color= '#c6eff7',
                 hover_border_color= '#6bd8ed',
                 pressed_color=None,
                 disabled_color=None):
        super().__init__(parent)
        self.model = parent
        self.moveable = True
        self.isDisplay = True
        
        button = QtWidgets.QPushButton(text, self)
        from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
        if isinstance(method,SGAbstractAction):
            button.clicked.connect(lambda: method.perform_with(method.model))
        else:
            button.clicked.connect(lambda: method())
        
        
        aStyleSheet = "QPushButton {" + (';'.join(filter(None, [
            f"background-color: {background_color}",
            f"background-image: url({background_image})" if background_image is not None else None,
            f"border: {border_size}px {border_style} {border_color}" ,
            f"border-radius: {border_radius}px" ,
            f"color: {text_color}" if text_color is not None else None,
            f"font-family: {font_family}" if font_family is not None else None,
            f"font-size: {font_size}px" if font_size is not None else None,
            f"font-weight: {font_weight}" if font_weight is not None else None,
            f"min-width: {min_width}px" if min_width is not None else None,
            f"min-height: {min_height}px" if min_height is not None else None,
            f"padding: {padding}px" if padding is not None else None
        ])) ) + '} '
        aStyleSheet_hover = "QPushButton:hover {" + (';'.join(filter(None, [
            f"color: {hover_text_color}" if hover_text_color is not None else None,
            f"background-color: {hover_background_color}",
            f"border-color: {hover_border_color}"
        ])) ) + '} '

        aStyleSheet_suite = ';'.join(filter(None, [
            f"QPushButton:pressed {{ background-color: {pressed_color} }}" if pressed_color is not None else None,
            f"QPushButton:disabled {{ background-color: {disabled_color} }}" if disabled_color is not None else None
        ])) 
        aStyleSheet = aStyleSheet + aStyleSheet_hover+ aStyleSheet_suite
        button.setStyleSheet(aStyleSheet)
        """
        /* Fond */
        background-color: #4CAF50;
        background-image: url(image.png);
        
        /* Bordures */
        border: 2px solid #45a049;
        border-radius: 10px;
        
        /* Texte */
        color: white;
        font-family: Arial;
        font-size: 14px;
        font-weight: bold;
        
        /* Dimensions */
        min-width: 80px;
        min-height: 30px;
        padding: 6px;
        
        /* États */
        QPushButton:hover { background-color: #45a049; }
        QPushButton:pressed { background-color: #3d8b40; }
        QPushButton:disabled { background-color: #cccccc; }
        """

# Autres propriétés
        # button.setIcon(QIcon('icon/icon_linear.png'))        # Ajouter une icône
        # button.setIconSize(QSize(20, 20))        # Taille de l'icône
        # button.setFlat(True)                     # Bouton plat sans bordure

        # button.setStyleSheet("QPushButton:hover { background-color: #45a049; }")   #OK
        # button.setStyleSheet("QPushButton:pressed { background-color: #3d8b40; }")   #OK
        # button.setStyleSheet("background-color: yellow;border: 8px solid #45a049;")     #OK
        # button.setStyleSheet("background-color: yellow;border: 8px solid #45a049; ")     #OK
        # button.setStyleSheet("border: 5px dashed #45a049;")   #OK
        # button.setStyleSheet("background-image: url(icon/save.png);")   #OK
        # button.setStyleSheet("background-color: yellow;border: 3px solid #45a049;border-radius: 10px; ")     #OK
        # button.setStyleSheet("background-color: beige; color: magenta; ")     #OK

        """    Texte */\n         font-family: Arial;\n        font-size: 14px;\n        font-weight: bold; 
              /* Dimensions */\n        min-width: 80px;\n        min-height: 30px;\n        padding: 6px;\n       
                QPushButton:hover { background-color: #45a049; }\n        QPushButton:pressed { background-color: #3d8b40; }\n        QPushButton:disabled { background-color: #cccccc; }\n"""

        # # Build the complete stylesheet
        # complete_style = f"{backgroundColor_specs}{textStyle_specs}{borderStyle_specs}"
        # button.setStyleSheet(complete_style)
        # label.setFont(QFont('Arial', 18)) -> Other way to set the Font
        
        # ajust the size of the label according to its style font and border. Then redefine the size of the widget according to the size of the geometry of the label 
        button.adjustSize()   
        self.setMinimumSize(button.geometry().size())


class SGButton_1bis(QtWidgets.QWidget):
    def __init__(self, parent, method, text, 
                 background_color=None,
                 background_image=None,
                 border_size=None,
                 border_style=None,
                 border_color=None,
                 border_radius=None,
                 text_color=None,
                 font_family=None,
                 font_size=None,
                 font_weight=None,
                 min_width=None,
                 min_height=None,
                 padding=None,
                 hover_color=None,
                 pressed_color=None,
                 disabled_color=None):
        super().__init__(parent)
        self.model = parent
        self.moveable = True
        self.isDisplay = True
        
        button = QtWidgets.QPushButton(text, self)
        from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
        if isinstance(method,SGAbstractAction):
            button.clicked.connect(lambda: method.perform_with(method.model))
        else:
            button.clicked.connect(lambda: method())
        # Use default values if any border property is set but others are None
        includeBorder = False
        if any(x is not None for x in [border_size, border_style, border_color]):
            border_size = border_size or 1 #default value
            border_style = border_style or 'solid' #default value
            border_color = border_color or 'grey' #default value
            includeBorder = True

        aStyleSheet = ';'.join(filter(None, [
            f"background-color: {background_color}" if background_color is not None else None,
            f"background-image: url({background_image})" if background_image is not None else None,
            f"border: {border_size}px {border_style} {border_color}" if includeBorder else None,
            f"border-radius: {border_radius}px" if border_radius is not None else None,
            f"color: {text_color}" if text_color is not None else None,
            f"font-family: {font_family}" if font_family is not None else None,
            f"font-size: {font_size}px" if font_size is not None else None,
            f"font-weight: {font_weight}" if font_weight is not None else None,
            f"min-width: {min_width}px" if min_width is not None else None,
            f"min-height: {min_height}px" if min_height is not None else None,
            f"padding: {padding}px" if padding is not None else None,
            f"QPushButton:hover {{ background-color: {hover_color} }}" if hover_color is not None else None,
            f"QPushButton:pressed {{ background-color: {pressed_color} }}" if pressed_color is not None else None,
            f"QPushButton:disabled {{ background-color: {disabled_color} }}" if disabled_color is not None else None
        ])) + ';'
        button.setStyleSheet(aStyleSheet)
        """
        /* Fond */
        background-color: #4CAF50;
        background-image: url(image.png);
        
        /* Bordures */
        border: 2px solid #45a049;
        border-radius: 10px;
        
        /* Texte */
        color: white;
        font-family: Arial;
        font-size: 14px;
        font-weight: bold;
        
        /* Dimensions */
        min-width: 80px;
        min-height: 30px;
        padding: 6px;
        
        /* États */
        QPushButton:hover { background-color: #45a049; }
        QPushButton:pressed { background-color: #3d8b40; }
        QPushButton:disabled { background-color: #cccccc; }
        """

# Autres propriétés
        # button.setIcon(QIcon('icon/icon_linear.png'))        # Ajouter une icône
        # button.setIconSize(QSize(20, 20))        # Taille de l'icône
        # button.setFlat(True)                     # Bouton plat sans bordure

        # button.setStyleSheet("QPushButton:hover { background-color: #45a049; }")   #OK
        # button.setStyleSheet("QPushButton:pressed { background-color: #3d8b40; }")   #OK
        # button.setStyleSheet("background-color: yellow;border: 8px solid #45a049;")     #OK
        # button.setStyleSheet("background-color: yellow;border: 8px solid #45a049; ")     #OK
        # button.setStyleSheet("border: 5px dashed #45a049;")   #OK
        # button.setStyleSheet("background-image: url(icon/save.png);")   #OK
        # button.setStyleSheet("background-color: yellow;border: 3px solid #45a049;border-radius: 10px; ")     #OK
        # button.setStyleSheet("background-color: beige; color: magenta; ")     #OK

        """    Texte */\n         font-family: Arial;\n        font-size: 14px;\n        font-weight: bold; 
              /* Dimensions */\n        min-width: 80px;\n        min-height: 30px;\n        padding: 6px;\n       
                QPushButton:hover { background-color: #45a049; }\n        QPushButton:pressed { background-color: #3d8b40; }\n        QPushButton:disabled { background-color: #cccccc; }\n"""

        # # Build the complete stylesheet
        # complete_style = f"{backgroundColor_specs}{textStyle_specs}{borderStyle_specs}"
        # button.setStyleSheet(complete_style)
        # label.setFont(QFont('Arial', 18)) -> Other way to set the Font
        
        # ajust the size of the label according to its style font and border. Then redefine the size of the widget according to the size of the geometry of the label 
        button.adjustSize()   
        self.setMinimumSize(button.geometry().size())


class SGButton2(QtWidgets.QWidget):
    def __init__(self, parent, method, text, textStyle_specs="", borderStyle_specs="", backgroundColor_specs="", fixedWidth=None, fixedHeight=None):
        super().__init__(parent)
        self.model = parent
        self.moveable = True
        self.isDisplay = True
        
        button = QtWidgets.QPushButton(text, self)
        from mainClasses.gameAction.SGAbstractAction import SGAbstractAction
        if isinstance(method,SGAbstractAction):
            button.clicked.connect(lambda: method.perform_with(method.model))
        else:
            button.clicked.connect(lambda: method())

        if fixedWidth is not None:
            button.setFixedWidth(fixedWidth)
            button.setWordWrap(True)  # Allow line wrapping if the text is too long

        if fixedHeight is not None:
            button.setFixedHeight(fixedHeight)
       
        # Build the complete stylesheet
        complete_style = f"{backgroundColor_specs}{textStyle_specs}{borderStyle_specs}"
        # button.setStyleSheet(complete_style)
        # label.setFont(QFont('Arial', 18)) -> Other way to set the Font
        
        # ajust the size of the label according to its style font and border. Then redefine the size of the widget according to the size of the geometry of the label 
        button.adjustSize()   
        self.setMinimumSize(button.geometry().size())
 