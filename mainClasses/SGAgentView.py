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
        
        # Allow drops
        self.setAcceptDrops(True)
        
        # Get position in entity
        self.getPositionInEntity()
    
    def getPositionInEntity(self):
        """Get the position of the agent within its cell"""
        if self.classDef.locationInEntity == "random":
            self.xCoord = random.randint(0, self.cell.size - self.size)
            self.yCoord = random.randint(0, self.cell.size - self.size)
        elif self.classDef.locationInEntity == "topRight":
            self.xCoord = self.cell.size - self.size
            self.yCoord = 0
        elif self.classDef.locationInEntity == "topLeft":
            self.xCoord = 0
            self.yCoord = 0
        elif self.classDef.locationInEntity == "bottomLeft":
            self.xCoord = 0
            self.yCoord = self.cell.size - self.size
        elif self.classDef.locationInEntity == "bottomRight":
            self.xCoord = self.cell.size - self.size
            self.yCoord = self.cell.size - self.size
        elif self.classDef.locationInEntity == "center":
            self.xCoord = (self.cell.size - self.size) // 2
            self.yCoord = (self.cell.size - self.size) // 2
        else:
            raise ValueError("Error in entry for locationInEntity")
    
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
        else:
            region = QRegion(0, 0, self.size, self.size)
        return region
