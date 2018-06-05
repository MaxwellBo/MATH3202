__author__ = "Maxwell Bo"

from gurobipy import *

m = Model("Space Station")


Compartments = ["A", "B", "C", "D"]
C = range(len(Compartments))

Weights = [
    70,
    90,
    100,
    110,
    120,
    130,
    150,
    180,
    210,
    220,
    250,
    280,
    340,
    350,
    400
]
W = range(len(Weights))
assert(len(Weights) == 15)

# m Minimum number of weights held in each comparment c in C
MinimumNumber = 3

# h Maximum amount of weight held in each compartment c in C
MaximumWeight = 1000

X = { (c, w): m.addVar(vtype=GRB.BINARY) for c in C for w in W }

DoNotExceedMaximumWeightPerCompartment = {
    c: m.addConstr(
        quicksum(X[c, w] * Weights[w] for w in W) <= MaximumWeight
    )
    for c in C
}

ExceedMinimumNumberOfWeightsPerCompartment = {
    c: m.addConstr(
        quicksum(X[c, w] for w in W) >= MinimumNumber
    )
    for c in C
}

UseWeightOnlyOnce = {
    w: m.addConstr(
        quicksum(X[c, w] for c in C) == 1
    )
    for w in W
}

AAndDEqual = m.addConstr(
    quicksum(X[Compartments.index('A'), w] * Weights[w] for w in W)
    ==
    quicksum(X[Compartments.index('D'), w] * Weights[w] for w in W)
)


BAndCEqual = m.addConstr(
    quicksum(X[Compartments.index('B'), w] * Weights[w] for w in W)
    ==
    quicksum(X[Compartments.index('C'), w] * Weights[w] for w in W)
)

m.optimize()

for c in C:
    print("Compartment", Compartments[c])

    for w in W:
        if X[c, w].x == 1:
            print(Weights[w])

    print("")

