
from typing import List, Dict, Self, Deque
from tt import BooleanExpression
from abc import ABC, abstractmethod
from itertools import count
from collections import deque
import logging
from puzzle_tree.defs import CONNECTIONS_LIMIT
logger = logging.getLogger(__name__)



class StateObj(ABC):

    @classmethod
    def connect(cls,input_obj:Self, output_obj:Self):
        assert (isinstance(input_obj, Edge) and not isinstance(output_obj, Edge)) or (not isinstance(input_obj, Edge) and isinstance(output_obj, Edge))
        input_obj.add_output(output_obj)
        output_obj.add_input(input_obj)
        input_obj.update()
        output_obj.update()

    _id_counter = count(0)
    def __init__(self, label:str = "",state: bool = False):
        self.id = next(StateObj._id_counter)
        self.bool_id = f"{self.__class__.__name__}_{self.id}"
        self.label = label
        self.state = state
        self.input_objs : Deque[StateObj] = deque(maxlen=CONNECTIONS_LIMIT)
        self.output_objs : Deque[StateObj] = deque(maxlen=CONNECTIONS_LIMIT)
        self.bool_expr = BooleanExpression("NULL")
    
    def __repr__(self):
        return f"{self.bool_id}: \n Label: {self.label} \n State: {self.state} \n Expression: {self.bool_expr} \n Inputs: {[n.bool_id for n in self.input_objs]} \n Outputs: {[n.bool_id for n in self.output_objs]}"

    def getBoolId(self):
        return self.bool_id

    def getState(self):
        return self.state

    def calculateState(self):
        input_states = {}
        for i in self.input_objs:
            input_states[i.getBoolId()] = i.getState()
        self.state = self.bool_expr.evaluate(**input_states)

    def powerOutputs(self):
        for out in self.output_objs:
            out.update()
            
    def isConnected(self):
        return True

    def update(self):
        self.generateBooleanExpression()
        self.calculateState()
        self.powerOutputs()
        

    def isOn(self):
        return self.state
        
    def isOff(self):
        return not self.isOn()
    
    def add_output(self, o:Self):
        self.output_objs.append(o)

    def add_input(self, i:Self):
        self.input_objs.append(i)

    @abstractmethod
    def generateBooleanExpression(self):
        pass


class Edge(StateObj):
    def __init__(self, label:str = "", state: bool = False):
        super().__init__(label, state)
        self.input_objs = deque(maxlen=1)
        self.output_objs = deque(maxlen=1)
        self._selected = True


    def __repr__(self):
        return super().__repr__() + f"\n Selected?: {self._selected}"
    
    # def add_output(self, o):
    #     if len(self.output_objs) == 0:
    #         self.output_objs.append(o)
    #     else:
    #         self.output_objs[0] = o 
            
    # def add_input(self, i:Self):
    #     if len(self.input_objs) == 0:
    #         self.input_objs.append(i)
            
    #     else:
    #         self.input_objs[0] = i

    def generateBooleanExpression(self):
        assert self.input_objs
        self.bool_expr = BooleanExpression(self.input_objs[0].getBoolId())

    def calculateState(self):
        assert self.input_objs
        input_states = {self.input_objs[0].getBoolId(): self.input_objs[0].getState()}
        self.state = self.bool_expr.evaluate(**input_states) & self._selected

        
class ORNode(StateObj):
    def __init__(self, label:str = "", state: bool = False):
        super().__init__(label, state)

    # def add_output(self, o):
    #     self.output_objs.append(o)

    # def add_input(self, i):
    #     self.input_objs.append(i)

    def generateBooleanExpression(self):
        self.bool_expr = BooleanExpression(" OR ".join(obj.getBoolId() for obj in self.input_objs))



class ANDNode(StateObj):
    def __init__(self, label:str = "", state: bool = False):
        super().__init__(label, state)


    # def add_output(self, o):
    #     self.output_objs.append(o)

    # def add_input(self, i):
    #     self.input_objs.append(i)

    def generateBooleanExpression(self):
        self.bool_expr = BooleanExpression(" AND ".join(obj.getBoolId() for obj in self.input_objs))


class NOTNode(StateObj):
    def __init__(self, label:str = "", state: bool = False):
        super().__init__(label, state)
        self.input_objs = deque(maxlen=1)
        self.output_objs = deque(maxlen=1)

    def add_output(self, o):
        if len(self.output_objs) == 0:
            self.output_objs.append(o)
        else:
            self.output_objs[0] = o
            
    def add_input(self, i:Self):
        if len(self.input_objs) == 0:
            self.input_objs.append(i)
            
        else:
            self.input_objs[0] = i
            

    def generateBooleanExpression(self):
        self.bool_expr = BooleanExpression(f"NOT {self.input_objs[0].getBoolId()}")


