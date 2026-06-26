from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Protocol
from collections import deque
from puzzle_tree.defs import UNDO_MEMORY_LEN
from puzzle_tree.node_logic import (
    StateObj, Edge, ORNode, ANDNode, NOTNode, SwitchNode, RootNode, LeafNode,
)

class Command(Protocol):
    def do(self) -> None: pass
    def undo(self) -> None: pass



class UndoStack:
    def __init__(self):
        self._done: deque[Command] = deque(maxlen=UNDO_MEMORY_LEN)
        self._undone: deque[Command] = deque(maxlen=UNDO_MEMORY_LEN)

    def execute(self, cmd: Command) -> None:
        cmd.do()
        self._done.append(cmd)
        self._undone.clear()          # branch: future is gone
 
    def undo(self) -> None:
        if self._done:
            cmd = self._done.pop()
            cmd.undo()
            self._undone.append(cmd)

    def redo(self) -> None:
        if self._undone:
            cmd = self._undone.pop()
            cmd.do()
            self._done.append(cmd)

    @property
    def can_undo(self): return bool(self._done)
    @property
    def can_redo(self): return bool(self._undone)


@dataclass
class AnnotatedNode():
    node:StateObj
    label: str
    desc: str



class TreeMananger():
    def __init__(self):
        self.nodes: dict[str, StateObj] = {}
        self.edges: dict[str, Edge] = {}
        self.undo_stack: list = []
        self.current_file: str | None = None
        self.unsaved: bool = False

    # class AddRootNode(se)

    def addRootNode(self, label, description=""):
        new_root_node = AnnotatedNode(RootNode,label, description)


