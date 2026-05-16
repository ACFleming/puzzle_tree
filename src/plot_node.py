import itertools
from typing import List
from enum import Enum

class Activity(Enum):
    OFF = 1
    ON = 2
    FORCED_ON = 3
    FORCED_OFF = 4

class Edge():
    _edge_id = itertools.count(1)

    def __init__(self,n1: Node, n2: Node, label:str = ""):
        self.start_node = n1
        self.end_node = n2
        self.start_node.output_edges.append(self)
        self.end_node.input_edges.append(self)
        self.state = Activity.OFF
        self.label = label

    def on(self):
        self.state = Activity.ON
        self.end_node.update()
    def off(self):
        self.state = Activity.OFF
        self.end_node.update()



class Node():
    _node_id = itertools.count(1)

    def __init__(self, label:str = "node"):
        self.id:str = next(Node._node_id)
        self.desc:str = ""
        self.activity_state:Activity = Activity.OFF
        self.input_edges: List[Edge]  = []
        self.output_edges: List[Edge] = []
        self.input_requirement = 1
        self.output_configuration: List[bool] = []

    
    def force_active_state(self, forced: Activity):
        assert (forced == Activity.FORCED_ON) or (forced == Activity.FORCED_OFF)
        self.activity_state = forced
        self.update()

    def update(self):
        active_edges = sum(1 for e in self.input_edges if e.state == Activity.ON)
        if active_edges >= self.input_requirement:
            self.activity_state = Activity.ON
        else:
            self.activity_state = Activity.OFF
        
        if len(self.output_configuration) == 0:
            for e in self.output_edges:
                e.on()
        else:
            for i,e in enumerate(self.output_edges):
                if self.output_configuration[i] == True:
                    e.on()
                else:
                    e.off()



if __name__ == "__main__":
    

    node1 = Node("Node1")
    node2 = Node("Node2")

    and_node = Node("AND Node")
    

    e1 = Edge(node1, and_node)
    e2 = Edge(node2,and_node)

    and_node.input_requirement = len(and_node.input_edges)

    node1.force_active_state(Activity.FORCED_ON)

    print(and_node.activity_state)

    node1.force_active_state(Activity.FORCED_OFF)
    node2.force_active_state(Activity.FORCED_ON)

    print(and_node.activity_state)

    node1.force_active_state(Activity.FORCED_ON)
    node2.force_active_state(Activity.FORCED_ON)

    print(and_node.activity_state)
    