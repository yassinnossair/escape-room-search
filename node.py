# node.py
# The Search Tree Node (Lecture 2, Concept 3) and the
# General Search Procedure skeleton (Lecture 2, Concept 4).

import problem


class SearchResult:
    """
    Wraps a completed search's outcome: the goal node found (or
    None if failure), plus the count of nodes expanded — our
    Week 4 comparison metric.
    """
    def __init__(self, goal_node, nodes_expanded):
        self.goal_node = goal_node
        self.nodes_expanded = nodes_expanded

    def __repr__(self):
        if self.goal_node is None:
            return f"SearchResult(FAILURE, nodes_expanded={self.nodes_expanded})"
        return (f"SearchResult(cost={self.goal_node.path_cost}, "
                f"nodes_expanded={self.nodes_expanded})")


class Node:
    """
    A search tree node — a 5-tuple, per Lecture 2 Concept 3:
    (state, parent, operator, depth, path_cost)
    """
    def __init__(self, state, parent, operator, depth, path_cost):
        self.state = state            # the state (r, I, A, D)
        self.parent = parent          # the Node we came from (None for root)
        self.operator = operator      # the action name, e.g. "Move_d1"
        self.depth = depth            # steps from the root
        self.path_cost = path_cost    # accumulated cost so far (g(n))

    def __repr__(self):
        # How this node prints when we look at it directly — for debugging.
        return f"Node(state={self.state}, depth={self.depth}, cost={self.path_cost})"


def make_root_node():
    """The root node: initial state, no parent, depth 0, cost 0."""
    s0 = problem.make_initial_state()
    return Node(state=s0, parent=None, operator=None, depth=0, path_cost=0)


def expand(node):
    """
    Generates all children of a node by applying every operator
    available in its state (Lecture 2, Concept 4, line 9: EXPAND).
    Returns a list of new Node objects.
    """
    children = []
    for action_name, new_state, step_cost in problem.get_operators(node.state):
        child = Node(
            state=new_state,
            parent=node,
            operator=action_name,
            depth=node.depth + 1,
            path_cost=node.path_cost + step_cost,
        )
        children.append(child)
    return children


def reconstruct_path(node):
    """
    Walks parent-pointers from a goal node back to the root,
    then reverses the result — giving the action sequence in order.
    """
    actions = []
    while node.parent is not None:
        actions.append(node.operator)
        node = node.parent
    actions.reverse()
    return actions