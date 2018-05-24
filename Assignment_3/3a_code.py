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

# m Maximum number of bottles that can be sold
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

# d Discount on the retail price
NO_DISCOUNT = 0
DISCOUNT = 0.1

# p Chance of a high demand day post discount
CHANCE_OF_HIGHER_DEMAND_POST_DISCOUNT = 0.8

########
# DATA #
########

# d_t Demand of bottles for each day t in T
RegularDemand: List[int] = [ int(i) for i in tabulate(DEMAND_TABLE)[1][1:] ]
HighDemand: List[int] = [ int(i) for i in tabulate(DEMAND_TABLE)[2][1:] ]

########
# MAIN #
########

State = namedtuple('State', ['bottles', 'day'])
INITIAL_STATE = State(INITIAL_NUMBER_OF_BOTTLES, FIRST_DAY)

Action = namedtuple('Action', ['ordered', 'discount'])

Communication = int

def cost_of_delivery(ordered: int):
    if ordered > 0: 
        return BASE_DELIVERY_COST + PER_BOTTLE_DELIVERY_COST * ordered
    else: 
        return 0

def apply_discount(discount: int):
    return (RETAIL_PRICE * (1 - DISCOUNT)) if discount else RETAIL_PRICE

def estimate_chance_of_higher_demand(discount: int):
    return CHANCE_OF_HIGHER_DEMAND_POST_DISCOUNT if discount else CHANCE_OF_HIGHER_DEMAND

def will_sell(s: State, a: Action, demand: List[int]):
    (bottles, day) = s
    (ordered, discount) = a

    # we either sell what is demanded, or sell our entire supply
    return min(demand[day], bottles + ordered)

def S(s: State, a: Action, demand: List[int]):
    (bottles, day) = s
    (ordered, discount) = a

    sold = will_sell(s, a, demand)
    to_store = clamp(0, bottles + ordered - sold, FRIDGE_CAPACITY)

    return State(bottles=to_store, day=day + 1)

def C(s: State, a: Action, demand: List[int], c: Communication):
    (ordered, discount) = a

    retail_price = apply_discount(discount) 
    sold = will_sell(s, a, demand)

    s_1 = S(s, a, demand)
    v_1 = V(s=s_1, c=c)[0]

    return (retail_price * sold) - cost_of_delivery(ordered) + v_1

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
                (1 - estimate_chance_of_higher_demand(a.discount)) * C(s, a, RegularDemand, c) +\
                     estimate_chance_of_higher_demand(a.discount)  * C(s, a, HighDemand, c)
                ,
                a
            )
            for a in actions
        )

    return cache[s, c]

###########
# RESULTS #
###########

def probe_optimal(s: State, c: Communication):
    (v, a) = cache[s, c]

    print("When in state", s, "perform action", a)

    if s.day != LAST_DAY:
        probe_optimal(S(s, a, RegularDemand), c)

        if c != 9:
            probe_optimal(S(s, a, HighDemand), c)


for (comm, expected) in [
    (9, 156.0), 
    (10, 180.47),
    (11, 189.91)
]:
    p = V(INITIAL_STATE, comm)
    print(f"Communication {comm} - Profit is {p[0]}")
    assert(round(p[0], 2) == expected)
    probe_optimal(INITIAL_STATE, comm)
