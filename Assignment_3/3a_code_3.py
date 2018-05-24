__author__  = "Maxwell Bo, Chantel Morris"

"""Assignment 3 - Dynamic Programming - Section A"""

from functools import lru_cache

#########
# UTILS #
#########

Days = range(1, 8)
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

# b Base delivery cost (cents)
BASE_DELIVERY_COST = 10 * 100

# e Bottle delivery cost (cents)
PER_BOTTLE_DELIVERY_COST = int(1.50 * 100)
# NB: we're converting int because we don't want floating point instabilities

# r Bottle retail price (cents)
RETAIL_PRICE = 5 * 100

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
    return clamp(0, s + a - Demand[t], FRIDGE_CAPACITY)

def BottlesSold(s: State, a: Action, t: Day): 
    return s - BottlesStored(s, a, t) 

def CostOfDelivery(s: State, a: Action, t: Action):
    if a > 0: 
        return BASE_DELIVERY_COST + PER_BOTTLE_DELIVERY_COST * a
    else: 
        return 0

@lru_cache(maxsize=4096)
def Profit(s: State, t: Day):
    print(t)
    if t == LAST_DAY + 1:
        return 0

    return max(
        (RETAIL_PRICE * BottlesSold(s, a, t))
        - 
        CostOfDelivery(s, a, t)
        + 
        Profit(
            s=BottlesStored(s, a, t),
            t=(t + 1) # check the next day
        )
        # range is non-inclusive of the maxval, hence the + 1
        for a in range(MAXIMUM_DELIVERY_SIZE + 1)
    )

print(Profit(BASE_DELIVERY_COST, FIRST_DAY))