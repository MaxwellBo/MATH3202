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

# r Cost ($/kL) of reconstituted orange juice
# "the average cost of reconstituted orange juice is $974 per thousand litres (kL)."
ORANGE_JUICE_COST = 974

# s Sell price ($/kL) of any juice j in J
# "We sell all juice produced for $1.50 per litre"
SELL_PRICE_PER_LITRE = 1.50
SELL_PRICE_PER_KILOLITRE = 1.50 * 1000

# l Truck delivery size (kL) of any fruit f in F
# "delivery trucks must always bring full loads of a single local fruit, 
# equivalent to 10 kL of processed juice per truck"
TRUCK_DELIVERY_SIZE = 10

# NB: Parsing all data from tables reduced the number of transcription errors
#     significantly. I have opted to continue to do so.

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

GourmetJuice = [ "Guava Delight", "Orchard Medley",  "Strawberry Surprise" ] 
# We don't define a G here because we need to use J's indexes

Fruit = [ row[0] for row in tabulate(COST_TABLE) ]
F = range(len(Fruit))

DeliverableFruit = Fruit[:-1] # We don't need to deliver oranges
D = range(len(DeliverableFruit))

Quarter = [ "Q" + str(i) for i in range(1, 9) ]
Q = range(len(Quarter))

########
# DATA #
########

Parts = namedtuple('Parts', Fruit)

def make_blend(cell):
    parts = cell.split(', ')
    # ['90% Orange', '10% Mango']

    defaults = { k: 0 for k in Fruit }
    overrides = {}

    for i in parts:
        percentage, ingredient = i.split()
        # "80%", "Apple"

        overrides[ingredient] = int(percentage[0:-1]) / 100 # -1 to strip %

    return Parts(**{**defaults, **overrides}) # merge, then unpack

# p_jf Proportion in N[0,1] of fruit f in F in juice j in J
Proportion = [ make_blend(row[1]) for row in tabulate(JUICE_TABLE) ]

# c_f Cost ($/kL) of local fruit f in F
Cost = [ int(row[1]) for row in tabulate(COST_TABLE) ]

# d_jq Anticipated ability to sell kL of juice j in J in quarter q in Q
Demand = [ [ int(i) for i in row ] for row in tabulate(DEMAND_TABLE) ]

# b_q Demand of kL of orange juice in Brisbane in quarter q in Q
BrisbaneOJDemand = [ int(row[1]) for row in tabulate(BRISBANE_FCOJ_SUPPLY_TABLE) ]

#############
# VARIABLES #
#############

# Number of kL of juice j in J produced in quarter q in Q
X = { (j, q): m.addVar() for j in J for q in Q }

#############
# OBJECTIVE #
#############

