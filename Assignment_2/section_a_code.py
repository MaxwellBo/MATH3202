__author__  = "Maxwell Bo, Chantel Morris"

"""Assignment 2 - Integer Programming - Section A"""

from gurobipy import *
from collections import namedtuple

m = Model("Pure Fresh")

#########
# UTILS #
#########

def tabulate(xy):
    return [ row.split('\t') for row in xy.strip().split('\n') ]

#############
# CONSTANTS #
#############

# Thanks to your previous work, the average cost of reconstituted orange juice is $974 per thousand litres (kL).
ORANGE_JUICE_COST = 974

# We sell all juice produced for $1.50 per litre
SELL_PRICE_PER_LITRE = 1.50
SELL_PRICE_PER_KILOLITRE = 1.50 * 1000

# delivery trucks must always bring full loads of a single local fruit, 
# equivalent to 10 kL of processed juice per truck
TRUCK_LOAD_SIZE = 10

# Quarter   Brisbane
BRISBANE_FCOJ_SUPPLY_TABLE = """
Q1	1800
Q2	2100
Q3	2500
Q4	2400
Q5	1750
Q6	1950
Q7	2600
Q8	2700
"""

JUICE_TABLE = """
Orange Juice	100% Orange
Orange and Mango Juice	90% Orange, 10% Mango
Breakfast Juice	55% Apple, 28% Pineapple, 15% Orange, 2% Mango
Tropical Juice	65% Apple, 30% Pineapple, 4% Orange, 1% Passionfruit
Guava Delight	80% Apple, 10% Pineapple, 10% Guava
Orchard Medley	50% Apple, 45% Orange, 5% Mango
Strawberry Surprise	90% Apple, 8% Strawberry, 2% Guava
"""

GOURMET_JUICES = [ "Guava Delight", "Orchard Medley",  "Strawberry Surprise" ] 

# Fruit	Cost ($/kL)
COST_TABLE = """
Apple	620
Mango	1300
Pineapple	800
Passionfruit	1500
Guava	710
Strawberry	1370
""" + "Orange	{}".format(ORANGE_JUICE_COST)

# Q1	Q2	Q3	Q4	Q5	Q6	Q7	Q8
DEMAND_TABLE = """
973	872	1206	981	781	1055	1420	1236
311	347	469	389	329	363	484	568
682	707	838	938	586	788	1141	988
492	586	726	739	450	549	645	779
340	459	593	393	276	424	559	389
1151	621	697	909	1133	615	542	865
625	740	468	409	665	750	411	464
"""

########
# SETS #
########

Juice = [ row[0] for row in tabulate(JUICE_TABLE) ]
J = range(len(Juice))

Fruit = [ row[0] for row in tabulate(COST_TABLE) ]
F = range(len(Fruit))

Quarter = [ "Q" + str(i) for i in range(1, 9) ]
Q = range(len(Quarter))

########
# DATA #
########

Parts = namedtuple('Parts', Fruit)

def make_blend(cell):
    parts = cell.split(', ')
    # ['90% Orange', '10% Mango']

    # care with global
    defaults = { k: 0 for k in Fruit }

    overrides = {}

    for i in parts:
        percentage, ingredient = i.split()
        # "80%", "Apple"

        overrides[ingredient] = int(percentage[0:-1]) / 100 # -1 to strip %

    return Parts(**{**defaults, **overrides}) # bigg splatt

def get_blend_price(parts):
    return sum(parts[f] * Cost[f] for f in F)

Blend = [ make_blend(row[1]) for row in tabulate(JUICE_TABLE) ]

Cost = [ int(row[1]) for row in tabulate(COST_TABLE) ]

Demand = [ [ int(i) for i in row ] for row in tabulate(DEMAND_TABLE) ]

BrisbaneFCOJSupply = [ int(row[1]) for row in tabulate(BRISBANE_FCOJ_SUPPLY_TABLE) ]

Gourmet = [ 1 if Juice[j] in GOURMET_JUICES else 0 for j in J ]

#############
# VARIABLES #
#############

# make a variable representing the number of kL of a certain juice produced per quarter
# TODO: TYPE
X = { (j, q): m.addVar() for j in J for q in Q }

#############
# OBJECTIVE #
#############

profit_function = quicksum(
    (X[j, q] * SELL_PRICE_PER_KILOLITRE)
    -
    (X[j, q] * get_blend_price(Blend[j]))
    for j in J for q in Q
)

m.setObjective(profit_function, GRB.MAXIMIZE)

###############
# CONSTRAINTS #
###############

DoNotExceedDemand = {
    (j, q): m.addConstr(
        X[j, q] <= Demand[j][q]
    )
    for j in J for q in Q
}

DoNotExceedBrisbaneFCOJSupply = {
    q: m.addConstr(
        quicksum(X[j, q] * Blend[j].Orange for j in J) <= BrisbaneFCOJSupply[q]
    )
    for q in Q
}

#------------------------------------------------------------------------------#

def print_vars(communication):

    print()
    print(communication)
    print()
    print("Optimal cost: ${:,}".format(m.objVal))
    print()

#------------------------------------------------------------------------------#

m.optimize()
print_vars("Communication 4")
assert(round(m.objVal) == 26240836)

#-----------------------------------------------------------------------------#

# make a variable representing the number of trucks delivering a certain fruit per quarter
# TODO: TYPE
T = { (f, q): m.addVar(vtype=GRB.INTEGER) for f in F for q in Q }

profit_function = quicksum(
    (X[j, q] * SELL_PRICE_PER_KILOLITRE)
    for j in J for q in Q
) - quicksum(
    T[f, q] * TRUCK_LOAD_SIZE * Cost[f]
    for f in F[:-1] for q in Q
) - quicksum(
    X[j, q] * Blend[j].Orange * ORANGE_JUICE_COST
    for j in J for q in Q
)

m.setObjective(profit_function, GRB.MAXIMIZE)

DoNotExceedFruitTruckDelivery = {
    (f, q): m.addConstr(
        quicksum(X[j, q] * Blend[j][f] for j in J) <= T[f, q] * TRUCK_LOAD_SIZE
    )
    for f in F[:-1] for q in Q
}

m.optimize()
print_vars("Communication 5")
assert(round(m.objVal) == 26065453)

#-----------------------------------------------------------------------------#

G = { (j, q): m.addVar(vtype=GRB.BINARY) for j in J for q in Q  }

GourmetLatch = {
    q: m.addConstr(
        # if the juice is gourmet, and it's being used, it consumes a spot
        quicksum(Gourmet[j] and G[j, q] for j in J) == 2
    )
    for q in Q
}

OnlyTwoGourmet = {
    (j, q): m.addConstr(
        G[j, q] * X[j, q] == X[j, q] # essentially `if G then X else 0` 
    )
    for j in J for q in Q
}

m.optimize()
print_vars("Communication 6")
assert(round(m.objVal) == 23426440)