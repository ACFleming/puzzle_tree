"""_summary_

    Returns:
        _type_: _description_
    """
from enum import Enum
from typing import Dict, Self, Deque
from abc import ABC, abstractmethod
from itertools import count
from collections import deque
from tt import BooleanExpression
from puzzle_tree.defs import CONNECTIONS_LIMIT

class NodeType(Enum):
    """Enum of the Node Types

    Args:
        Enum (_type_): _description_
    """
    ROOT = 1
    EDGE = 2
    LEAF = 3
    AND = 4
    OR = 5
    NOT = 6
    SWITCH = 7
    ERROR = 8



class StateObj(ABC):
    """Abstract State Object. All real nodes inherit from this
    """

    @classmethod
    def connect(cls,input_obj:Self, output_obj:Self):
        """Connect the input object to the output object. This is the way the tree is connected
        Note: One and only one of the objects must be an edge

        Args:
            input_obj (Self): _description_
            output_obj (Self): _description_
        """
        input_is_edge = isinstance(input_obj, Edge)
        output_is_edge = isinstance(output_obj, Edge)
        assert input_is_edge != output_is_edge

        input_obj.add_output(output_obj)
        output_obj.add_input(input_obj)
        input_obj.update()
        output_obj.update()

    _id_counter = count(0)
    def __init__(self):
        self._id = next(StateObj._id_counter)
        self._bool_id = f"{self.__class__.__name__}_{self._id}"
        self._state = False
        self._input_objs : Deque[StateObj] = deque(maxlen=CONNECTIONS_LIMIT)
        self._output_objs : Deque[StateObj] = deque(maxlen=CONNECTIONS_LIMIT)
        self._bool_expr = BooleanExpression("NULL")

    def __repr__(self):
        return (
            f"{self._bool_id}:\n"
            f" State: {self._state}\n"
            f" Expression: {self._bool_expr}\n"
            f" Inputs: {[n.bool_id for n in self._input_objs]}\n"
            f" Outputs: {[n.bool_id for n in self._output_objs]}"
        )

    @property
    def bool_id(self) -> str:
        """Returns the id of the boolean variable

        Returns:
            str: class name + id
        """
        return self.bool_id

    @property
    def state(self) -> bool:
        """Returns the state of the object

        Returns:
            bool: state
        """
        return self._state

    def calculate_state(self):
        """Calculates the current state of the object based on the state of the inputs 
        and the boolean expression of this node
        """
        input_states = {}
        for i in self._input_objs:
            input_states[i.getBoolId()] = i.getState()
        self._state = self._bool_expr.evaluate(**input_states)

    def update_ouputs(self):
        """Call update on all output edges
        """
        for out in self._output_objs:
            out.update()

    def update(self):
        """Update this node. 
        This is done by generating the boolean expression for this node based on the input node.
        Then calculating the state from this expression.
        Then update the outputs.
        """
        self.generate_bool_expr()
        self.calculate_state()
        self.update_ouputs()

    def add_output(self, o:Self):
        """Add an output object

        Args:
            o (Self): _description_
        """
        self._output_objs.append(o)

    def add_input(self, i:Self):
        """Add an input object

        Args:
            i (Self): _description_
        """
        self._input_objs.append(i)

    @abstractmethod
    def generate_bool_expr(self):
        """Generate the boolan expression for this type of node. 
        This uses the bool_ids of the input nodes as boolean algebraic operators
        """



class Edge(StateObj):
    """Edge object. Unique kind of object. Used to connect 2 kinds of nodes together.
    It also has a selected condition, where the edge can be selected or not, meaning  
    the state does not propagate along the unselected edg. Used for the switch node type.
    Can only have 1 input and 1 output.
    """
    def __init__(self):
        super().__init__()
        self._input_objs = deque(maxlen=1)
        self._output_objs = deque(maxlen=1)
        self._selected = True

    def edge_selected(self, v: bool):
        """Set whether or not this edge is selected

        Args:
            v (bool): Edge selection condition
        """
        self._selected = v



    def __repr__(self):
        return super().__repr__() + f"\n Selected?: {self._selected}"

    def generate_bool_expr(self):
        assert self._input_objs
        self._bool_expr = BooleanExpression(self._input_objs[0].getBoolId())

    def calculate_state(self):
        assert self._input_objs
        input_states = {self._input_objs[0].getBoolId(): self._input_objs[0].getState()}
        self._state = self._bool_expr.evaluate(**input_states) & self._selected

