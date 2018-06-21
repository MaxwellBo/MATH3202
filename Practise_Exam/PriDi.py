__author__ = "Maxwell Bo (43926871)"

from collections import namedtuple

#########
# UTILS #
#########

def inclusive_range(start, stop): 
    return range(start, stop + 1)

#                        / high     if high < n 
# clamp(low, n, high) = |  low      if n < low
#                       \  n        otherwise
def clamp(low, n, high): 
    return max(min(high, n), low)

########
# DATA #
########

# Each round is a new stage in our stochastic model
Rounds = inclusive_range(1, 10)
T = range(len(Rounds))

FIRST_ROUND = T[0]
LAST_ROUND = T[-1]

COOPERATE = True
DEFECT = False

INITIAL_COOPERABILITY = 0.6

ON_COOPERATE = +0.1 # to cooperabiliy of opponent
ON_DEFECT = -0.2 # to cooperabiliy of opponent

# p_yo Payoff if you make decision y and opponent makes decision o
PLAYOFF_TABLE = {
    (COOPERATE, COOPERATE): 3,
    (COOPERATE, DEFECT): 0,
    (DEFECT, COOPERATE): 5,
    (DEFECT, DEFECT): 1
}

def get_payoff(you, opponent): 
    return PLAYOFF_TABLE[you, opponent]

#########
# MODEL #
#########

#                             v stage 
State = namedtuple('State', ['round', 'cooperability'])
Action = bool # decision for you to cooperate (True) or defect (False)
OpponentAction = bool # # decision for opponent to cooperate (True) or defect (False)

INITIAL_STATE = State(round=FIRST_ROUND, cooperability=INITIAL_COOPERABILITY)

def S(s: State, a: Action) -> State:
    round_1 = s.round + 1

    change_in_cooperability = ON_COOPERATE if a == COOPERATE else ON_DEFECT

    cooperability_1 = s.cooperability + change_in_cooperability

    #                                          v ensures probability stays between 0 and 1
    return State(round=round_1, cooperability=clamp(0, cooperability_1, 1))

def C(s: State, a: Action, o: OpponentAction) -> int:
    return get_payoff(a, o)

cache = {}

def V(s: State):
    if s in cache:
        return cache[s]

    if s.round == LAST_ROUND + 1: # frontier overflow
        return (0, None)

    else:
        actions = [ COOPERATE, DEFECT ]

        cache[s] = max(
            (
                (
                         s.cooperability  * (C(s, a, COOPERATE) + V(S(s, a))[0])
                    +
                    (1 - s.cooperability) * (C(s, a, DEFECT)    + V(S(s, a))[0])
                )
                ,
                a
            )
            for a in actions
        )

    return cache[s]

def optimal_value():
    (value, _) = V(INITIAL_STATE)

    print("The optimal payoff is ${}".format(round(value, 2)))

def probe_optimal_path():
    def probe(s: State):
        if s.round != LAST_ROUND + 1: # frontier overflow
            (_, a) = V(s)

            print("In round", Rounds[s.round], 
                "the opponents cooperability is", round(s.cooperability, 1),
                "so you should", "cooperate" if a == COOPERATE else "defect"
            )

            s_1 = S(s, a)
            probe(s_1)

    probe(INITIAL_STATE)

optimal_value()
probe_optimal_path()
