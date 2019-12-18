__author__ = "Maxwell Bo (43926871)"

from collections import namedtuple
from typing import *

#########
# UTILS #
#########

def inclusive_range(start, stop): 
    return range(start, stop + 1)

########
# DATA #
########

# Each round is a new stage in our stochastic model
Time = inclusive_range(1, 10)
T = range(len(Time))

INITIAL_TIME = T[0]
FINAL_TIME = T[-1]
INITIAL_CARS = 0
ROUNDTRIP_TIME = 20
CAPACITY = 2

DEPART = True
REMAIN = False

cars_table = {
    10: 1,
    30: 2,
    40: 1
}

#########
# MODEL #
#########

#                             v stage 
State = namedtuple('State', ['time', 'cars'])
Action = bool # decision to cross the river

INITIAL_STATE = State(time=INITIAL_TIME, cars=INITIAL_CARS)

def S(s: State, a: Action) -> State:

    new_cars = cars_table.get(s.time, 0)

    if a is DEPART:
        return State(time = s.time + ROUNDTRIP_TIME, cars = s.cars - CAPACITY + new_cars)
    else:
        return State(time = s.time + 1, cars = s.cars + new_cars)

def C(s: State, a: Action) -> int:
    return 1

cache = {}

def V(s: State) -> Tuple[int, Action]:
    if s in cache:
        return cache[s]

    if s.time == 10000000: # frontier overflow
        return (0, None)

    else:
        actions = [ DEPART, REMAIN ]

        cache[s] = min(
            (
                (C(s, a) + V(S(s, a))[0])
                ,
                a
            )
            for a in actions
        )

    return cache[s]

def probe_optimal_path():
    def probe(s: State):
        if s.time != FINAL_TIME + 1: # frontier overflow
            (_, a) = V(s)
            print(a)
            s_1 = S(s, a)
            print("Optimal action is", a, "resulting in state", s_1)
            probe(s_1)

    probe(INITIAL_STATE)

probe_optimal_path()