class SwitchNode(StateObj):
    def __init__(self, label:str = "", state: bool = False):
        super().__init__(label, state)
        self.input_objs = deque(maxlen=1)
        self.switch_selection: dict[int, bool] = {}

    def add_output(self, o):
        super().add_output(o)
        self.switch_selection[o] = False
    
    # def add_input(self, i:Self):
    #     if len(self.input_objs) == 0:
    #         self.input_objs.append(i)
    #     else:
    #         self.input_objs[0] = i

    def __repr__(self):
        return super().__repr__() + f"\n Switch Selection?: {self.switch_selection}"

    def generateBooleanExpression(self):
        self.bool_expr = BooleanExpression(self.input_objs[0].getBoolId())

    def switchOn(self, on_indicies:List[int]):
        self.setSwitchState(dict.fromkeys(on_indicies, True))

    def switchOff(self, off_indicies:List[int]):
        self.setSwitchState(dict.fromkeys(off_indicies, False))

    def setSwitchState(self, edge_indicies: Dict[int, bool]):
        for k,v in edge_indicies.items():
            self.switch_selection[k] = v
            e = self.output_objs[k]
            assert isinstance(e,Edge)
            # Only the switch function is allowed to select or deslect edges
            e._selected = v
            


class RootNode(StateObj):
    def __init__(self, label:str = "", state: bool = False):
        super().__init__(label, state)

    # def add_output(self, o):
    #     self.output_objs.append(o)
            
    def add_input(self, i:Self):
        pass        

    def generateBooleanExpression(self):
        self.bool_expr = BooleanExpression(self.getBoolId())

    def calculateState(self):
        pass

    def on(self):
        self.state = True
        self.powerOutputs()

    def off(self):
        self.state = False
        self.powerOutputs()

    def setState(self,b:bool):
        self.on() if b else self.off()


class LeafNode(ANDNode):
    def __init__(self, label:str = "",state: bool = False):
        super().__init__(label, state)
        self.input_objs = deque(maxlen=1)

    def add_output(self, o):
        pass
    
    # def add_input(self, i:Self):
    #     if len(self.input_objs) == 0:
    #         self.input_objs.append(i)
    #     else:
    #         self.input_objs[0] = i


if __name__ == "__main__":
    

    node1 = RootNode("Node1")
    node2 = RootNode("Node2")

    e3 = Edge()
    e4 = Edge()

    StateObj.connect(node1, e3)
    StateObj.connect(node2, e4)

    or_node = ORNode("OR Node")

    
    
    StateObj.connect(e3, or_node)
    StateObj.connect(e4, or_node)


    for state1 in [False, True]:
        node1.setState(state1)
        for state2 in [False, True]:
            
            node2.setState(state2)

            print(f"{state1} OR {state2} == {or_node.getState()}")

    and_node = ANDNode("AND Node")
    
    StateObj.connect(e3, and_node)
    StateObj.connect(e4, and_node)

    for state1 in [False, True]:
        node1.setState(state1)
        for state2 in [False, True]:
            
            node2.setState(state2)


            print(f"{state1} AND {state2} == {and_node.getState()}")
    
    not_node = NOTNode("NOT Node")
    StateObj.connect(e3,not_node)

    for state1 in [False, True]:
        node1.setState(state1)
        print(f"NOT {state1} == {not_node.getState()}")
    
    switch_node = SwitchNode("Switch Node")
    StateObj.connect(e3, switch_node)
    up_edge = Edge("Up Edge")
    down_edge = Edge("Down Edge")
    StateObj.connect(switch_node, up_edge)
    StateObj.connect(switch_node,down_edge)
    up_node = LeafNode("Up Node")
    StateObj.connect(up_edge, up_node)
    down_node = LeafNode("Down Node")
    StateObj.connect(down_edge, down_node)
    print(switch_node)

    for state1 in [False, True]:
        node1.setState(state1)
        for connections in range(4):
            match connections:
                case 0:
                    switch_node.allOff()
                case 1:
                    switch_node.switchOn([0])
                case 2:
                    switch_node.switchOff([0])
                    switch_node.switchOn([1])
                case 3:
                    switch_node.allOff()
                    switch_node.allOn()


            print(f"{state1} with Switch {switch_node.getState()} Up {up_edge.connected} --> Up is {up_node.getState()}")
            print(f"{state1} with Switch {switch_node.getState()} Down {down_edge.connected} --> Down is {down_node.getState()}")
    

    StateObj.connect