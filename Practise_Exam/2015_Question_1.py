from gurobipy import *
import random

m = Model()

# 100 candidate sites
S = range(100)
random.seed(20)

# p Penalty for drilling multiple times in group g in G
PENALTY = 10000

# Drill cost at each site
DrillCost = [random.randint(15000,60000) for s in S]

# 30 groups with between 5 and 10 elements in every group
Group = [sorted(random.sample(S, random.randint(5,10))) for i in range(30)]
G = range(len(Group))

# X_s Decision to drill at candidate site s in S
X = { s: m.addVar(vtype=GRB.BINARY) for s in S }

# P_g Decision to penalize group g in G
P = { g: m.addVar(vtype=GRB.BINARY) for g in G }

drill_costs = quicksum(
    X[s] * DrillCost[s] 
    for s in S
)

penalties = quicksum(
    P[g] * PENALTY
    for g in G
)

cost_function = drill_costs + penalties

m.setObjective(cost_function, GRB.MINIMIZE)

EnforceTwentyDrillSites = m.addConstr(
    quicksum(X[s] for s in S) == 20
)

CapDrillSitesPerGroup = {
    g: m.addConstr(
        quicksum(X[s] for s in Group[g]) <= 1 + P[g]
    )
    for g in G
}

m.optimize()

print("Cost $", m.objVal)
print("Sites", [s for s in S if X[s].x == 1])
