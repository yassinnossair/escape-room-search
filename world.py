# world.py
# Facility-6 — the fixed world definition for Escape Room+
# This data NEVER changes during search (Session 3, Part 0).

# ROOMS
START = "R1"
EXIT = "R6"
ROOMS = {"R1", "R2", "R3", "R4", "R5", "R6"}

# DOORS
# Each door: Connects (pair of rooms), OneWay (bool),
#            Lock (set of required items), Time (positive number)
DOORS = {
    "d1": {"Connects": {"R1", "R2"}, "OneWay": False, "Lock": set(),      "Time": 1},
    "d2": {"Connects": {"R1", "R3"}, "OneWay": False, "Lock": set(),      "Time": 2},
    "d3": {"Connects": {"R2", "R6"}, "OneWay": False, "Lock": {"k1"},     "Time": 1},
    "d4": {"Connects": {"R3", "R6"}, "OneWay": False, "Lock": set(),      "Time": 10},
    "d9": {"Connects": {"R3", "R6"}, "OneWay": False, "Lock": set(),      "Time": 3},
    "d5": {"Connects": {"R2", "R4"}, "OneWay": True,  "Lock": set(),      "Time": 1},
    "d6": {"Connects": {"R4", "R6"}, "OneWay": False, "Lock": {"k2"},     "Time": 1},
    "d7": {"Connects": {"R3", "R5"}, "OneWay": False, "Lock": {"k1"},     "Time": 1},
    "d8": {"Connects": {"R5", "R6"}, "OneWay": False, "Lock": set(),      "Time": 1},
}

# ITEMS
# Each item: Location (room), Consumable (bool), PickupTime (positive number)
ITEMS = {
    "k1": {"Location": "R2", "Consumable": True,  "PickupTime": 1},
    "k2": {"Location": "R3", "Consumable": False, "PickupTime": 2},
    "k3": {"Location": "R5", "Consumable": False, "PickupTime": 2},
}