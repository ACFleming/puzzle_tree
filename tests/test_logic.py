"""
test_logic.py
=============
Run with:
    pytest test_logic.py -v
"""
import pytest
from puzzle_tree.node_logic import (
    StateObj, Edge, ORNode, ANDNode, NOTNode, SwitchNode, RootNode, LeafNode,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture
def root_edge_leaf():
    r = RootNode("D")
    e = Edge("E")
    l = LeafNode("S")
    StateObj.connect(r, e)
    StateObj.connect(e, l)
    return r, e, l

@pytest.fixture
def or_config():
    r1, r2 = RootNode("R1"), RootNode("R2")
    e1, e2 = Edge(), Edge()
    or_node = ORNode()
    e3 = Edge()
    leaf = LeafNode("L")
    StateObj.connect(r1, e1); StateObj.connect(r2, e2)
    StateObj.connect(e1, or_node); StateObj.connect(e2, or_node)
    StateObj.connect(or_node, e3); StateObj.connect(e3, leaf)
    return r1, r2, or_node, leaf

@pytest.fixture
def and_config():
    r1, r2 = RootNode("R1"), RootNode("R2")
    e1, e2 = Edge(), Edge()
    and_node = ANDNode()
    e3 = Edge()
    leaf = LeafNode("L")
    StateObj.connect(r1, e1); StateObj.connect(r2, e2)
    StateObj.connect(e1, and_node); StateObj.connect(e2, and_node)
    StateObj.connect(and_node, e3); StateObj.connect(e3, leaf)
    return r1, r2, and_node, leaf

@pytest.fixture
def not_config():
    r = RootNode()
    e1, e2 = Edge(), Edge()
    not_node = NOTNode("N")
    leaf_node = LeafNode("L")
    StateObj.connect(r, e1)
    StateObj.connect(e1, not_node)
    StateObj.connect(not_node, e2)
    StateObj.connect(e2, leaf_node)
    return r, e1, not_node, e2, leaf_node

@pytest.fixture
def switch_config():
    root = RootNode()
    e_in   = Edge()
    switch = SwitchNode()
    e_up, e_down       = Edge("up"), Edge("down")
    leaf_up, leaf_down = LeafNode(), LeafNode()
    StateObj.connect(root, e_in)
    StateObj.connect(e_in, switch)
    StateObj.connect(switch, e_up);   StateObj.connect(e_up,   leaf_up)
    StateObj.connect(switch, e_down); StateObj.connect(e_down, leaf_down)
    return root, e_in, switch, e_up, e_down, leaf_up, leaf_down

# ── Tests ─────────────────────────────────────────────────────────────────────

# Test Root Edge Leaf
@pytest.mark.parametrize("root_input,expected", [
    (False, False),
    (True, True)
])
def test_root_edge_leaf(root_edge_leaf, root_input, expected):
    root, edge, leaf = root_edge_leaf
    root.setState(root_input)
    assert edge.getState() == expected
    assert leaf.getState() == expected

@pytest.mark.parametrize("r1_input,r2_input,expected", [
    (False, False, False),
    (True,  False, True),
    (False, True,  True),
    (True,  True,  True),
])
# Test OR Node
def test_or_node(or_config, r1_input, r2_input, expected):
    r1, r2, or_node, leaf = or_config
    r1.setState(r1_input)
    r2.setState(r2_input)
    assert leaf.getState() == expected


@pytest.mark.parametrize("r1_input,r2_input,expected", [
    (False, False, False),
    (True,  False, False),
    (False, True,  False),
    (True,  True,  True),
])
    
# Test AND Node
def test_and_node(and_config, r1_input, r2_input, expected):
    r1, r2, and_node, leaf = and_config
    r1.setState(r1_input)
    r2.setState(r2_input)
    assert leaf.getState() == expected

@pytest.mark.parametrize("root_input,expected", [
    (False, True),
    (True, False)
])
def test_not_node(not_config, root_input, expected):
    root, e1,not_node, e2, leaf = not_config
    root.setState(root_input)
    assert leaf.getState() == expected

@pytest.mark.parametrize("root_input,switch_positions, expected_up, expected_down", [
    (False, {0:False,   1:False},   False,  False),
    (False, {0:False,   1:True},    False,  False),
    (False, {0:True,    1:False},   False,  False),
    (False, {0:True,    1:True},    False,  False),
    (True,  {0:False,   1:False},   False,  False),
    (True,  {0:False,   1:True},    False,  True),
    (True,  {0:True,    1:False},   True,   False),
    (True,  {0:True,    1:True},    True,   True),
])
def test_switch_node(switch_config, root_input,switch_positions, expected_up, expected_down):
    root, e_in, switch, e_up, e_down, leaf_up, leaf_down = switch_config
    switch.setSwitchState(switch_positions)
    root.setState(root_input)
    assert leaf_up.getState() == expected_up
    assert leaf_down.getState() == expected_down