__author__ = "Maxwell Bo (43926871)"

from gurobipy import *

m = Model("Question 1 - Integer Programming")

Ports = ['Manly','Cleveland','Dunwich']
P = range(len(Ports))
B = range(18)

# t_bp Time (min) for boat b in B to travel to port p in P
Travel = [
    [29, 27, 21], [39, 18, 30], [40, 20, 31], [33, 19, 27], [35, 29, 36], [21, 23, 20],
    [30, 41, 32], [37, 27, 36], [20, 25, 34], [36, 28, 20], [24, 23, 25], [38, 22, 40], 
    [39, 19, 27], [30, 18, 28], [40, 20, 32], [21, 32, 40], [23, 18, 20], [31, 18, 20]
]

# c_p Maximum capacity of boats b in B for port p in P
Capacity = [8, 8, 6]

# X_bp Decision for boat b in B to seek shelter in port p in P
# where 1 is the decision to seek shelter, 0 otherwise
X = { (b, p): m.addVar(vtype=GRB.BINARY) for b in B for p in P }

cost_function = quicksum(
    X[b, p] * Travel[b][p]
    for b in B for p in P
)

m.setObjective(cost_function, GRB.MINIMIZE)

AllBoatsMustGetToPort = {
    b: m.addConstr(
        quicksum(X[b, p] for p in P) == 1
    )
    for b in B
}

DontExceedPortCapacity = {
    p: m.addConstr(
        quicksum(X[b, p] for b in B) <= Capacity[p]
    )
    for p in P
}

m.optimize()

print("Minimum total travel time is", m.objVal, "minutes")

def print_decisions():
    for b in B:
        for p in P:
            x = X[b, p].x

            if x:
                print("Boat", b, "seeks shelter in port", Ports[p])

print_decisions()

##########
# PART B #
##########

# m Maximum travel time of all boats b in B
M = m.addVar(vtype=GRB.INTEGER)

cost_function = M

m.setObjective(cost_function, GRB.MINIMIZE)

BindMax = {
    (b, p): m.addConstr(
        (X[b, p] * Travel[b][p]) <= M
    )
    for b in B for p in P
}

m.optimize()

print("Minimum maximum travel time is", m.objVal, "minutes")

print_decisions()