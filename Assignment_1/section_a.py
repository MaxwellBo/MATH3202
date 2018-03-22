__author__  = "Maxwell Bo, Chantel Morris"

"""Assignment 1 - Linear Programming - Section A"""

from gurobipy import *

m = Model("Pure Fresh")

# "Each quarter we use a single ship for imports with a capacity of 10,000 barrels."
SHIP_CAPACITY = 10000

# "We currently have 
# 3200 barrels of frozen concentrated orange juice in Brisbane, 
# 4000 barrels in Melbourne, and 
# 3800 barrels in Adelaide."
BRISBANE_BARRELS = 3200
MELBOURNE_BARRELS = 4000
ADELAIDE_BARRELS = 3800

# "We can store any concentrate on hand at the end of a quarter for a cost of $25 per barrel."
STORAGE_COST_PER_QUARTER = 25

# "We have a maximum storage capacity of 
# 3900 barrels in Brisbane, 
# 5500 barrels in Melbourne and 
# 6700 barrels in Adelaide."
BRISBANE_MAXIMUM_CAPACITY = 3900
MELBOURNE_MAXIMUM_CAPACITY = 5500
ADELAIDE_MAXIMUM_CAPACITY = 6700

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

MaximumCapacity = [ BRISBANE_MAXIMUM_CAPACITY, MELBOURNE_MAXIMUM_CAPACITY, ADELAIDE_MAXIMUM_CAPACITY ]

#############
# VARIABLES #
#############

# make a variable representing the number of barrels delivered to each city in each quarter
X = { (c, q): m.addVar(vtype=GRB.INTEGER) for c in C for q in Q } 

# make a variable representing the number of barrels stored in each city at the end of each quarter
S = { (c, q): m.addVar(vtype=GRB.INTEGER) for c in C for q in Q} # stored

#############
# OBJECTIVE #
#############
cost_function = quicksum(
    S[c, q] * STORAGE_COST_PER_QUARTER
    +
    X[c, q] * Cost[q]
    for c in C for q in Q
)

m.setObjective(cost_function, GRB.MINIMIZE)

###############
# CONSTRAINTS #
###############

first_quarter = Q[0]

BaseStored = {
    c: m.addConstr(
        InitialSupply[c] + X[c, q] - Demand[c][q] == S[c, q]
    )
    for c in C for q in [ first_quarter ]
}

InductiveStored = {
    (c, q): m.addConstr(
        S[c, q - 1] + X[c, q] - Demand[c][q] == S[c, q]
    )
    for c in C for q in Q[1:] # everything but the first quarter
}

ShipCapacity = {
    # ...we use a single ship for imports ... with a capacity of 10 000 barrels"
    q: m.addConstr(
        quicksum(X[c, q] for c in C) <= SHIP_CAPACITY
    )
    for q in Q  # "Each quarter...
}

################################################################################

def print_vars(communication):
    columns = "{:>12} {:>12} {:>12} {:>12}"

    print()
    print(communication)

    for (stage, var) in [ ("Deliveries", X), ("Stored", S) ]:
        print()
        print(stage)
        print()
        print(columns.format("Quarter", *Cities))

        for q in Q:
            print(columns.format(Quarter[q], *[int(var[c, q].x) for c in C]))

    print()
    print("Optimal cost: ${:,}".format(m.objVal))
    print()

################################################################################

m.optimize()
print_vars("Communication 1")

################################################################################

last_quarter = Q[-1]

LastQuarterStorage = {
    c: m.addConstr(
        # "...it would be desirable to end up with at least 3000 barrels in storage in each port."
        S[c, last_quarter] >= 3000,
        "LastQuarterStorage"
    )
    for c in C
}

m.optimize()
print_vars("Communication 2")

################################################################################

MaximumCapacity = {
    (c, q): m.addConstr(
        # "...ensure that we do not exceed the capacities of our facilities in each port."
        S[c, q] <= MaximumCapacity[c],
        "MaximumCapacity"
    )
    for c in C for q in Q
}

m.optimize()
print_vars("Communication 3")

# for (i, c) in ShipCapacity.items():
#     print(c.SARHSUp)
#     print(c.SARHSLow)

################################################################################

"""
Communicaton 1

Deliveries

     Quarter     Brisbane    Melbourne     Adelaide
          Q1            0         2200         7800
          Q2         3200         6800            0
          Q3            0            0            0
          Q4         4150          300            0
          Q5            0            0            0
          Q6         1950         5850         2200
          Q7         2600          700         1850
          Q8         2700         1350         1950

Stored

     Quarter     Brisbane    Melbourne     Adelaide
          Q1         1400         3800         8400
          Q2         2500         7200         6600
          Q3            0         4400         4900
          Q4         1750         2500         2500
          Q5            0            0            0
          Q6            0         2250            0
          Q7            0            0            0
          Q8            0            0            0

Optimal cost: $43,704,050.00
"""

"""
Communication 2

Deliveries

     Quarter     Brisbane    Melbourne     Adelaide
          Q1            0         2200         7800
          Q2         7500         2500            0
          Q3            0            0            0
          Q4            0         4600            0
          Q5            0            0            0
          Q6         4200         3600         2200
          Q7          200         7300         2500
          Q8         5700            0         4300

Stored

     Quarter     Brisbane    Melbourne     Adelaide
          Q1         1400         3800         8400
          Q2         6800         2900         6600
          Q3         4300          100         4900
          Q4         1900         2500         2500
          Q5          150            0            0
          Q6         2400            0            0
          Q7            0         4350          650
          Q8         3000         3000         3000

Optimal cost: $53,169,450.0
"""

"""
Communication 3

Deliveries

     Quarter     Brisbane    Melbourne     Adelaide
          Q1            0         3900         6100
          Q2         4600         3400         1800
          Q3            0            0            0
          Q4         2750         2000           50
          Q5            0            0            0
          Q6         1950         3600         4450
          Q7         6500         3500            0
          Q8         1800         3800         4400

Stored

     Quarter     Brisbane    Melbourne     Adelaide
          Q1         1400         5500         6700
          Q2         3900         5500         6700
          Q3         1400         2700         5000
          Q4         1750         2500         2650
          Q5            0            0          150
          Q6            0            0         2400
          Q7         3900          550          550
          Q8         3000         3000         3000

Optimal cost: $53,177,650.0
"""
