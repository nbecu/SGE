from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class SGAgentCollection():
    def __init__(self,parent):
        #Basic initialize
        self.parent=parent
        self.agents={}
        #Initialize the different pov
        self.povs={"default":Qt.black}
        
       
    #To get all the Agents of the collection 
    def getAgents(self):
        return self.agents
    
    #To get all the povs of the collection 
    def getPovs(self):
        return self.povs
    
    #To get an Agent in particular
    def getAgent(self,aName):
        return self.agents[aName]
    
    #To add an Agent 
    def addAgent(self,anAgent):
        self.agents[anAgent.getId()]=anAgent
    
    #To remove an Agent in particular
    def removeAgent(self,aName):
        pass
        
    

        
    
        
            