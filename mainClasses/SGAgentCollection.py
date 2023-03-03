from PyQt5 import QtWidgets 
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import *
from PyQt5.QtCore import *

#Class that manage the collection of agent
class SGAgentCollection():
    def __init__(self,parent):
        #Basic initialize
        self.parent=parent
        self.listofcollection={}
        #Initialize the different pov
        self.povs={}
        
    #To add a new collection
    def addToCollection(self,name):
        self.listofcollection[name]=[]

    #To add a new Agent to his collection  
    def addAnAgentToHisCollection(self,anAgentName,CollectionName):
        self.listofcollection[str(CollectionName)]=anAgentName
    
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
        self.agents.append(anAgent)
    
    #To remove an Agent in particular
    def removeAgent(self,aName):
        pass
        
    

        
    
        
            