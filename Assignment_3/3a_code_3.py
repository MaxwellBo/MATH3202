__author__  = "Maxwell Bo, Chantel Morris"

"""Assignment 3 - Dynamic Programming - Section A"""

from functools import lru_cache

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
Demand	7	8	11	11	4	5	11
"""

########
# DATA #
########

# d_t Demand of bottles for each day t in T
Demand = [ int(i) for i in tabulate(DEMAND_TABLE)[1][1:] ]
assert(len(Demand) == 7)

#########
# FUNCS #
#########

State = int     # the number of bottles we hold
Action = int    # the number of bottles we order
Day = int       # the day we're ordering the bottles on

def BottlesStored(s: State, a: Action, t: Day):
    return clamp(0, s + a - BottlesSold(s, a, t), FRIDGE_CAPACITY)

def BottlesSold(s: State, a: Action, t: Day): 
    # we either sell what is demanded, or sell our entire supply
    return min(Demand[t], s + a)

def CostOfDelivery(a: Action):
    if a > 0: 
        return BASE_DELIVERY_COST + PER_BOTTLE_DELIVERY_COST * a
    else: 
        return 0

@lru_cache(maxsize=4096)
def Profit(s: State, t: Day):
    if t == LAST_DAY + 1:
        return 0

    return max(
        -CostOfDelivery(a)
        +
        (RETAIL_PRICE * BottlesSold(s, a, t))
        + 
        Profit(
            s=BottlesStored(s, a, t),
            t=(t + 1) # check the next day
        )
        # range is non-inclusive of the maxval, hence the + 1
        for a in range(MAXIMUM_DELIVERY_SIZE + 1)
    )

print(Profit(INITIAL_NUMBER_OF_BOTTLES, FIRST_DAY))