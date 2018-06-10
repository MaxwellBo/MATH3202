from gurobipy import *
import random

# 100 candidate sites
S = range(100)
random.seed(20)

# Drill cost at each site
DrillCost = [random.randint(15000,60000) for s in S]

# 30 groups with between 5 and 10 elements in every group
Group = [sorted(random.sample(S, random.randint(5,10))) for i in range(30)]
G = range(len(Group))

m = Model("Drilling")

# X is 1 if we drill at site s
X = {s : m.addVar(vtype=GRB.BINARY) for s in S}

# Y is 1 if we drill at a site in group g
Y = {g : m.addVar(vtype=GRB.BINARY) for g in G}

m.setObjective(quicksum(DrillCost[s]*X[s] for s in S) + 
                        10000*quicksum(Y[g] for g in G))

m.addConstr(quicksum(X[s] for s in S) == 20)
for g in G:
    m.addConstr(quicksum(X[s] for s in Group[g]) <= 1 + Y[g])
    
m.optimize()

for s in S:
    if X[s].x > .99:
        print(s)