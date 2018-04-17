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

blend_table = """
Orange Juice	100% Orange
Orange and Mango Juice	90% Orange, 10% Mango
Breakfast Juice	55% Apple, 28% Pineapple, 15% Orange, 2% Mango
Tropical Juice	65% Apple, 30% Pineapple, 4% Orange, 1% Passionfruit
Guava Delight	80% Apple, 10% Pineapple, 10% Guava
Orchard Medley	50% Apple, 45% Orange, 5% Mango
Strawberry Surprise	90% Apple, 8% Strawberry, 2% Guava
"""

# Fruit	Cost ($/kL)
cost_table = """
Apple	620
Mango	1300
Pineapple	800
Passionfruit	1500
Guava	710
Strawberry	1370
""" + "Orange	{}".format(ORANGE_JUICE_COST)

# Q1	Q2	Q3	Q4	Q5	Q6	Q7	Q8
demand_table = """
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

Juices = [ row[0] for row in tabulate(blend_table) ]
J = range(len(Juices))

Fruits = [ row[0] for row in tabulate(cost_table) ]
F = range(len(Fruits))

Quarters = [ "Q" + str(i) for i in range(1, 9) ]
Q = range(len(Quarters))

########
# DATA #
########

Blend = namedtuple('Blend', Fruits)

def make_blend(cell):
    parts = cell.split(', ')
    # ['90% Orange', '10% Mango']

    # care with global
    defaults = { k: 0 for k in Fruits }

    overrides = {}

    for i in parts:
        percentage, ingredient = i.split()
        # "80%", "Apple"

        overrides[ingredient] = int(percentage[0:-1]) # -1 to strip percentage

    return Blend(**{**defaults, **overrides}) # bigg splatt

def get_blend_price(blend):
    return sum((blend[f] / 100) * Costs[f] for f in F)

Blends = [ make_blend(row[1]) for row in tabulate(blend_table) ]

Costs = [ int(row[1]) for row in tabulate(cost_table) ]

Demands = [ [ int(i) for i in row ] for row in tabulate(demand_table) ]

#############
# VARIABLES #
#############

# make a variable representing the number of kL of a certain juice produced per quarter
X = { (j, q): m.addVar() for j in J for q in Q }

#############
# OBJECTIVE #
#############

cost_function = quicksum(
    X[j, q] * SELL_PRICE_PER_KILOLITRE
    -
    X[j, q] * get_blend_price(Blends[j])
    for j in J for q in Q
)

m.setObjective(cost_function, GRB.MAXIMIZE)

###############
# CONSTRAINTS #
###############

DemandCeiling = {
    (j, q): m.addConstr(
        X[j, q] <= Demands[j][q]
    )
    for j in J for q in Q
}

def print_vars(communication):
    print()
    print(communication)
    print()
    print("Optimal cost: ${:,}".format(m.objVal))
    print()

m.optimize()
print_vars("Communication 4")


#-----------------------------------------------------------------------------#
