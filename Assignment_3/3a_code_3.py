__author__  = "Maxwell Bo, Chantel Morris"

"""Assignment 3 - Dynamic Programming - Section A"""

from functools import lru_cache
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

# m Maximum number of bottles that can be sold
MAXIMUM_DELIVERY_SIZE = 15

DEMAND_TABLE = """
Day	1	2	3	4	5	6	7
Regular Demand	7	8	11	11	4	5	11
High Demand	13	12	15	13	9	9	18
"""

# h Chance of having higher demand than usual
CHANCE_OF_HIGHER_DEMAND = 0.4

########
# DATA #
########

Demand = List[int]
# d_t Demand of bottles for each day t in T
# global Demand # forgive me
RegularDemand: Demand = [ int(i) for i in tabulate(DEMAND_TABLE)[1][1:] ]
HighDemand: Demand = [ int(i) for i in tabulate(DEMAND_TABLE)[2][1:] ]

#########
# FUNCS #
#########

State = int     # the number of bottles we hold
Action = int    # the number of bottles we order
Day = int       # the day we're ordering the bottles on
Communication = int

def BottlesStored(s: State, a: Action, t: Day, d: Demand):
    return clamp(0, s + a - BottlesSold(s, a, t, d), FRIDGE_CAPACITY)
 
def BottlesSold(s: State, a: Action, t: Day, d: Demand): 
    # we either sell what is demanded, or sell our entire supply
    return min(d[t], s + a)

def CostOfDelivery(a: Action):
    if a > 0: 
        return BASE_DELIVERY_COST + PER_BOTTLE_DELIVERY_COST * a
    else: 
        return 0

def OptimalCost(s: State, t: Day, d: Demand, c: Communication):
    return max(
        -CostOfDelivery(a)
        +
        (RETAIL_PRICE * BottlesSold(s, a, t, d))
        + 
        Profit(
            s=BottlesStored(s, a, t, d),
            t=(t + 1), # check the next day
            c=c
        )
        # range is non-inclusive of the maxval, hence the + 1
        for a in range(MAXIMUM_DELIVERY_SIZE + 1)
    )


@lru_cache(maxsize=4096)
def Profit(s: State, t: Day, c: Communication):
    if t == LAST_DAY + 1:
        return 0

    if c == 9:
        return OptimalCost(s, t, RegularDemand, c)
    elif c == 10:
        return (1 - CHANCE_OF_HIGHER_DEMAND) * OptimalCost(s, t, RegularDemand, c) +\
        (CHANCE_OF_HIGHER_DEMAND) * OptimalCost(s, t, HighDemand, c)


p = Profit(INITIAL_NUMBER_OF_BOTTLES, FIRST_DAY, 9)
print(f"Communication 9 - Profit is {p}")

p = Profit(INITIAL_NUMBER_OF_BOTTLES, FIRST_DAY, 10)
print(f"Communication 10 - Profit is {p}")