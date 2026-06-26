CONNECTIONS_LIMIT = 5
UNDO_MEMORY_LEN = 30

class VisualData:
    label:str
    colour: str
    text_colour: str
    shape:str
    x:float
    y:float
    height:float
    width:float
    rot:float
    


NODE_TYPES = {
    "root":     {"label": "Root",   "colour": "#AD6109", "text": "#ffffff"},
    "NOT":      {"label": "NOT",    "colour": "#CF3419", "text": "#ffffff"},
    "AND":      {"label": "AND",    "colour": "#3D1ABB", "text": "#ffffff"},
    "OR":       {"label": "OR",     "colour": "#229CAC", "text": "#ffffff"},
    "SWITCH":   {"label": "Switch", "colour": "#8F3F8F", "text": "#ffffff"},
    "LEAF":     {"label": "Leaf",   "colour": "#119B2F", "text": "#ffffff"},
    "EDGE":     {"label": "Edge",   "colour": "#A8A8A8", "text": "#000000"},
}
