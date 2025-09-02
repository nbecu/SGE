from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMenu, QAction, QInputDialog, QMessageBox, QDialog, QLabel, QVBoxLayout, QToolTip
from PyQt5.QtGui import QCursor
from mainClasses.SGEntityView import SGEntityView
import random

class SGAgentView(SGEntityView):
    """
    View class for SGAgent - handles all UI and display logic for agents
    Separated from the model to enable Model-View architecture
    """
    
    def __init__(self, agent_model, parent=None):
        """
        Initialize the agent view
        
        Args:
            agent_model: The SGAgent model instance
            parent: Parent widget
        """
        super().__init__(agent_model, parent)
        self.agent_model = agent_model
        
        # Agent-specific properties
        self.cell = agent_model.cell
        self.defaultImage = agent_model.defaultImage
        self.popupImage = agent_model.popupImage
        self.dragging = False
        
        # Initialize position coordinates to avoid AttributeError
        self.xCoord = 0
        self.yCoord = 0
        
        # Allow drops
        self.setAcceptDrops(True)
        
        # Don't position immediately - wait for grid layout to be applied
        # self.getPositionInEntity()
    
    def getPositionInEntity(self):
        """Get the absolute position of the agent within its cell"""
        # Use the agent model's current cell, not the view's cached cell
        current_cell = self.agent_model.cell
        
        print(f"DEBUG: getPositionInEntity called for agent {self.agent_model.id}")
        print(f"DEBUG: Current cell: {current_cell.id if current_cell else 'None'}")
        print(f"DEBUG: Cell view exists: {hasattr(current_cell, 'view') and current_cell.view is not None}")
        if hasattr(current_cell, 'view') and current_cell.view:
            print(f"DEBUG: Cell view position: ({current_cell.view.x()}, {current_cell.view.y()})")
        
        # Calculate relative position within the cell
        if self.classDef.locationInEntity == "random":
            relX = random.randint(0, current_cell.size - self.size)
            relY = random.randint(0, current_cell.size - self.size)
        elif self.classDef.locationInEntity == "topRight":
            relX = current_cell.size - self.size
            relY = 0
        elif self.classDef.locationInEntity == "topLeft":
            relX = 0
            relY = 0
        elif self.classDef.locationInEntity == "bottomLeft":
            relX = 0
            relY = current_cell.size - self.size
        elif self.classDef.locationInEntity == "bottomRight":
            relX = current_cell.size - self.size
            relY = current_cell.size - self.size
        elif self.classDef.locationInEntity == "center":
            relX = (current_cell.size - self.size) // 2
            relY = (current_cell.size - self.size) // 2
        else:
            raise ValueError("Error in entry for locationInEntity")
        
        # Calculate absolute position based on cell position
        self.xCoord = current_cell.view.x() + relX
        self.yCoord = current_cell.view.y() + relY
        
        print(f"DEBUG: Agent {self.agent_model.id} calculated position: ({self.xCoord}, {self.yCoord})")
        
        # Update the view position
        self.move(self.xCoord, self.yCoord)
    
    def updatePositionFromCell(self):
        """Update agent position when cell moves"""
        # Update the view's cell reference to match the model
        self.cell = self.agent_model.cell
        self.getPositionInEntity()
    
    def paintEvent(self, event):
        """Paint the agent"""
        painter = QPainter() 
        painter.begin(self)
        region = self.getRegion()
        painter.setClipRegion(region)
        
        image = self.defaultImage if self.defaultImage is not None else self.getImage()
        if image is not None:
            if image.width() == 0 or image.height == 0: 
                raise ValueError(f'Image size is not valid for {self.privateID}')
            rect, scaledImage = self.rescaleImage(image)
            painter.drawPixmap(rect, scaledImage)
        else:
            painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
            
        penColorAndWidth = self.getBorderColorAndWidth()
        painter.setPen(QPen(penColorAndWidth['color'], penColorAndWidth['width']))
        
        agentShape = self.classDef.shape
        x = self.xCoord
        y = self.yCoord
        
        if self.isDisplay == True:
            if(agentShape == "circleAgent"):
                self.setGeometry(x, y, self.size, self.size)
                painter.drawEllipse(0, 0, self.size, self.size)
            elif(agentShape == "squareAgent"):
                self.setGeometry(x, y, self.size, self.size)
                painter.drawRect(0, 0, self.size, self.size)
            elif(agentShape == "ellipseAgent1"): 
                self.setGeometry(x, y, self.size, round(self.size / 2))
                painter.drawEllipse(0, 0, self.size, round(self.size / 2))
            elif(agentShape == "ellipseAgent2"): 
                self.setGeometry(x, y, round(self.size / 2), self.size)
                painter.drawEllipse(0, 0, round(self.size / 2), self.size)
            elif(agentShape == "rectAgent1"): 
                self.setGeometry(x, y, self.size, round(self.size / 2))
                painter.drawRect(0, 0, self.size, round(self.size / 2))
            elif(agentShape == "rectAgent2"): 
                self.setGeometry(x, y, round(self.size / 2), self.size)
                painter.drawRect(0, 0, round(self.size / 2), self.size)
            elif(agentShape == "triangleAgent1"): 
                self.setGeometry(x, y, self.size, self.size)
                points = QPolygon([
                    QPoint(round(self.size / 2), 0),
                    QPoint(0, self.size),
                    QPoint(self.size, self.size)
                ])
                painter.drawPolygon(points)
            elif(agentShape == "triangleAgent2"): 
                self.setGeometry(x, y, self.size, self.size)
                points = QPolygon([
                    QPoint(0, 0),
                    QPoint(self.size, 0),
                    QPoint(round(self.size / 2), self.size)
                ])
                painter.drawPolygon(points)
            elif(agentShape == "arrowAgent1"): 
                self.setGeometry(x, y, self.size, self.size)
                points = QPolygon([
                    QPoint(round(self.size / 2), 0),
                    QPoint(0, self.size),
                    QPoint(round(self.size / 2), round(self.size / 3) * 2),
                    QPoint(self.size, self.size)
                ])
                painter.drawPolygon(points)
            elif(agentShape == "arrowAgent2"): 
                self.setGeometry(x, y, self.size, self.size)
                points = QPolygon([
                    QPoint(0, 0),
                    QPoint(self.size, 0),
                    QPoint(round(self.size / 2), round(self.size / 3)),
                    QPoint(round(self.size / 2), self.size)
                ])
                painter.drawPolygon(points)
            elif(agentShape == "hexagonAgent"):
                self.setGeometry(x, y, self.size, self.size)
                side = self.size / 2
                height = round(side * (3 ** 0.5)) + 10  # Hauteur de l'hexagone équilatéral
                points = QPolygon([
                    QPoint(round(self.size / 2), 0),                # Sommet supérieur
                    QPoint(self.size, round(height / 4)),           # Coin supérieur droit
                    QPoint(self.size, round(3 * height / 4)),       # Coin inférieur droit
                    QPoint(round(self.size / 2), height),           # Sommet inférieur
                    QPoint(0, round(3 * height / 4)),               # Coin inférieur gauche
                    QPoint(0, round(height / 4))                     # Coin supérieur gauche
                ])
                painter.drawPolygon(points)
                
        painter.end()
    
    def getRegion(self):
        """Get the region for the agent shape"""
        agentShape = self.classDef.shape
        if agentShape == "circleAgent":
            region = QRegion(0, 0, self.size, self.size, QRegion.Ellipse)
        elif agentShape == "squareAgent":
            region = QRegion(0, 0, self.size, self.size)
        elif agentShape == "ellipseAgent1":
            region = QRegion(0, 0, self.size, round(self.size / 2), QRegion.Ellipse)
        elif agentShape == "ellipseAgent2":
            region = QRegion(0, 0, round(self.size / 2), self.size, QRegion.Ellipse)
        elif agentShape == "rectAgent1":
            region = QRegion(0, 0, self.size, round(self.size / 2))
        elif agentShape == "rectAgent2":
            region = QRegion(0, 0, round(self.size / 2), self.size)
        elif agentShape == "triangleAgent1":
            points = QPolygon([
                QPoint(round(self.size / 2), 0),
                QPoint(0, self.size),
                QPoint(self.size, self.size)
            ])
            region = QRegion(points)
        elif agentShape == "triangleAgent2":
            points = QPolygon([
                QPoint(0, 0),
                QPoint(self.size, 0),
                QPoint(round(self.size / 2), self.size)
            ])
            region = QRegion(points)
        elif agentShape == "arrowAgent1":
            points = QPolygon([
                QPoint(round(self.size / 2), 0),
                QPoint(0, self.size),
                QPoint(round(self.size / 2), round(self.size / 3) * 2),
                QPoint(self.size, self.size)
            ])
            region = QRegion(points)
        elif agentShape == "arrowAgent2":
            points = QPolygon([
                QPoint(0, 0),
                QPoint(self.size, 0),
                QPoint(round(self.size / 2), round(self.size / 3)),
                QPoint(round(self.size / 2), self.size)
            ])
            region = QRegion(points)
        elif agentShape == "hexagonAgent":  
            side = self.size / 2
            height = round(side * (3 ** 0.5)) + 10  
            points = QPolygon([
                QPoint(round(self.size / 2), 0),        
                QPoint(self.size, round(height / 4)),           
                QPoint(self.size, round(3 * height / 4)),    
                QPoint(round(self.size / 2), height),        
                QPoint(0, round(3 * height / 4)),              
                QPoint(0, round(height / 4))                   
            ])
            region = QRegion(points)
        else:
            region = QRegion(0, 0, self.size, self.size)
        return region

    # Interaction methods
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            # Something is selected
            aLegendItem = self.agent_model.model.getSelectedLegendItem()
            if aLegendItem is None: 
                return  # Exit the method

            # Use the gameAction system for ALL players (including Admin)
            from mainClasses.gameAction.SGMove import SGMove
            if isinstance(aLegendItem.gameAction, SGMove): 
                return
            aLegendItem.gameAction.perform_with(self.agent_model)
            return

    def mouseMoveEvent(self, e):
        """Handle mouse move events for dragging"""
        if e.buttons() != Qt.LeftButton:
            return

        mimeData = QMimeData()
        drag = QDrag(self)
        drag.setMimeData(mimeData)

        # Take a snapshot of the widget (the agent)
        pixmap = self.grab()

        # Make the pixmap semi-transparent
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QColor(0, 0, 0, 128))  # 128 = 50% opacity
        painter.end()

        # Set the pixmap as the drag preview
        drag.setPixmap(pixmap)

        # Keep the cursor aligned with the click point
        drag.setHotSpot(e.pos())

        # Start the drag operation
        drag.exec_(Qt.CopyAction | Qt.MoveAction)

    def dragEnterEvent(self, e):
        """Handle drag enter events"""
        e.acceptProposedAction()

    def dropEvent(self, e):    
        """Handle drop events"""
        if hasattr(e.source(), 'cell') and self.agent_model.cell is not None:
            # Specific case: forward the drop to the cell
            self.agent_model.cell.dropEvent(e)
        else:
            # Fallback: delegate the drop handling to the parent model
            self.agent_model.model.dropEvent(e)

    def enterEvent(self, event):
        """Handle mouse enter events for tooltips"""
        if self.dragging:
            return

        if self.popupImage:
            # Convertir l'image en HTML pour ToolTip
            image_html = f"<img src='{self.popupImage}' style='max-width: 200px; max-height: 200px;'>"
            QToolTip.showText(QCursor.pos(), image_html, self)

    def leaveEvent(self, event):
        """Handle mouse leave events"""
        QToolTip.hideText()
