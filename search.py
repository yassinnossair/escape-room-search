# search.py
# GENERAL-SEARCH (Lecture 2, Concept 4) + BFS (Concept 6)
# Repeated states handled via strategy #3: never revisit a
# generated state (Lecture 2, Concept 15; Session 3 commitment).

import problem
import node


def general_search(queuing_function):
    """
    GENERAL-SEARCH(problem, QING-FUN) — Lecture 2, Concept 4.
    queuing_function decides how new children are inserted into
    the 'nodes' queue. Returns the goal Node, or None if no
    solution exists.
    """
    root = node.make_root_node()
    nodes = [root]                      # MAKE-Q(MAKE-NODE(INIT-STATE))
    visited = {root.state}              # strategy #3: states already generated

    while nodes:                        # while nodes is not empty
        current = nodes.pop(0)          # REMOVE-FIRST(nodes)

        if problem.goal_test(current.state):   # GOAL-TEST
            return current                       # return node

        children = node.expand(current)         # EXPAND(node, OPERATORS)

        # Strategy #3: drop any child whose state was already generated
        new_children = []
        for child in children:
            if child.state not in visited:
                visited.add(child.state)
                new_children.append(child)

        nodes = queuing_function(nodes, new_children)   # QING-FUN(nodes, children)

    return None                         # failure — queue emptied, no goal found


def enqueue_at_end(nodes, children):
    """FIFO — Lecture 2, Concept 6. BFS's queuing function."""
    return nodes + children


def bfs():
    """BF-SEARCH(problem) = GENERAL-SEARCH(problem, ENQUEUE-AT-END)."""
    return general_search(enqueue_at_end)