__author__  = "Maxwell Bo"

from collections import namedtuple

#########
# UTILS #
#########

def inclusive_range(start, stop): return range(start, stop + 1)

########
# DATA #
########

# Each season is a new stage in our stochastic model
Seasons = "Summer Autumn Winter Spring Summer".split()
T = range(len(Seasons))
FIRST_SEASON = T[0]
LAST_SEASON = T[-1]

# o_t Required operators in season t in T
OperatorsRequired = [ 155, 120, 140, 100, 155 ]

# u Cost of employment above the level required ($)
COST_PER_USELESS_EMPLOYEE = 2000

def cost_of_changing_level_of_employement(difference):
    return 200 * (difference ** 2)

#########
# MODEL #
#########

State = namedtuple('State', ['season', 'operators'])
Action = namedtuple('Action', ['delta'])

INITIAL_STATE  = State(season=FIRST_SEASON, operators=0)

def S(s: State, a: Action) -> State:
    season_1 = s.season + 1
    operators_1 = s.operators + a.delta

    return State(season=season_1, operators=operators_1)

def C(s: State, a: Action) -> int:
    useless_employees = S(s, a).operators - OperatorsRequired[s.season]

    # we must have the required number of employees
    assert(useless_employees >= 0)

    return (useless_employees * COST_PER_USELESS_EMPLOYEE)\
        + cost_of_changing_level_of_employement(a.delta)

cache = {}

def V(s: State):
    if s in cache:
        return cache[s]

    if s.season == LAST_SEASON + 1: # frontier overflow
        return (0, None)
    else:
        # we can either take the minimum number of operators required, 
        # or we could get all we'd ever need
        actions = [ Action(delta=d) for d in
            inclusive_range(
                OperatorsRequired[s.season] - s.operators, 
                max(OperatorsRequired) - s.operators
            )    
        ]

        cache[s] = min(
            (
                C(s, a) + V(S(s, a))[0]
                ,
                a
            )
            for a in actions
        )

    return cache[s]


###########
# RESULTS #
###########

def optimal_value():
    (value, _) = V(INITIAL_STATE)

    print("Optimal cost", value)

def probe_optimal_path():
    def probe(s: State):
        if s.season != LAST_SEASON + 1: # frontier overflow
            (_, a) = V(s)

            print("In", Seasons[s.season], "hire", a.delta)

            s_1 = S(s, a)
            probe(s_1)

    probe(INITIAL_STATE)

optimal_value()
probe_optimal_path()