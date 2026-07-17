# problem.py
# State representation, initial state, goal test, and operators
# for Escape Room+ (Session 3, Parts a-d).

import world

# ----------------------------------------------------------------
# STATE: a tuple (r, I, A, D)
#   r = current room (string)
#   I = inventory (frozenset of item names)
#   A = available items on the floor (frozenset of item names)
#   D = usable doors (frozenset of door names)
# ----------------------------------------------------------------

def make_initial_state():
    """Builds <s, {}, Items, Doors> — Session 3, Part (b)."""
    r = world.START
    I = frozenset()                      # empty inventory
    A = frozenset(world.ITEMS.keys())    # all items still on the floor
    D = frozenset(world.DOORS.keys())    # all doors still usable
    return (r, I, A, D)


def goal_test(state):
    """True iff r = e — Session 3, Part (c)."""
    r, I, A, D = state
    return r == world.EXIT


def get_operators(state):
    """
    Returns a list of (action_name, new_state, cost) for every
    operator applicable in this state — Move_d and PickUp_i,
    Session 3, Part (d).
    """
    r, I, A, D = state
    operators = []

    # ---- OPERATOR 1: Move_d (one per door) ----
    for d_name in sorted(D):                        # M1: d in D
        door = world.DOORS[d_name]
        if r in door["Connects"]:             # M2: door touches current room
            if door["Lock"].issubset(I):       # M3: agent holds every required item
                # Compute result state
                rooms_pair = door["Connects"]
                r_prime = (rooms_pair - {r}).pop()   # the OTHER room

                used = {i for i in door["Lock"] if world.ITEMS[i]["Consumable"]}
                I_new = frozenset(I - used)

                if door["OneWay"]:
                    D_new = frozenset(D - {d_name})
                else:
                    D_new = D

                new_state = (r_prime, I_new, A, D_new)
                cost = door["Time"]
                operators.append((f"Move_{d_name}", new_state, cost))

    # ---- OPERATOR 2: PickUp_i (one per item) ----
    for i_name in sorted(A):                          # P1: i in A
        item = world.ITEMS[i_name]
        if item["Location"] == r:             # P2: item lies in current room
            I_new = frozenset(I | {i_name})
            A_new = frozenset(A - {i_name})
            new_state = (r, I_new, A_new, D)
            cost = item["PickupTime"]
            operators.append((f"PickUp_{i_name}", new_state, cost))

    return operators