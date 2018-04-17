__author__  = "Maxwell Bo, Chantel Morris"

"""Assignment 2 - Integer Programming - Section A"""

from gurobipy import *
from collections import namedtuple

m = Model("Pure Fresh")

#########
# UTILS #
#########

def tabulate(xy):
    return [ y.split() for y in xy.strip().split('\n') ]

#############
# CONSTANTS #
#############

# Thanks to your previous work, the average cost of reconstituted orange juice is $974 per thousand litres (kL).
ORANGE_JUICE_COST = 974

# Fruit	Cost ($/kL)
cost_table = """
Apple	620
Mango	1300
Pineapple	800
Passionfruit	1500
Guava	710
Strawberry	1370
Orange {}
""".format(ORANGE_JUICE_COST)

# Quarter	Q1	Q2	Q3	Q4	Q5	Q6	Q7	Q8
demand_table = """
Orange Juice	973	872	1206	981	781	1055	1420	1236
Orange & Mango Juice	311	347	469	389	329	363	484	568
Breakfast Juice	682	707	838	938	586	788	1141	988
Tropical Juice	492	586	726	739	450	549	645	779
Guava Delight	340	459	593	393	276	424	559	389
Orchard Medley	1151	621	697	909	1133	615	542	865
Strawberry Surprise	625	740	468	409	665	750	411	464
"""

blend_table = """
Orange Juice	100% Orange
Orange and Mango Juice	90% Orange, 10% Mango
Breakfast Juice	55% Apple, 28% Pineapple, 15% Orange, 2% Mango
Tropical Juice	65% Apple, 30% Pineapple, 4% Orange, 1% Passionfruit
Guava Delight	80% Apple, 10% Pineapple, 10% Guava
Orchard Medley	50% Apple, 45% Orange, 5% Mango
Strawberry Surprise	90% Apple, 8% Strawberry, 2% Guava
"""

########
# SETS #
########

Fruits = [ i[0] for i in tabulate(cost_table) ]
F = range(len(Fruits))

Juices = [ i[0] for i in tabulate(demand_table) ]
J = range(len(Juices))

Quarters = [ "Q" + str(i) for i in range(1, 9) ]
Q = range(len(Quarters))




########
# DATA #
########

Blend = namedtuple('Blend', Fruits)

def make_blend(entry):
    parts = entry.split('\t')[1].split(', ')
    # ['90% Orange', '10% Mango']

    # care with global
    defaults = { k: 0 for k in Fruits }

    overrides = {}

    for i in parts:
        percentage, ingredient = i.split()
        # "80%", "Apple"

        overrides[ingredient] = int(percentage[0:-1]) # -1 to strip percentage

    return Blend(**{**defaults, **overrides})

Blends = [ make_blend(i) for i in blend_table.strip().split('\n') ]


#############
# VARIABLES #
#############

#############
# OBJECTIVE #
#############

###############
# CONSTRAINTS #
###############


#-----------------------------------------------------------------------------#
