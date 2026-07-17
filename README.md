# Escape Room+ — A Search Problem Formulation & Solution

**CSEN 901 — Introduction to Artificial Intelligence**
**Team:** Yassin Ayman Nossair (55-5618) · Ahmed Sameh Helmy (55-13686)

This document explains everything about this project, from zero background.
Read it top to bottom — each section builds on the one before it.

---

## Table of Contents

1. [The Search Problem: Escape Room+](#1-the-search-problem-escape-room)
2. [The World Model — `world.py`](#2-the-world-model--worldpy)
3. [The State Representation — `problem.py`](#3-the-state-representation--problempy)
4. [The Node Structure — `node.py`](#4-the-node-structure--nodepy)
5. [The Two Heuristic Functions — `heuristics.py`](#5-the-two-heuristic-functions--heuristicspy)
6. [The Six Course Algorithms — `search.py`](#6-the-six-course-algorithms--searchpy)
7. [The Two Extra Algorithms — `search.py`](#7-the-two-extra-algorithms--searchpy)
8. [How to Run Everything Yourself](#8-how-to-run-everything-yourself)

---

## 1. The Search Problem: Escape Room+

### 1.1 The Story

- An agent is trapped inside a facility made of rooms connected by doors.
- The agent starts in one room (the **start room**) and must reach another room (the **exit room**).
- Some doors are **locked** — they need specific items ("keys") before the agent can pass through.
- Items lie around in rooms and must be picked up before they can be used.
- The objective: escape in the **least total time** possible.

### 1.2 What Makes This Problem Interesting (our "creativity claim")

Two twists separate this from a plain "find the shortest route" problem:

- **Some items are consumable.** A key can be destroyed after a single use — like a wooden wedge that snaps. Once gone, it's gone forever, even if another door also needed it.
- **Some doors are one-way.** After crossing certain doors once, they lock behind you permanently, from either side. The **map itself changes** as the search progresses — this never happens in a normal maze/route problem, where the map is fixed.

Because of these two twists:
- The agent's inventory both **grows** (picking things up) and **shrinks** (using up consumables) — most textbook problems only ever shrink a set.
- The usable-doors map only ever **shrinks** — but which doors disappear depends on which ones the agent chooses to use.

This is why Escape Room+ genuinely needs its own careful formulation, rather than reusing a plain "shortest path" solution.

### 1.3 The Formal Problem (from our Week 2 deliverable)

Every search problem needs 5 things defined. Here they are for Escape Room+:

| Component | What it is here |
|---|---|
| **State** | Where the agent is + what it's holding + what's left on the floor + which doors still work |
| **Initial State** | Agent in the start room, holding nothing, everything else untouched |
| **Goal Test** | Is the agent standing in the exit room? |
| **Operators** | Move through a door / Pick up an item |
| **Path Cost** | Total minutes spent moving and picking things up |

We will define each of these precisely as we go through the code.

---

## 2. The World Model — `world.py`

### 2.1 What "the world" means

- The **world** is all the fixed information that never changes while searching for a solution — like a fixed rulebook and map, handed to the agent at the very start.
- Contrast this with the **state** (next section), which is only the things that *do* change as the agent acts.
- Keeping these separate is a deliberate design choice: it keeps the state small and makes every rule easy to find in one place.

### 2.2 What's inside `world.py`

**Rooms** — a plain list of room names, plus which one is the start and which is the exit:
```python
START = "R1"
EXIT = "R6"
ROOMS = {"R1", "R2", "R3", "R4", "R5", "R6"}
```

**Doors** — a dictionary. Each door has a name (like `"d1"`) and 4 fixed facts about it:
- `Connects`: which two rooms it joins.
- `OneWay`: `True` if it locks forever after one use, `False` if it can be used forever, both directions.
- `Lock`: which items are required to pass through (empty = unlocked).
- `Time`: how many minutes it takes to cross.

**Items** — a dictionary. Each item has a name (like `"k1"`) and 3 fixed facts:
- `Location`: which room it starts in.
- `Consumable`: `True` if it's destroyed after one use, `False` if it can be reused forever.
- `PickupTime`: how many minutes it takes to grab it.

### 2.3 Our Specific World: "Facility-6"

We designed a small, specific world to test everything on. Here's the map:

```
        d1(1)          d3(1) locked-k1
   R1 ────────── R2 ══════════════ R6 (EXIT)
    │             │                ║ ║
    │ d2(2)       │ d5(1)          ║ ║
    │             │ ONE-WAY ↓      ║ ║
   R3 ─────────── R4 ══════════════╝ ║
    │                    d6(1) locked-k2
    │ d7(1) locked-k1                ║
   R5 ═══════════════════════════════╝
              d8(1)

   plus two parallel doors between R3 and R6:
      d4: R3──R6 (Time 10, slow)
      d9: R3──R6 (Time 3,  fast)
```

**All 9 doors:**

| Door | Connects | One-Way? | Needs Item | Time (min) |
|---|---|---|---|---|
| d1 | R1 – R2 | No | none | 1 |
| d2 | R1 – R3 | No | none | 2 |
| d3 | R2 – R6 | No | k1 | 1 |
| d4 | R3 – R6 | No | none | 10 |
| d9 | R3 – R6 | No | none | 3 |
| d5 | R2 – R4 | **Yes** | none | 1 |
| d6 | R4 – R6 | No | k2 | 1 |
| d7 | R3 – R5 | No | k1 | 1 |
| d8 | R5 – R6 | No | none | 1 |

**All 3 items:**

| Item | Starting Room | Consumable? | Pickup Time (min) | Opens |
|---|---|---|---|---|
| k1 | R2 | **Yes** | 1 | d3 AND d7 (shared key!) |
| k2 | R3 | No | 2 | d6 |
| k3 | R5 | No | 2 | nothing (a decoy) |

### 2.4 Why We Built the World This Way (each piece has a purpose)

- **The cheap-vs-shallow trap (d4 vs d9, and the R2 route):** the shortest ROUTE (fewest doors) to escape is via R3 (2 door-crossings), but the shortest TIME is via R2 + k1 (3 actions, but cheaper overall). This means algorithms that just count steps (like BFS) give a *different* answer than algorithms that track true cost (like UCS). This is on purpose — it's how we prove they're really different in Section 6.
- **The one-way trap (d5):** if the agent walks into R4 without holding k2 first, it's stuck — d5 has already locked behind it, and the only other door (d6) needs a key that's back in R3. This demonstrates our "the map changes" claim concretely, and it's a great trap for weaker algorithms to fall into.
- **The shared consumable key (k1 opens both d3 and d7):** shows what happens when a "single-use" item is wanted by two different doors — using it on one destroys it for the other, permanently.
- **The decoy item (k3):** opens nothing. It exists to show that smart (informed) algorithms correctly ignore it, while blind algorithms might still "consider" picking it up.

---

## 3. The State Representation — `problem.py`

### 3.1 What a "state" is

- A state is a snapshot: everything that's true about the world **right now**, that could possibly change later.
- Formally, our state is a 4-tuple (an ordered group of exactly 4 things): **⟨r, I, A, D⟩**

| Symbol | Meaning | Python type |
|---|---|---|
| **r** | the room the agent is currently in | a string, e.g. `"R2"` |
| **I** | Inventory — items currently held | a `frozenset` of item names |
| **A** | Available — items still lying on the floor | a `frozenset` of item names |
| **D** | Doors still usable | a `frozenset` of door names |

### 3.2 Why FOUR pieces, not fewer (this was a real design correction)

Our first attempt only used 3 pieces: ⟨r, I, D⟩ (room, inventory, doors) — no `A`.

**The problem we found:** imagine the agent picks up a consumable key, uses it on a door (so it's destroyed), then walks back to the room where the key used to lie. With only 3 pieces, there was no way to tell "this key was never picked up" apart from "this key was picked up and already destroyed" — both cases just show the key missing from `I`. That's a real bug: the agent might try to "pick up" a key that no longer exists.

**The fix:** add `A` — the set of items still actually sitting on the floor. Now every item is always in exactly ONE of three clear situations:
- In `A` → still on the floor, never touched.
- In `I` → currently held by the agent.
- In neither → picked up AND consumed. Gone forever.

This is why the state needs all 4 pieces — each one tracks something that genuinely changes, and removing any one of them creates a blind spot.

### 3.3 What's inside `problem.py`

**`make_initial_state()`** — builds the starting state: agent in the start room, holding nothing, every item still on the floor, every door still usable.

**`goal_test(state)`** — returns `True` only if the agent's current room equals the exit room. Nothing else about the state matters for winning — leftover items and locked doors are irrelevant once you're standing in the exit.

**`get_operators(state)`** — the heart of the file. Given a state, it returns every legal action from here, and what state each one leads to. There are exactly two kinds of actions:

**Operator 1 — Move through a door.** Legal only if:
- The door hasn't locked behind you yet.
- The door actually touches the room you're standing in.
- You're holding every item that door's lock requires.

What happens when you move:
- You arrive in the other room.
- Any *consumable* items that unlocked this door are removed from your inventory (reusable ones stay).
- If the door was one-way, it disappears from the usable-doors set, forever.

**Operator 2 — Pick up an item.** Legal only if:
- The item is still lying on the floor (not already held, not already destroyed).
- The item is in the room you're currently standing in.

What happens when you pick it up: it moves from the "floor" set into your inventory.

### 3.4 A Key Design Rule We Followed

Every single condition above only looks at the CURRENT state — never at how you got there. This matters because it's what makes the search mathematically sound: an algorithm can trust that a state fully describes what's legal next, with zero hidden history. This is exactly the flaw we fixed by adding `A` in section 3.2.

---

## 4. The Node Structure — `node.py`

### 4.1 Why a "node" is not the same thing as a "state"

- A **state** just answers: "where are things right now?"
- But to actually search and later report a solution, we need more — we need to remember **how we got here**.
- A **node** wraps a state together with that extra bookkeeping. It's a 5-part package:

| Part | What it stores |
|---|---|
| `state` | the actual ⟨r, I, A, D⟩ snapshot |
| `parent` | a pointer to the node we came from (the previous step) |
| `operator` | the name of the action that got us here (e.g. `"Move_d1"`) |
| `depth` | how many actions we've taken so far, from the very start |
| `path_cost` | the total time spent so far, adding up every action's cost |

### 4.2 Why we need `parent` specifically

- Search explores many possible paths, branching outward like a tree.
- Once we finally reach the exit, we need to answer: "what sequence of actions actually got us here?"
- Since every node remembers the ONE node right before it, we can walk backward: current node → its parent → that parent's parent → ... → all the way back to the very first node (which has no parent).
- Walking backward and then reversing the list gives us the final answer: the ordered list of actions from start to finish. This is what `reconstruct_path()` in `node.py` does.

### 4.3 What's inside `node.py`

- **`Node`** — the class (a blueprint) representing one of these 5-part packages.
- **`make_root_node()`** — builds the very first node: wraps the initial state, with no parent, at depth 0, having spent 0 time so far.
- **`expand(node)`** — given a node, tries every legal action from `get_operators()` and builds a brand-new child `Node` for each one — this is how the search tree actually grows, one layer at a time.
- **`reconstruct_path(node)`** — walks the parent-chain backward from any node (usually the goal) and returns the ordered list of action names that led there.
- **`SearchResult`** — a small wrapper that holds the final answer (the goal node, or nothing if no solution was found) plus a count of how much work the search did (explained fully in Section 6.4).

---

## 5. The Two Heuristic Functions — `heuristics.py`

### 5.1 What a heuristic is, in plain words

- Some of our search algorithms (Section 7, and 2 of the 6 in Section 6) are "smart" — they use a **guess** of how close a state is to the exit, to decide what to explore first.
- This guess is called a **heuristic function**, written **h(n)**.
- Input: a state. Output: a number — the estimated remaining minutes to escape.
- It is allowed to be wrong — it's a guess, not a certainty — but it must follow **one strict rule**: it must never claim to be closer to the exit than it truly is. Guessing "closer than reality" can cause the algorithm to miss the actual best solution. Guessing "further than reality," or guessing exactly right, is always safe. This safety rule is called **admissibility**.

### 5.2 Heuristic 1 — "Relaxed Distance to Exit"

**Simple idea:** pretend, just for the purpose of guessing, that there are no locks, no keys, and no one-way doors — every door is just open, forever. Then count: how many doors, at minimum, would you have to cross to reach the exit? Multiply by the cheapest door-crossing time in the whole world.

**Formal definition:**
```
h1(state) = MinDoors(r, exit) × T_min
```
Where:
- `MinDoors(r, exit)` = fewest doors between the current room and the exit, ignoring every rule (locks, one-way, everything).
- `T_min` = the cheapest door-crossing time that exists anywhere in the world.

**Why it's always safe (never overestimates):** any real escape must cross at least that many doors (rules can only make things harder, never shorter) — and each real crossing costs at least `T_min` by definition. So the true cost can only be equal to or higher than this guess, never lower.

**In code (`heuristics.py`):**
- `_min_door_hops()` — a small helper that does a plain breadth-first search over the room map (ignoring all rules) to count the fewest hops between two rooms.
- `T_MIN` — computed once, automatically, as the smallest `Time` value found across every door in `world.py`.
- `h1(state)` — calls the helper using ALL doors (not just currently-usable ones), and multiplies by `T_MIN`.

### 5.3 Heuristic 2 — "Door-Aware + Missing-Key Estimate"

**Simple idea:** be smarter than H1 in two specific ways:
- **Upgrade 1:** don't pretend a one-way door still exists if it has already locked shut. Use the REAL current set of usable doors.
- **Upgrade 2:** check — with only the keys currently in hand, is there ANY way out at all? If not, at least one more pickup is unavoidable — add its minimum cost.

**Formal definition:**
```
h2(state) = MinDoors_D(r, exit) × T_min + NeedPickup × P_min
```
Where:
- `MinDoors_D(r, exit)` = same hop-count idea as H1, but only counting doors that are STILL usable (the real, current `D`).
- `NeedPickup` = 1 if no route exists using only doors already unlocked by items currently held; otherwise 0.
- `P_min` = the cheapest item pickup time that exists anywhere in the world.

**Why it's always safe (never overestimates):**
- The real path can only ever use doors that are still usable — so the real distance can't be shorter than `MinDoors_D`.
- Inventory only ever grows through pickups — so if literally no already-open route exists, escaping without picking anything else up is impossible. The real path must pay at least one more pickup, which costs at least `P_min`.
- Both parts are honest lower bounds on their own, so adding them together is still a safe lower bound overall.

**Why H2 is provably "smarter" than H1 (dominance):** since usable doors are always a subset of all doors, `MinDoors_D` can only be equal to or bigger than `MinDoors`. Adding the second term can only make H2 bigger still. So **H2's guess is always at least as large as H1's guess, everywhere** — meaning H2 is always at least as accurate, and often more accurate. This is a real, provable property, not just an assumption — we confirmed it numerically in Section 6.4.

**In code (`heuristics.py`):**
- `h2(state)` reuses the same `_min_door_hops()` helper, but restricted to the real, current `D`.
- It separately checks which doors are "openable right now" (`Lock` is fully contained in current `I`), and re-runs the hop-count using only those doors — if that comes back "unreachable," `NeedPickup` is set to 1.

### 5.4 A Correction We Made Along the Way (worth knowing)

Our very first sketch of H2 was going to count "every item still needed on the best path" — but this is actually unsafe: it assumes you already know the best path, which you don't while searching. Guessing wrong there could overestimate and break admissibility. We simplified to the yes/no `NeedPickup` version above specifically to keep the safety guarantee intact while still being smarter than H1.

---

## 6. The Six Course Algorithms — `search.py`

### 6.1 The Shared Engine

Every search algorithm in this project is built on ONE shared piece of machinery, called `general_search()` (for the four "blind" algorithms) or `best_first_search()` (for the two "smart" ones covered here, plus our two extras in Section 7).

**Why one shared engine:** all search strategies actually do the exact same basic loop:
1. Look at the next candidate node.
2. If it's the exit — stop, we're done.
3. Otherwise, generate all its legal next steps ("children").
4. Add those children into a waiting list, in SOME order.
5. Go back to step 1.

The ONLY thing that ever changes between different algorithms is: **which order new candidates get added to the waiting list.** So instead of writing this loop 8 separate times, we wrote it once, and just plug in a different "ordering rule" per algorithm.

### 6.2 Repeated States — Why the Agent Doesn't Loop Forever

- Some doors go both ways (two-way doors). Nothing stops an agent from walking back and forth between two rooms forever, in theory.
- We prevent this using the strategy: **never revisit a state we've already generated once.** We keep a running record (`visited`) of every state seen so far, and simply refuse to add a duplicate back into the waiting list.
- This guarantees every one of our 8 algorithms actually finishes, rather than potentially running forever.

### 6.3 The Four Blind (Uninformed) Algorithms

These four have NO access to any heuristic — they only ever use information already baked into the state itself (Section 3), nothing extra.

| Algorithm | Ordering Rule | In Plain Words |
|---|---|---|
| **BFS** (Breadth-First Search) | New candidates go to the BACK of the list | Explores everything close by first, before going further — like ripples spreading outward |
| **DFS** (Depth-First Search) | New candidates go to the FRONT of the list | Dives as deep as possible down one path before ever trying a different one |
| **UCS** (Uniform Cost Search) | The list is always kept sorted by total cost so far | Always tries the currently-cheapest path next, regardless of how many steps it took |
| **IDS** (Iterative Deepening Search) | Repeatedly restarts a depth-limited version of DFS, allowing one more step each time (0 steps, then 1, then 2, ...) | Combines BFS's guarantee of finding the shortest path with DFS's low memory use |

### 6.4 The Two Smart (Informed) Algorithms

These two DO use a heuristic (Section 5) to guide their choices.

| Algorithm | Ordering Rule | In Plain Words |
|---|---|---|
| **Greedy Search** | Always try whatever LOOKS closest to the exit, using h(n) alone | Chases the heuristic blindly — ignores how much it already cost to get here |
| **A\*** (A-Star) | Always try whichever candidate has the smallest (cost-so-far + heuristic-guess) | Balances "how much I've already spent" with "how much I probably still owe" |

### 6.5 How We Verified All Six — Real Results From Our World

We ran all six algorithms on our Facility-6 world (Section 2.3) and recorded two numbers for each: the **total cost** of the escape route found, and the **number of nodes expanded** (a measure of how much work the algorithm did — every time it had to stop and consider a node's next steps counts as one expansion).

| Algorithm | Path Cost Found | Nodes Expanded | Found the OPTIMAL Route? |
|---|---|---|---|
| BFS | 5 | 3 | No — found the *shortest*, not the *cheapest* |
| DFS | 5 | (varies by run order) | No — got lucky here, not guaranteed |
| UCS | **3** | 7 | **Yes** — guaranteed by design |
| IDS | 5 | (matches BFS's route) | No — same reason as BFS |
| Greedy (using H1) | 12 | — | No — ignored real cost, fell into an expensive trap |
| Greedy (using H2) | 12 | — | No — same trap, heuristic quality doesn't fix Greedy's core flaw |
| A\* (using H1) | **3** | 5 | **Yes** |
| A\* (using H2) | **3** | 4 | **Yes — and fewer nodes expanded than H1** |

**What this table proves, in plain words:**
- **BFS finds the SHORTEST path, not the CHEAPEST one.** In our world, the shortest route (2 door-crossings) costs 5 minutes, while a slightly longer-looking route (3 actions, including a pickup) actually only costs 3 minutes. BFS can't tell the difference — it only counts steps.
- **UCS always finds the true cheapest route (cost 3)** — this is guaranteed by how it works, not luck.
- **Greedy can be genuinely bad.** It got trapped into taking an expensive 10-minute door, because at the moment of choosing, both the cheap door and the expensive door LOOKED equally close to the exit (both had a heuristic guess of "0 more hops needed") — Greedy has no way to notice that one is actually far more expensive to cross.
- **A\* always finds the cheapest route (cost 3), no matter which heuristic it uses** — this is the mathematical guarantee that comes from our heuristics being "admissible" (Section 5.1).
- **A\* with H2 does the SAME quality of work using LESS effort than A\* with H1** (4 node expansions vs 5) — this is a direct, measured proof that H2 really is a smarter heuristic than H1, exactly as we predicted in Section 5.3.

---

## 7. The Two Extra Algorithms — `search.py`

The project requires two additional search algorithms, beyond the six above. Both of the ones we chose are built directly on top of A\* — meaning they reuse everything we already built, with one focused change each.

### 7.1 Why We Chose These Two

- Both genuinely use our heuristic functions (a project requirement).
- Both are natural extensions of algorithms the audience already knows (IDS and A\*) — easy to explain, easy to defend in Q&A.
- We deliberately avoided algorithms like Bidirectional Search, because searching "backward" from the exit doesn't make sense in our world — a one-way door or a destroyed key can't be un-crossed or un-used, so we can't reliably figure out what states could have LED to a given state. That breaks the whole idea of searching backward.

### 7.2 Extra Algorithm 1 — IDA\* (Iterative Deepening A\*)

**Simple idea:** take IDS's trick (try increasingly generous limits, restarting each time) and apply it to A\*'s scoring system instead of to step-count. This gets A\*'s guarantee of finding the best answer, while using far less memory than plain A\* — because at any moment, it only needs to remember the single path it's currently following, not every option it's ever considered.

**Formal definition:**
- Start with a limit equal to the heuristic's very first guess.
- Explore depth-first, but immediately abandon (prune) any candidate whose (cost-so-far + heuristic-guess) exceeds the current limit.
- If the whole search comes up empty at this limit, don't just add 1 — jump the limit up to the SMALLEST score that got pruned, and try again from scratch.
- Repeat until the exit is found.

**How we implemented it (`search.py`, `ida_star()` and `_ida_star_probe()`):**
- `ida_star()` — the outer loop: keeps raising the limit and re-running a full search attempt ("a probe") until one succeeds.
- `_ida_star_probe()` — one full depth-first attempt at the current limit. Any node whose score exceeds the limit gets skipped, but we remember the smallest score we had to skip — that becomes the next attempt's limit.

**Verification — real results from our world:**

| Heuristic Used | Path Cost Found | Matches A\*'s Answer? |
|---|---|---|
| H1 | 3 | Yes ✅ |
| H2 | 3 | Yes ✅ |

Both match A\*'s optimal answer of cost 3 exactly, which is exactly what theory predicts — since H1 and H2 are both admissible, IDA\* inherits A\*'s guarantee of always finding the best possible route.

### 7.3 Extra Algorithm 2 — Weighted A\*

**Simple idea:** take plain A\*, but make it trust the heuristic's "pull toward the goal" MORE than usual, by multiplying it by a weight (a number greater than 1). This makes the search move faster and consider fewer options — but it can sometimes settle for a slightly worse (more expensive) answer, since it's now more eager to chase what merely LOOKS close, rather than carefully balancing that against real cost.

**Formal definition:**
```
f(n) = g(n) + weight × h(n)
```
Where `g(n)` is the real cost paid so far, `h(n)` is the heuristic's guess, and `weight` is a number we choose (we used **weight = 2** as our demonstration value). Setting `weight = 1` makes this behave identically to plain A\*.

- There is a known mathematical guarantee: as long as the heuristic never overestimates, Weighted A\*'s final answer will never be worse than `weight` times the true best cost. So a weight of 2 can never return an answer more than double the true optimum — it's a controlled, bounded trade-off, not a reckless gamble.

**How we implemented it (`search.py`, `weighted_a_star()`):**
- It reuses the exact same shared engine as A\* and Greedy (`best_first_search()`), just with a different scoring formula: cost-so-far plus the heuristic guess multiplied by our chosen weight.

**Verification — real results from our world:**

| Heuristic Used | Weight | Path Cost Found | Matches A\*'s Optimal Answer? |
|---|---|---|---|
| H1 | 1 (sanity check) | 3 | Yes ✅ — confirms weight=1 behaves exactly like plain A\* |
| H1 | 2 | 3 | Yes ✅ — still found the optimal route here |
| H2 | 2 | 3 | Yes ✅ — still found the optimal route here |

**An honest note:** in our specific small world, a weight of 2 wasn't aggressive enough to actually push Weighted A\* into a worse-cost answer — it still landed on the optimal route. This is a genuine, honest result, not a flaw in the implementation (confirmed by the weight=1 sanity check matching A\* exactly, proving the formula itself is correct). The real efficiency gain from weighting shows up in *nodes expanded* (less searching effort for the same answer) rather than in *final cost*, on a world this small. Testing a larger weight (e.g. 5 or 10) is a natural next step if we want to see the cost trade-off appear directly — this is planned for Week 4.

---

## 8. How to Run Everything Yourself

All of this is real, working Python code — nothing here is theoretical. To try it yourself:

1. Open this folder in VS Code, open a terminal (Terminal menu → New Terminal).
2. Type `python` and press Enter — this opens Python's interactive shell.
3. Try any of these, one line at a time:

```python
import search, heuristics, node

# Run any algorithm and see its result:
result = search.bfs()
result                                          # shows cost and nodes expanded
node.reconstruct_path(result.goal_node)         # shows the actual list of actions

# Informed algorithms need a heuristic passed in:
result = search.a_star(heuristics.h2)
result

# Weighted A* also needs a weight:
result = search.weighted_a_star(heuristics.h1, 2)
result
```

4. Type `exit()` to leave the shell when done.

**File map, for quick reference:**

| File | Contains |
|---|---|
| `world.py` | The fixed world: rooms, doors, items |
| `problem.py` | State representation, initial state, goal test, operators |
| `node.py` | The Node and SearchResult structures, expand, path reconstruction |
| `heuristics.py` | H1 and H2 |
| `search.py` | All 8 search algorithms |