# search.py
# GENERAL-SEARCH (Lecture 2, Concept 4) + all 8 algorithms.
# Repeated states handled via strategy #3: never revisit a
# generated state (Lecture 2, Concept 15; Session 3 commitment).
# Every function now returns a node.SearchResult, which tracks
# nodes_expanded for Week 4 comparisons.

import problem
import node


def general_search(queuing_function):
    """GENERAL-SEARCH(problem, QING-FUN) — Lecture 2, Concept 4."""
    root = node.make_root_node()
    nodes = [root]
    visited = {root.state}
    expanded_count = 0

    while nodes:
        current = nodes.pop(0)

        if problem.goal_test(current.state):
            return node.SearchResult(current, expanded_count)

        expanded_count += 1
        children = node.expand(current)

        new_children = []
        for child in children:
            if child.state not in visited:
                visited.add(child.state)
                new_children.append(child)

        nodes = queuing_function(nodes, new_children)

    return node.SearchResult(None, expanded_count)


def enqueue_at_end(nodes, children):
    return nodes + children


def bfs():
    return general_search(enqueue_at_end)


def enqueue_at_front(nodes, children):
    return children + nodes


def dfs():
    return general_search(enqueue_at_front)


def ordered_insert(nodes, children):
    combined = nodes + children
    combined.sort(key=lambda n: n.path_cost)
    return combined


def ucs():
    return general_search(ordered_insert)


def depth_limited_search(limit):
    """DL-SEARCH — internal helper for IDS only, not standalone."""
    root = node.make_root_node()
    nodes = [root]
    visited = {root.state}
    expanded_count = 0

    while nodes:
        current = nodes.pop(0)

        if problem.goal_test(current.state):
            return current, expanded_count

        if current.depth < limit:
            expanded_count += 1
            children = node.expand(current)
            new_children = []
            for child in children:
                if child.state not in visited:
                    visited.add(child.state)
                    new_children.append(child)
            nodes = enqueue_at_front(nodes, new_children)

    return None, expanded_count


def ids(max_depth=50):
    total_expanded = 0
    for depth in range(max_depth + 1):
        result_node, count = depth_limited_search(depth)
        total_expanded += count
        if result_node is not None:
            return node.SearchResult(result_node, total_expanded)
    return node.SearchResult(None, total_expanded)


def best_first_search(f_function):
    """BEST-FIRST-SEARCH(problem, F) — Lecture 3, Concept 2."""
    root = node.make_root_node()
    nodes = [root]
    visited = {root.state}
    expanded_count = 0

    while nodes:
        nodes.sort(key=f_function)
        current = nodes.pop(0)

        if problem.goal_test(current.state):
            return node.SearchResult(current, expanded_count)

        expanded_count += 1
        children = node.expand(current)
        for child in children:
            if child.state not in visited:
                visited.add(child.state)
                nodes.append(child)

    return node.SearchResult(None, expanded_count)


def greedy(heuristic_fn):
    f = lambda n: heuristic_fn(n.state)
    return best_first_search(f)


def a_star(heuristic_fn):
    f = lambda n: n.path_cost + heuristic_fn(n.state)
    return best_first_search(f)


def ida_star(heuristic_fn):
    """IDA* — Iterative Deepening A*."""
    root = node.make_root_node()
    limit = heuristic_fn(root.state)
    total_expanded = 0

    while True:
        result_node, next_limit, count = _ida_star_probe(root, limit, heuristic_fn)
        total_expanded += count
        if result_node is not None:
            return node.SearchResult(result_node, total_expanded)
        if next_limit == float("inf"):
            return node.SearchResult(None, total_expanded)
        limit = next_limit


def _ida_star_probe(root, limit, heuristic_fn):
    stack = [root]
    visited = {root.state}
    smallest_exceeding = float("inf")
    expanded_count = 0

    while stack:
        current = stack.pop()

        f_current = current.path_cost + heuristic_fn(current.state)
        if f_current > limit:
            smallest_exceeding = min(smallest_exceeding, f_current)
            continue

        if problem.goal_test(current.state):
            return current, None, expanded_count

        expanded_count += 1
        for child in node.expand(current):
            if child.state not in visited:
                visited.add(child.state)
                stack.append(child)

    return None, smallest_exceeding, expanded_count


def weighted_a_star(heuristic_fn, weight):
    f = lambda n: n.path_cost + weight * heuristic_fn(n.state)
    return best_first_search(f)