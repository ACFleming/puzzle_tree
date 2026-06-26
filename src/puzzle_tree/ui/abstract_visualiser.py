from enum import Enum, auto


class FlowchartShape(Enum):
    PROCESS      = auto()
    DECISION     = auto()
    TERMINAL     = auto()
    IO           = auto()
    DOCUMENT     = auto()
    CONNECTOR    = auto()
    SUBROUTINE   = auto()
    MANUAL_INPUT = auto()
    PREPARATION  = auto()
    DATABASE     = auto()
    DISPLAY      = auto()
    DELAY        = auto()


# class PlottedNode():
#     def __init__(self, logic_node: StateObj, x, y, label, description, colour, text_colour):
#         super().__init__(label)
#         self.logic_node: StateObj = logic_node
#         self.description: str = description
#         self.colour = colour
#         self.text_colour = colour
#         self.x = x
#         self.y = y

# class PlottedEdge(StateObj):
#     def __init__(self, start_node: PlottedNode, end_node:PlottedNode, label, colour, text_colour):
#         super().__init__(label)
#         self.colour = colour
#         self.text_colour = colour
#         self.start = start_node
#         self.end = end_node