import sys
from pathlib import Path

from mainClasses.SGModel import*
from mainClasses.SGEntity import*
from mainClasses.SGEntityDef import*
from mainClasses.SGAgent import*
from mainClasses.SGCell import*
from mainClasses.SGModelAction import*
from mainClasses.SGPlayer import*
from mainClasses.SGSimulationVariable import*
from mainClasses.SGTimeManager import*

from mainClasses.SGDiagramTest import *



class SGTestGetData():
    def __init__(self, model):
        self.model = model

    def view_diagram(self):
        print("test")
        self.view_diagram_test()

    def view_diagram_test(self):
        data = self.getAllDataSinceInitialization()
        # list_phasePERround = []
        phases = set(entry['phase'] for entry in data)
        rounds = set(entry['round'] for entry in data)
        cell_data_test = []
        agent_data_test = []
        xValue = []
        for round_value in list(rounds):
            for phase_value in phases:
                xValue.append(round_value * len(phases) + phase_value)
                # print("round : {} , phase_value : {} : ".format(round_value, phase_value))
            cell_data_counts2 = [sum(1 for entry in data if
                                     entry['round'] == round_value and entry['phase'] == phase and entry[
                                         'entityDef'] == 'Cell') for phase in phases]
            cell_data_test = cell_data_test + cell_data_counts2

            agent_data_count2 = [sum(1 for entry in data if
                                     entry['round'] == round_value and entry['phase'] == phase and entry[
                                         'entityDef'] == 'Agent') for phase in phases]
            agent_data_test = agent_data_test + agent_data_count2

        cell_data_counts = [sum(1 for entry in data if entry['phase'] == phase and entry['entityDef'] == 'Cell') for
                            phase in
                            phases]
        agent_data_counts = [sum(1 for entry in data if entry['phase'] == phase and entry['entityDef'] == 'Agent') for
                             phase
                             in phases]

        # xValue = list(phases)
        # xValue = np.arange(1, 121)
        cell_data = list(cell_data_counts)
        agent_data = list(agent_data_counts)
        sgdiagramtest = SGDiagramTest(xValue=xValue, cell_data=cell_data_test, agent_data=agent_data_test)
        sgdiagramtest.update_data()
        #sgdiagramtest.update()
        #window.show()

    def getAllDataSinceInitialization(self):
        dictOfData ={}
        historyData = []
        for aEntity in self.model.getAllEntities():
            h = aEntity.getHistoryDataJSON()
            historyData.append(h)
            dictOfData[aEntity.getObjectIdentiferForJsonDumps] = aEntity.history["value"]
            """print("id: {}, entityName: {}, entityDef: {}, value: {}".
                  format(h['id'], h['entityName'], h['entityDef'], h['value']))"""

            # ToDo: Here I fetch the raw format of the history["value"] of the entity, but perhaps it would need to be reformated
        #print(historyData)


        return historyData
        # self.modelgetAllAgents
        # self.model.getAllCells  --> These two lines are equivalent to self.modelgetAllEntities

        # In addition to data carried by the entities, there are are also data carried by :
        #      - SGEntityDef, SimVariable and SGPlayer --> Those data are in the form of attribute and values
        #      - GameActions  --> Those data are the number of actions performed or left at each round