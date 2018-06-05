__author__  = "Maxwell Bo, Chantel Morris"

"""Assignment 3 - Dynamic Programming - Section A"""

from collections import namedtuple
from typing import List

#########
# UTILS #
#########

Days = range(1, 7 + 1)
T = range(len(Days))

FIRST_DAY = T[0]
LAST_DAY = T[-1]

def tabulate(xy):
    return [ row.split('\t') for row in xy.strip().split('\n') ]

def clamp(minn, n, maxn):
    return max(min(maxn, n), minn)

#############
# CONSTANTS #
#############

DEMAND_TABLE = """
Day	1	2	3	4	5	6	7
Regular Demand	7	8	11	11	4	5	11
High Demand	13	12	15	13	9	9	18
"""

# m Maximum number of bottles that can be ordered
MAXIMUM_DELIVERY_SIZE = 15

# b Base delivery cost ($)
BASE_DELIVERY_COST = 10

# e Bottle delivery cost ($)
PER_BOTTLE_DELIVERY_COST = 1.50

# r Bottle retail price ($)
RETAIL_PRICE = 5

# i Number of bottles in the fridge on day 1
INITIAL_NUMBER_OF_BOTTLES = 0

# c Number of bottles fridge can hold
FRIDGE_CAPACITY = 10

# h Chance of having higher demand than usual
CHANCE_OF_HIGHER_DEMAND = 0.4

DISCOUNT = 0.1
# z Discounted retail price
DISCOUNTED_PRICE = (RETAIL_PRICE * (1 - DISCOUNT)) 

# p Chance of a high demand day post discount
CHANCE_OF_HIGHER_DEMAND_POST_DISCOUNT = 0.8

########
# DATA #
########

# d_t Demand of bottles on day t in T
# we've unpacked the the demand array for ease of use
RegularDemand: List[int] = [ int(i) for i in tabulate(DEMAND_TABLE)[1][1:] ]
HighDemand: List[int] = [ int(i) for i in tabulate(DEMAND_TABLE)[2][1:] ]

########
# MAIN #
########

State = namedtuple('State', ['bottles', 'day'])
INITIAL_STATE = State(INITIAL_NUMBER_OF_BOTTLES, FIRST_DAY)

Action = namedtuple('Action', ['ordered', 'discount'])

Communication = int

def delivery_cost(a: Action):
    if a.ordered > 0: 
        return BASE_DELIVERY_COST + PER_BOTTLE_DELIVERY_COST * a.ordered
    else: 
        return 0

def has_higher_demand(a: Action):
    return CHANCE_OF_HIGHER_DEMAND_POST_DISCOUNT if a.discount else CHANCE_OF_HIGHER_DEMAND

def decide_price(a: Action):
    return DISCOUNTED_PRICE if a.discount else RETAIL_PRICE

def decide_sold(s: State, a: Action, demand: List[int]):
    (bottles, day) = s
    (ordered, discount) = a

    # we either sell what is demanded, or sell our entire supply
    return min(demand[day], bottles + ordered)

def S(s: State, a: Action, demand: List[int]):
    (bottles, day) = s
    (ordered, discount) = a

    sold = decide_sold(s, a, demand)
    to_store = clamp(0, bottles + ordered - sold, FRIDGE_CAPACITY)

    return State(bottles=to_store, day=day + 1)

def C(s: State, a: Action, demand: List[int], c: Communication):
    price = decide_price(a)
    sold = decide_sold(s, a, demand)

    s_1 = S(s, a, demand)
    v_1 = V(s=s_1, c=c)[0]

    return (price * sold) - delivery_cost(a) + v_1

cache = {}

def V(s: State, c: Communication):
    if (s, c) in cache:
        return cache[s, c]

    if s.day == LAST_DAY + 1:
        return (0, None)

    # range is non-inclusive of the maxval, hence the + 1
    order_actions = range(MAXIMUM_DELIVERY_SIZE + 1)

    if c == 9:
        actions = [ Action(ordered=o, discount=False) for o in order_actions ]

        cache[(s, c)] = max(
            (C(s, a, RegularDemand, c), a)
            for a in actions
        )
    else:
        discount_actions = [True, False] if c == 11 else [False]
        actions = [ Action(ordered=o, discount=d) for o in order_actions for d in discount_actions]

        cache[(s, c)] = max(
            (
                (1 - has_higher_demand(a)) * C(s, a, RegularDemand, c) +\
                     has_higher_demand(a)  * C(s, a, HighDemand, c)
                ,
                a
            )
            for a in actions
        )

    return cache[s, c]

###########
# RESULTS #
###########

def probe_optimal(c: Communication):

    print("\t".join(i.rjust(6, " ") for i in ["Day", "Bottles", "Order"]))

    def go(s: State):
        (v, a) = cache[s, c]

        print("\t".join(str(i).rjust(6, " ") for i in [Days[s.day], s.bottles, a.ordered]))

        if s.day != LAST_DAY:
            go(S(s, a, RegularDemand))

            if c != 9:
                go(S(s, a, HighDemand))

    go(INITIAL_STATE)


def gen_table(c: Communication):
    all_states = [ State(bottles=b, day=d) for d in T for b in range(FRIDGE_CAPACITY + 1) ]

    rows = [[ "", *[ str(Days[d]) for d in T]]]

    for b in range(FRIDGE_CAPACITY + 1):
        row = [ str(b) ]

        for d in T:
            s = State(bottles=b, day=d)

            try:
                (v, a) = cache[s, c]
                contents = str(a.ordered) if c == 10 else ('D ' if a.discount else ' ') + str(a.ordered)
                row.append(contents)

            except Exception:
                row.append('')

        rows.append(row)

    print('\n'.join(['\t'.join([cell.rjust(8, ' ') for cell in row]) for row in rows]))

def gen_graph(s: State, c: Communication):

    def go(s: State, c: Communication):
        (v, a) = cache[s, c]

        if s.day != LAST_DAY:
            left = go(S(s, a, RegularDemand), c)
            right = go(S(s, a, HighDemand), c)

            builder = "node[circle,draw] {"
            builder += str((s.bottles, T[s.day]))
            builder += "} "
            builder += "edge from parent node[] {"
            builder += str((a.ordered, a.discount))
            builder += "}\n"

            if left:
                builder += "child {"
                builder += left
                builder += "}"

            else:
                builder += "child[missing]{}"

            builder += '\n'

            if right:
                builder += "child {"
                builder += right
                builder += "}"
            else:
                builder += "child[missing]{}"

            return builder
    
    builder = """\\begin{tikzpicture}[
  rotate=90,
  every node/.style={scale=.6},
  level distance=2cm,
  level 1/.style={sibling distance=13.6cm},
  level 2/.style={sibling distance=6.3cm},
  level 3/.style={sibling distance=3.cm},
  level 4/.style={sibling distance=1.7cm},
  level 5/.style={sibling distance=0.7cm}
  ]{
    """

    builder += "\\"

    builder += go(s, c)

    builder += """;
\end{tikzpicture}
"""
    return builder

for (comm, expected) in [
    (9, 156.0), 
    (10, 180.47),
    (11, 189.91)
]:
    p = V(INITIAL_STATE, comm)

    print(f"Communication {comm} - Profit is ${round(p[0], 2)} \n")

    if comm == 9:
        probe_optimal(comm)
    else:
        gen_table(comm)

    print('\n')