profit_function = quicksum(
    (X[j, q] * SELL_PRICE_PER_KILOLITRE)
    -
    (X[j, q] * sum(Proportion[j][f] * Cost[f] for f in F))
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

DoNotExceedBrisbaneOJDemand = { 
    q: m.addConstr(
        quicksum(X[j, q] * Proportion[j].Orange for j in J) <= BrisbaneOJDemand[q]
    )
    for q in Q
}

#------------------------------------------------------------------------------#

def print_profit(communication, model):
    print()
    print()
    print(communication)
    print()
    print("Optimal profit: ${:,}".format(model.objVal))

def print_cost(communication, model):
    print()
    print()
    print(communication)
    print()
    print("Optimal cost: ${:,}".format(model.objVal))


def print_header(variable):
    cols = "{:>22} " + " ".join(["{:>6}"] * len(Quarter))

    print()
    print(variable)
    print()
    print(cols.format("", *Quarter))

    return cols

def print_production():
    cols = print_header("Production")

    for j in J:
        print(cols.format(Juice[j], *[int(X[j, q].x) for q in Q]))

def analyse_production():
    cols = print_header("Production sensitivity analysis (SAObjLow)")

    for j in J:
        print(cols.format(Juice[j], *[int(X[j, q].SAOBJLow) for q in Q]))
 
def print_trucks():
    cols = print_header("Trucks")

    for f in D:
        print(cols.format(Fruit[f], *[int(T[f, q].x) for q in Q]))

def print_gourmet_choice():
    cols = print_header("Gourmet Choice")

    for j in J:
        if Juice[j] in GourmetJuice:
            print(cols.format(Juice[j], *[int(G[j, q].x) for q in Q]))

def analyse_demand_slack():
    cols = print_header("Demand sensitivity analysis (Slack)")

    for j in J:
        print(cols.format(Juice[j], *[int(DoNotExceedDemand[j, q].slack) for q in Q]))

def analyse_demand_pi():
    cols = print_header("Demand sensitivity analysis (Pi)")

    for j in J:
        print(cols.format(Juice[j], *[int(DoNotExceedDemand[j, q].pi) for q in Q]))

def analyse_demand_sarhslow():
    cols = print_header("Demand supply sensitivity analysis (SARHSLow)")

    for j in J:
        print(cols.format("SARHSLow", *[int(DoNotExceedDemand[j, q].SARHSLow) for q in Q]))

def analyse_brisbane_supply_slack():
    cols = print_header("Brisbane supply sensitivity analysis (Slack)")

    print(cols.format("Slack", *[int(DoNotExceedBrisbaneOJDemand[q].slack) for q in Q]))

def analyse_brisbane_supply_pi():
    cols = print_header("Brisbane supply sensitivity analysis (Pi)")

    print(cols.format("Pi", *[int(DoNotExceedBrisbaneOJDemand[q].pi) for q in Q]))

def analyse_brisbane_supply_sarhslow():
    cols = print_header("Brisbane supply sensitivity analysis (SARHSLow)")

    print(cols.format("SARHSLow", *[int(DoNotExceedBrisbaneOJDemand[q].SARHSLow) for q in Q]))

def analyse_truck_slack():
    cols = print_header("Truck capacity ({}) (Slack)".format(TRUCK_DELIVERY_SIZE))

    for f in D:
        print(cols.format(Fruit[f], *["{0:.2f}".format(abs(DoNotExceedFruitTruckSupply[f, q].slack)) for q in Q]))

#------------------------------------------------------------------------------#

m.optimize()
print_profit("Communication 4", m)
print_production()
analyse_production()
analyse_demand_pi()
analyse_demand_sarhslow()
analyse_brisbane_supply_pi()
analyse_brisbane_supply_sarhslow()
assert(round(m.objVal) == 26240836)

#-----------------------------------------------------------------------------#

# Number of trucks delivering a given fruit f in F in quarter q in Q
T = { (f, q): m.addVar(vtype=GRB.INTEGER) for f in F for q in Q }

profit_function = quicksum(
    X[j, q] * SELL_PRICE_PER_KILOLITRE
    for j in J for q in Q
) - quicksum(
    T[f, q] * TRUCK_DELIVERY_SIZE * Cost[f]
    for f in D for q in Q
) - quicksum(
    X[j, q] * Proportion[j].Orange * ORANGE_JUICE_COST
    for j in J for q in Q
)

m.setObjective(profit_function, GRB.MAXIMIZE)
m.setParam("MIPGap", 0)

DoNotExceedFruitTruckSupply = {
    (f, q): m.addConstr(
        quicksum(X[j, q] * Proportion[j][f] for j in J) <= T[f, q] * TRUCK_DELIVERY_SIZE
    )
    for f in D for q in Q
}

m.optimize()
print_profit("Communication 5", m)
print_production()
print_trucks()
assert(round(m.objVal) == 26065453)

#-----------------------------------------------------------------------------#

G = { (j, q): m.addVar(vtype=GRB.BINARY) for j in J for q in Q  }

OnlyTwoGourmetProduced = {
    q: m.addConstr(
        # if the juice is gourmet, and it's being used, it consumes a spot
        quicksum(G[j, q] for j in J if Juice[j] in GourmetJuice) == 2
    )
    for q in Q
}

BindDecisionVariable = {
    (j, q): m.addConstr(
        X[j, q] <= G[j, q] * Demand[j][q] # redundant
    )
    for j in J for q in Q if Juice[j] in GourmetJuice
}

m.optimize()
print_profit("Communication 6", m)
print_production()
print_trucks()
print_gourmet_choice()
assert(round(m.objVal) == 23426440)

#-----------------------------------------------------------------------------#

ProduceOneGourmetPerTwoQuarters = {
    (j, q): m.addConstr(
        G[j, q] + G[j, q + 1] >= 1
    )
    for j in J for q in Q[:-1] if Juice[j] in GourmetJuice
}

m.optimize()
print_profit("Communication 7", m)
print_production()
print_trucks()
print_gourmet_choice()
analyse_demand_slack()
analyse_truck_slack()
analyse_brisbane_supply_slack()

assert(round(m.objVal) == 23206548)

#-----------------------------------------------------------------------------#
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

# c_ft Cost ($) of traveling from location f in L to location t in L
Cost = [ [ parse_cell(col) for col in row[1:] ] for row in tabulate(TRAVEL_COST_TABLE)[1:] ]

#############
# VARIABLES #
#############

# t_ft Decision to travel from location f in L to location t in L
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

def print_path():
    for f in L:
        print(
            ' '.join("{}->{}".format(Location[f], Location[t]) 
            if int(T[f, t].x) else '     ' for t in L)
        )

n.optimize()
print_cost("Communication 8", n)
print_path()
assert(n.objVal == 725)
