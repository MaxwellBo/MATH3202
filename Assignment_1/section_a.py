__author__  = "Mawell Bo, Chantel Morris"

"""Assignment 1 - Linear Programming - Section A"""

from gurobipy import *

SHIP_CAPACITY = 10000

STORAGE_COST_PER_QUARTER = 25

BRISBANE_BARRELS = 3200
MELBOURNE_BARRELS = 4000
ADELAIDE_BARRELS = 3800

# Quarter	Brisbane	Melbourne	Adelaide	Cost
table = """
Q1	1800	2400	3200	$873
Q2	2100	3400	1800	$901
Q3	2500	2800	1700	$1010
Q4	2400	2200	2400	$992
Q5	1750	2500	2500	$1025
Q6	1950	3600	2200	$906
Q7	2600	2950	1850	$1011
Q8	2700	1350	1950	$1013
"""

lines = [ i.split() for i in table.strip().split('\n') ]

########
# SETS #
########
Quarter = [ i[0] for i in lines ]
Q = range(len(Quarter))

Cities = [ "Brisbane", "Melbourne", "Adelaide" ]
C = range(len(Cities))

########
# DATA #
########

InitialSupply = [ BRISBANE_BARRELS, MELBOURNE_BARRELS,  ADELAIDE_BARRELS ]

BrisbaneDemand      = [ int(i[1])     for i in lines ]
MelbourneDemand     = [ int(i[2])     for i in lines ]
AdelaideDemand      = [ int(i[3])     for i in lines ]
Demand =        [ BrisbaneDemand,   MelbourneDemand,    AdelaideDemand ]

Cost                = [ int(i[4][1:]) for i in lines ]
# slicing `1:` to remove the dollar sign

###############################################################################

m = Model("Pure Fresh")

X = {}
for c in C:
    for q in Q:
        # make a variable representing the number of barrels shipped to each
        # city in each quarter
        X[(c, q)] = m.addVar(vtype=GRB.INTEGER)

def barrels_getting_stored(c, q):
    new_supply = X[(c, q)]

    if q == 0: # AKA "Q1" 
        return InitialSupply[c] + new_supply - Demand[c][q]
    else:
        return barrels_getting_stored(c, q - 1) + new_supply - Demand[c][q]

cost_function = quicksum(
    barrels_getting_stored(c, q) * STORAGE_COST_PER_QUARTER
    +
    X[(c, q)] * Cost[c]
    for c in C for q in Q
)

m.setObjective(cost_function, GRB.MINIMIZE)

# "Each quarter..."
for q in Q:
    # "...we use a single ship for imports ... with a capacity of 10 000 barrels"
    m.addConstr(quicksum(X[(c, q)] for c in C) <= SHIP_CAPACITY)

for c in C:
    for q in Q:
        # kinda a nifty little trick here;
        # this ensures that demand is being met each quarter
        # (look at what barrels_getting_stored expresses)
        m.addConstr(barrels_getting_stored(c, q) >= 0)

m.optimize()

###############################################################################

columns = "{:>12} {:>12} {:>12} {:>12}"


print()
print(columns.format("Quarter", *Cities))

for q in Q:
    print(columns.format(Quarter[q], *[X[(c, q)].x for c in C]))

print()
print("Optimal cost: ${:,}".format(m.objVal))

###############################################################################

