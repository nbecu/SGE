from PyQt5.QtGui import *
from PyQt5.QtCore import *
from mainClasses.SGEntityView import SGEntityView
from mainClasses.SGEntity import SGEntity

class SGCellView(SGEntityView):
    """
    View class for SGCell - handles all UI and display logic for cells
    Separated from the model to enable Model-View architecture
    """
    
    def __init__(self, cell_model, parent=None):
        """
        Initialize the cell view
        
        Args:
            cell_model: The SGCell model instance
            parent: Parent widget
        """
        super().__init__(cell_model, parent)
        self.cell_model = cell_model
        
        # Cell-specific properties
        self.grid = cell_model.grid
        self.xCoord = cell_model.xCoord
        self.yCoord = cell_model.yCoord
        self.gap = cell_model.gap
        self.saveGap = cell_model.saveGap
        self.saveSize = cell_model.saveSize
        self.startXBase = cell_model.startXBase
        self.startYBase = cell_model.startYBase
        self.defaultImage = cell_model.defaultImage
        
        # Allow drops for agents
        self.setAcceptDrops(True)
    
    def getId(self):
        """Get cell identifier"""
        return "cell" + str(self.xCoord) + "-" + str(self.yCoord)
    
    def paintEvent(self, event):
        """Paint the cell"""
        painter = QPainter()
        painter.begin(self)
        region = self.getRegion()
        image = self.getImage()
        
        if self.isDisplay == True:
            if self.defaultImage != None:
                rect, scaledImage = self.rescaleImage(self.defaultImage)
                painter.setClipRegion(region)
                painter.drawPixmap(rect, scaledImage)
            elif image != None:
                rect, scaledImage = self.rescaleImage(image)
                painter.setClipRegion(region)
                painter.drawPixmap(rect, scaledImage)
            else: 
                painter.setBrush(QBrush(self.getColor(), Qt.SolidPattern))
                
            penColorAndWidth = self.getBorderColorAndWidth()
            painter.setPen(QPen(penColorAndWidth['color'], penColorAndWidth['width']))
            
            self.startXBase = self.grid.frameMargin
            self.startYBase = self.grid.frameMargin
            self.startX = int(self.startXBase + (self.xCoord - 1) * (self.size + self.gap) + self.gap) 
            self.startY = int(self.startYBase + (self.yCoord - 1) * (self.size + self.gap) + self.gap)
            
            if (self.shape == "hexagonal"):
                self.startY = self.startY + self.size / 4
                
            # Base of the gameBoard
            if(self.shape == "square"):
                painter.drawRect(0, 0, self.size, self.size)
                self.setMinimumSize(self.size, self.size + 1)
                self.move(self.startX, self.startY)
            elif(self.shape == "hexagonal"):
                self.setMinimumSize(self.size, self.size)
                points = QPolygon([
                    QPoint(int(self.size / 2), 0),
                    QPoint(self.size, int(self.size / 4)),
                    QPoint(self.size, int(3 * self.size / 4)),
                    QPoint(int(self.size / 2), self.size),
                    QPoint(0, int(3 * self.size / 4)),
                    QPoint(0, int(self.size / 4))              
                ])
                painter.drawPolygon(points)
                if(self.yCoord % 2 != 0):
                    self.move(self.startX, int(self.startY - self.size / 2 * self.yCoord + (self.gap / 10 + self.size / 4) * self.yCoord))
                else:
                    self.move((self.startX + int(self.size / 2) + int(self.gap / 2)), int(self.startY - self.size / 2 * self.yCoord + (self.gap / 10 + self.size / 4) * self.yCoord))
                        
        painter.end()
    
    def getRegion(self):
        """Get the region for the cell shape"""
        cellShape = self.classDef.shape
        if cellShape == "square":
            region = QRegion(0, 0, self.size, self.size)
        if cellShape == "hexagonal":
            points = QPolygon([
                QPoint(int(self.size / 2), 0),
                QPoint(self.size, int(self.size / 4)),
                QPoint(self.size, int(3 * self.size / 4)),
                QPoint(int(self.size / 2), self.size),
                QPoint(0, int(3 * self.size / 4)),
                QPoint(0, int(self.size / 4))              
            ])
            region = QRegion(points)
        return region

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            # Something is selected
            aLegendItem = self.cell_model.model.getSelectedLegendItem()
            if aLegendItem is None: 
                return  # Exit the method

            # Use the gameAction system for ALL players (including Admin)
            aLegendItem.gameAction.perform_with(self.cell_model)
            return

    def dropEvent(self, e):
        """Handle drop events for agent movement"""
        e.acceptProposedAction()
        aAgent = e.source()

        # Delegate type checking to the model
        if not self.cell_model.shouldAcceptDropFrom(aAgent):
            return
        
        currentPlayer = self.cell_model.model.getCurrentPlayer()
    
        # Get authorized move action from player
        authorizedMoveAction = currentPlayer.getAuthorizedMoveActionForDrop(aAgent, self.cell_model)
        
        # Execute the move action if found
        if authorizedMoveAction is not None:
            authorizedMoveAction.perform_with(aAgent, self.cell_model)
            e.setDropAction(Qt.MoveAction)
            # TODO: Remove this line when SGAgentView is implemented
            # The dragging state should be managed by the agent's view, not here
            aAgent.dragging = False
            print(f"DEBUG: Move action completed")
            return
        else:
            print(f"DEBUG: No authorized move action found")

    def dragEnterEvent(self, e):
        """Handle drag enter events"""
        # This event is called during an agent drag 
        e.accept()

    def mouseMoveEvent(self, e):
        """Handle mouse move events to prevent cell dragging"""
        # This method is used to prevent the drag of a cell
        if e.buttons() != Qt.LeftButton:
            return
