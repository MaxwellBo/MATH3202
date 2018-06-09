from gurobipy import *
import random

# Data and ranges
nHospitalSites = 30
nSuburbs = 55
MaxSuburbsPerHospital = 7
MaxPopulation = 500000

H = range(nHospitalSites)
S = range(nSuburbs)

random.seed(3)

FixedCost = [random.randint(5000000,10000000) for h in H]
Population = [random.randint(60000,90000) for s in S]

# Travel distance - multiply by population moved to get travel cost
Dist = [[random.randint(0,50) for s in S] for h in H]

# Set up model and set the gap on the answer to 0
m = Model()
m.setParam('MIPGap', 0)

# B_h Decision to build hospital h in H
B = { h: m.addVar(vtype=GRB.BINARY) for h in H }

# S_hs Decision for hospital h in H to service suburb s in S
E = { (s, h): m.addVar(vtype=GRB.BINARY) for s in S for h in H }

build_cost = quicksum(
    B[h]
    *
    FixedCost[h]
    for h in H
)

travel_cost = quicksum(
    E[s, h]
    *
    Dist[h][s] * Population[s]
    for s in S for h in H
)

cost_function = build_cost + travel_cost

m.setObjective(cost_function, GRB.MINIMIZE)


NoMoreThanSevenSuburbs = {
    h: m.addConstr(
        quicksum(E[s, h] for s in S) <= MaxSuburbsPerHospital* B[h]
    )
    for h in H
}

NoMoreThanSevenSuburbs = {
    s: m.addConstr(
        quicksum(E[s, h] for h in H) == 1
    )
    for s in S
}

NoMoreThanMaxPopulation = {
    h: m.addConstr(
        quicksum(E[s, h] * Population[s] for s in S) <= MaxPopulation
    )
    for h in H
}

m.optimize()

print("Minimum cost $", m.objVal)
print("Hospitals", [ h for h in H if B[h].x == 1])
