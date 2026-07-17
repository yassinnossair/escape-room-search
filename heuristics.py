# heuristics.py
# Heuristic 1 (relaxed distance to exit) and Heuristic 2
# (door-aware + missing-items estimate) — Phase 0, Step 2.

import world


def _min_door_hops(start_room, target_room, usable_doors):
    """
    Plain BFS over the ROOM MAP (not the search-state space).
    Returns the fewest number of doors needed to go from
    start_room to target_room, using only doors in usable_doors.
    Ignores locks, one-way rules, everything except connectivity.
    """
    if start_room == target_room:
        return 0

    frontier = [start_room]
    visited_rooms = {start_room}
    hops = 0

    while frontier:
        hops += 1
        next_frontier = []
        for room in frontier:
            for d_name in usable_doors:
                door = world.DOORS[d_name]
                if room in door["Connects"]:
                    other = (door["Connects"] - {room}).pop()
                    if other == target_room:
                        return hops
                    if other not in visited_rooms:
                        visited_rooms.add(other)
                        next_frontier.append(other)
        frontier = next_frontier

    return float("inf")   # target unreachable through usable_doors


# Precompute constants once (Session 3 / Step 2 definitions)
T_MIN = min(door["Time"] for door in world.DOORS.values())
P_MIN = min(item["PickupTime"] for item in world.ITEMS.values())


def h1(state):
    """
    Relaxed distance to exit — Phase 0, Step 2.
    Ignores locks, items, one-way rules entirely.
    h1 = MinDoors(r, e) * T_MIN
    """
    r, I, A, D = state
    hops = _min_door_hops(r, world.EXIT, set(world.DOORS.keys()))
    return hops * T_MIN


def h2(state):
    """
    Door-aware + missing-items estimate — Phase 0, Step 2.
    h2 = MinDoors_D(r, e) * T_MIN + NeedPickup * P_MIN
    """
    r, I, A, D = state

    # Upgrade 1: only count doors still usable (D), not all doors
    hops = _min_door_hops(r, world.EXIT, set(D))
    term1 = hops * T_MIN

    # Upgrade 2: is there a route using ONLY doors already openable
    # with our current inventory I (Lock(d) subset of I)?
    openable_doors = {
        d_name for d_name in D
        if world.DOORS[d_name]["Lock"].issubset(I)
    }
    openable_hops = _min_door_hops(r, world.EXIT, openable_doors)
    need_pickup = 1 if openable_hops == float("inf") else 0

    term2 = need_pickup * P_MIN
    return term1 + term2