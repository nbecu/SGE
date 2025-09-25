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
        
        # Type identification attributes
        self.isEntity = True
        self.isCell = False
        self.isAgent = True
        
        # Agent-specific properties
        self.cell = agent_model.cell
        self.defaultImage = agent_model.defaultImage
        self.popupImage = agent_model.popupImage
        self.dragging = False
        
        # Initialize position coordinates to avoid AttributeError
        self.xCoord = 0
        self.yCoord = 0
        
        # Save reference size for zoom calculations
        self.saveSize = self.size
        
        # Allow drops
        self.setAcceptDrops(True)
        
        # Don't position immediately - wait for grid layout to be applied
        # self.getPositionInEntity()
    
    def getPositionInEntity(self, saved_cell_position=None):
        """Get the absolute position of the agent within its cell"""
        # Use the agent model's current cell, not the view's cached cell
        current_cell = self.agent_model.cell
        
        # Use grid size for consistent zoom behavior (like SGCellView)
        grid_size = current_cell.grid.size
        
        # Calculate relative position within the cell based on current grid size
        if self.type.locationInEntity == "random":
            # For random, we need to maintain the same relative position
            if not hasattr(self, '_randomX') or not hasattr(self, '_randomY'):
                self._randomX = random.random()  # Store as 0.0 to 1.0
                self._randomY = random.random()
            relX = int(self._randomX * (grid_size - self.size))
            relY = int(self._randomY * (grid_size - self.size))
        elif self.type.locationInEntity == "topRight":
            relX = grid_size - self.size
            relY = 0
        elif self.type.locationInEntity == "topLeft":
            relX = 0
            relY = 0
        elif self.type.locationInEntity == "bottomLeft":
            relX = 0
            relY = grid_size - self.size
        elif self.type.locationInEntity == "bottomRight":
            relX = grid_size - self.size
            relY = grid_size - self.size
        elif self.type.locationInEntity == "center":
            # For center, always maintain exact center regardless of sizes
            relX = (grid_size - self.size) / 2
            relY = (grid_size - self.size) / 2
            # Ensure we get exact center by using precise calculation
            relX = max(0, relX)  # Don't go negative
            relY = max(0, relY)  # Don't go negative
        else:
            raise ValueError("Error in entry for locationInEntity")
        
        # Always use current cell position for accurate positioning
        cell_x = current_cell.view.x()
        cell_y = current_cell.view.y()
        
        self.xCoord = cell_x + round(relX)
        self.yCoord = cell_y + round(relY)
        
        # Update the view position
        try:
            self.move(self.xCoord, self.yCoord)
        except RuntimeError:
            # Agent view has been deleted, ignore the error
            pass
    
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
        
        agentShape = self.type.shape
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
        agentShape = self.type.shape
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
            from mainClasses.gameAction.SGCreate  import SGCreate
            if isinstance(aLegendItem.gameAction, SGCreate): 
                return aLegendItem.gameAction.perform_with(self.agent_model.cell)
            aLegendItem.gameAction.perform_with(self.agent_model)
            return

    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def mouseMoveEvent(self, e):
        """Handle mouse move events for dragging"""
        if e.buttons() != Qt.LeftButton:
            # If no button is pressed, reset dragging state
            if self.dragging:
                self.dragging = False
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
        result = drag.exec_(Qt.CopyAction | Qt.MoveAction)
        
        # Reset dragging state after drag operation completes
        self.dragging = False

    def dragEnterEvent(self, e):
        """Handle drag enter events"""
        e.acceptProposedAction()

    def dropEvent(self, e):    
        """Handle drop events"""
        # Reset dragging state when drop occurs
        self.dragging = False
        
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
        # No fallback - only show tooltip if popupImage exists (original behavior)

    def leaveEvent(self, event):
        """Handle mouse leave events"""
        QToolTip.hideText()
    
    # ============================================================================
    # ZOOM METHODS
    # ============================================================================
    
    def updateZoom(self, zoom_factor):
        """
        Update agent zoom based on zoom factor
        """
        # Calculate zoomed size from reference value
        self.size = round(self.saveSize * zoom_factor)
        self.update()
    
    def zoomIn(self, zoom_factor=1.1):
        """Zoom in the agent - legacy method for compatibility"""
        self.size = round(self.size * zoom_factor)
        self.update()
    
    def zoomOut(self, zoom_factor=0.9):
        """Zoom out the agent - legacy method for compatibility"""
        self.size = round(self.size * zoom_factor)
        self.update()