# trace_temp.py
# TEMPORARY diagnostic script — prints real node-by-node traces
# for IDA* and Weighted A*, for the Week 3 presentation slides.
# Not part of the committed codebase.

import problem
import node
import heuristics


def trace_ida_star(heuristic_fn, heuristic_name):
    print(f"\n=== IDA* trace using {heuristic_name} ===")
    root = node.make_root_node()
    limit = heuristic_fn(root.state)
    print(f"Initial limit = h(root) = {limit}")

    round_num = 1
    while True:
        print(f"\n--- Probe {round_num}, limit = {limit} ---")
        stack = [root]
        visited = {root.state}
        smallest_exceeding = float("inf")

        while stack:
            current = stack.pop()
            g = current.path_cost
            h = heuristic_fn(current.state)
            f = g + h
            room = current.state[0]

            if f > limit:
                print(f"  PRUNE  room={room} g={g} h={h} f={f} (> limit)")
                smallest_exceeding = min(smallest_exceeding, f)
                continue

            if problem.goal_test(current.state):
                print(f"  GOAL   room={room} g={g} h={h} f={f}")
                print(f"\nFound path: {node.reconstruct_path(current)}")
                print(f"Final cost: {current.path_cost}")
                return

            print(f"  EXPAND room={room} g={g} h={h} f={f} action={current.operator}")
            for child in node.expand(current):
                if child.state not in visited:
                    visited.add(child.state)
                    stack.append(child)

        if smallest_exceeding == float("inf"):
            print("No solution.")
            return
        limit = smallest_exceeding
        round_num += 1


def trace_weighted_a_star(heuristic_fn, heuristic_name, weight):
    print(f"\n=== Weighted A* trace using {heuristic_name}, weight={weight} ===")
    root = node.make_root_node()
    nodes = [root]
    visited = {root.state}

    while nodes:
        nodes.sort(key=lambda n: n.path_cost + weight * heuristic_fn(n.state))
        current = nodes.pop(0)
        g = current.path_cost
        h = heuristic_fn(current.state)
        f = g + weight * h
        room = current.state[0]

        if problem.goal_test(current.state):
            print(f"  GOAL   room={room} g={g} h={h} f={f} action={current.operator}")
            print(f"\nFound path: {node.reconstruct_path(current)}")
            print(f"Final cost: {current.path_cost}")
            return

        print(f"  EXPAND room={room} g={g} h={h} f={f} action={current.operator}")
        for child in node.expand(current):
            if child.state not in visited:
                visited.add(child.state)
                nodes.append(child)

    print("No solution.")


if __name__ == "__main__":
    trace_ida_star(heuristics.h2, "H2")
    trace_weighted_a_star(heuristics.h2, "H2", 2)