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

# "the average cost of reconstituted orange juice is $974 per thousand litres (kL)."
ORANGE_JUICE_COST = 974

# "We sell all juice produced for $1.50 per litre"
SELL_PRICE_PER_LITRE = 1.50
SELL_PRICE_PER_KILOLITRE = 1.50 * 1000

# "delivery trucks must always bring full loads of a single local fruit, 
# equivalent to 10 kL of processed juice per truck"
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
    (SELL_PRICE_PER_KILOLITRE * X[j, q])
    -
    (sum(Blend[j][f] * Cost[f] for f in F) * X[j, q])
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

def print_vars(model, communication):
    print()
    print(communication)
    print()
    print("Optimal cost: ${:,}".format(model.objVal))
    print()

#------------------------------------------------------------------------------#

m.optimize()
print_vars(m, "Communication 4")
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
m.setParam("MIPGap", 0)

DoNotExceedFruitTruckDelivery = {
    (f, q): m.addConstr(
        quicksum(X[j, q] * Blend[j][f] for j in J) <= T[f, q] * TRUCK_LOAD_SIZE
    )
    for f in F[:-1] for q in Q
}

m.optimize()
print_vars(m, "Communication 5")
assert(round(m.objVal) == 26065453)

#-----------------------------------------------------------------------------#

G = { (j, q): m.addVar(vtype=GRB.BINARY) for j in J for q in Q  }

LimitOfTwoGourmetProduced = {
    q: m.addConstr(
        # if the juice is gourmet, and it's being used, it consumes a spot
        quicksum(Gourmet[j] and G[j, q] for j in J) == 2
    )
    for q in Q
}

PreventThirdGourmetProduction = {
    (j, q): m.addConstr(
        G[j, q] * X[j, q] == X[j, q] # essentially `if G then X else 0` 
    )
    for j in J for q in Q
}

m.optimize()
print_vars(m, "Communication 6")
assert(round(m.objVal) == 23426440)

#-----------------------------------------------------------------------------#

ProduceOnePerTwoQuarters = {
    (j, q): m.addConstr(
        G[j, q] + G[j, q + 1] >= 1
    )
    for j in J for q in Q[:-1]
}

m.optimize()
print_vars(m, "Communication 7")
assert(round(m.objVal) == 23206548)

#-----------------------------------------------------------------------------#

n = Model("Pure Fresh")

#############
# CONSTANTS #
#############

TRAVEL_COST_TABLE =  """
    D	1	2	3	4	5	6	7	8	9	10
D	—	68	222	117	102	71	131	133	146	166	16
1	68	—	269	98	144	138	198	180	214	231	79
2	222	269	—	215	125	173	145	90	163	114	205
3	117	98	215	—	106	156	203	139	226	221	113
4	102	144	125	106	—	82	107	37	132	117	86
5	71	138	173	156	82	—	60	95	76	97	60
6	131	198	145	203	107	60	—	97	25	42	119
7	133	180	90	139	37	95	97	—	122	94	117
8	146	214	163	226	132	76	25	122	—	51	136
9	166	231	114	221	117	97	42	94	51	—	153
10	16	79	205	113	86	60	119	117	136	153	—
"""

########
# SETS #
########

Location = tabulate(TRAVEL_COST_TABLE)[0]
L = range(len(Location))

########
# DATA #
########

def parse_cell(x): return sys.maxsize if x == '—' else int(x)

Cost = [ [ parse_cell(col) for col in row[1:] ] for row in tabulate(TRAVEL_COST_TABLE)[1:] ]

#############
# VARIABLES #
#############

# from, to
T = { (f, t): n.addVar(vtype=GRB.BINARY) for f in L for t in L }

#############
# OBJECTIVE #
#############

cost_function = quicksum(
    T[f, t] * Cost[f][t]
    for f in L for t in L
)

n.setObjective(cost_function, GRB.MINIMIZE)

###############
# CONSTRAINTS #
###############

DepartFromEachLocationOnce = {
    t: n.addConstr(
        quicksum(T[f, t] for f in L) == 1
    )
    for t in L
}

ArriveAtEachLocationOnce = {
    f: n.addConstr(
        quicksum(T[f, t] for t in L) == 1
    )
    for f in L
}

NoTwoLocationLoops = {
    (f, t): n.addConstr(
        T[f, t] + T[t, f] <= 1
    )
    for f in L for t in L
}

n.optimize()
print_vars(n, "Communication 8")
assert(n.objVal == 725)

for f in L:
    print(' '.join("{}->{}".format(f, t) if int(T[f, t].x) else '     ' for t in L))