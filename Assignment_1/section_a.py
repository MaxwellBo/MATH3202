__author__  = "Mawell Bo, Chantel Morris"

"""Assignment 1 – Linear Programming - Section A – Report to your boss"""

from gurobipy import *

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

parsed = [ i.split() for i in table.strip().split('\n') ]

Quarter             = [     i[0]      for i in parsed ]
BrisbaneDemand     = [ int(i[1])     for i in parsed ]
MelbourneDemand    = [ int(i[2])     for i in parsed ]
AdelaideDemand     = [ int(i[3])     for i in parsed ]
Cost                = [ int(i[4][1:]) for i in parsed ]
# slicing `1:` to remove the dollar sign

assert(len(Quarter) == 8)
Q = range(len(Quarter))

Cities = [ "Brisbane", "Melbourne", "Adelaide" ]
C = range(len(Cities))

BRISBANE_BARRELS = 3200
MELBOURNE_BARRELS = 4000
ADELAIDE_BARRELS = 3800

Demand = [ BrisbaneDemand, MelbourneDemand, AdelaideDemand ]
InitialSupply = [ BRISBANE_BARRELS, MELBOURNE_BARRELS, ADELAIDE_BARRELS ]

SHIP_CAPACITY = 10000

STORAGE_COST_PER_QUARTER = 25

###############################################################################

m = Model("Pure Fresh")

X = {}
for c in C:
    for q in Q:
        # make a variable representing the number of barrels shipped to each
        # city in each quarter
        X[(c, q)] = m.addVar(vtype=GRB.INTEGER)

def number_in_storage(c, q):
    if q == 0: # AKA "Q1" 
        return InitialSupply[c] - Demand[c][q]
    else:
        new_supply = X[(c, q)]
        return number_in_storage(c, q - 1) + new_supply - Demand[c][q]

cost_function = quicksum(
    number_in_storage(c, q) * STORAGE_COST_PER_QUARTER
    +
    X[(c, q)] * Cost[c]
    for c in C for q in Q
)

m.setObjective(cost_function, GRB.MINIMIZE)

# "Each quarter..."
for q in Q:
    # "...we use a single ship for imports ... with a capacity of 10 000 barrels"
    m.addConstr(quicksum(X[(c, q)] for c in C) <= SHIP_CAPACITY)

m.optimize()

###############################################################################

for q in Q:
    print(Quarter[q], *[X[(c, q)].x for c in C])

print("Optimal cost:", m.objVal)