class ORNode(StateObj):
    """OR node. State is true when one or more input edges is true. False otherwise.
    Can only have 1 output.
    """
    def __init__(self):
        super().__init__()
        self._node_type = NodeType.OR

    def generate_bool_expr(self):
        parts = " OR ".join(obj.getBoolId() for obj in self._input_objs)
        self._bool_expr = BooleanExpression(parts)

class ANDNode(StateObj):
    """AND node. State is true when all of the input edges are true. False otherwise.
    Can only have 1 output.
    """
    def __init__(self):
        super().__init__()
        self._node_type = NodeType.AND


    def generate_bool_expr(self):
        parts = " AND ".join(obj.getBoolId() for obj in self._input_objs)
        self._bool_expr = BooleanExpression(parts)


class NOTNode(StateObj):
    """NOT node. State is true when the input edge is false. False otherwise.
    Can only have 1 input and 1 output.
    """
    def __init__(self):
        super().__init__()
        self._input_objs = deque(maxlen=1)
        self._output_objs = deque(maxlen=1)
        self._node_type = NodeType.NOT

    def add_output(self, o):
        if len(self._output_objs) == 0:
            self._output_objs.append(o)
        else:
            self._output_objs[0] = o

    def add_input(self, i:Self):
        if len(self._input_objs) == 0:
            self._input_objs.append(i)

        else:
            self._input_objs[0] = i


    def generate_bool_expr(self):
        parts = " NOT ".join(obj.getBoolId() for obj in self._input_objs)
        self._bool_expr = BooleanExpression(parts)


class SwitchNode(StateObj):
    """Switch node. State is true if any of the input edges are true. False otherwise.
    Main function is to select/deselect the output edges, such that zero or more edges 
    may propagate the state. Can only have 1 input.
    """
    def __init__(self):
        super().__init__()
        self._input_objs = deque(maxlen=1)
        self._switch_selection: dict[int, bool] = {}
        self._node_type = NodeType.SWITCH

    def add_output(self, o):
        super().add_output(o)
        assert isinstance(o,Edge)
            # Only the switch function is allowed to select or deslect edges
        o.edge_selected(False)
        self._switch_selection[o] = False

    def __repr__(self):
        return super().__repr__() + f"\n Switch Selection?: {self._switch_selection}"

    def generate_bool_expr(self):
        parts = " OR ".join(obj.getBoolId() for obj in self._input_objs)
        self._bool_expr = BooleanExpression(parts)


    def select_switch_edges(self, edge_indicies: Dict[int, bool]):
        """Specify the selected condition for any/all output edges.

        Args:
            edge_indicies (Dict[int, bool]): Mapping of edge index to selected condition 
            for that edge index

        Raises:
            KeyError: If the indicies are not valid indicies (i.e. that output edge does not exist)
        """
        unknown = set(edge_indicies) - set(self._switch_selection)
        if unknown:
            raise KeyError(f"Unknown edges: {unknown}")
        for k,v in edge_indicies.items():
            assert isinstance(v, bool)
            self._switch_selection[k] = v
            e = self._output_objs[k]
            assert isinstance(e,Edge)
            # Only the switch function is allowed to select or deslect edges
            e.edge_selected(v)



class RootNode(StateObj):
    """Root node. Tree is built from 1 or more roots. State is set by user. Expression is not used.
    Cannot have any inputs.

    """
    def __init__(self):
        super().__init__()
        self._node_type = NodeType.ROOT

    def add_input(self, i:Self):
        pass

    def generate_bool_expr(self):
        self._bool_expr = BooleanExpression(self.bool_id())

    def calculate_state(self):
        pass

    def on(self):
        """Set state true
        """
        self.set_state(True)

    def off(self):
        """Set state false
        """
        self.set_state(False)


    def set_state(self,b:bool):
        """Set state to given value

        Args:
            b (bool): new state value
        """
        self._state = b
        self.update_ouputs()


class LeafNode(ANDNode):
    """Leaf node. Used as the end of a node. 
    State is true if any of the input edges are true. False otherwise.
    Can only have 1 input.
    Args:
        ANDNode (_type_): _description_
    """
    def __init__(self):
        super().__init__()
        self._input_objs = deque(maxlen=1)

    def add_output(self, o):
        pass

    def generate_bool_expr(self):
        parts = " OR ".join(obj.getBoolId() for obj in self._input_objs)
        self._bool_expr = BooleanExpression(parts)
