__author__  = "Maxwell Bo"

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

# u  Cost of employment above the level required ($)
COST_PER_USELESS_EMPLOYEE = 2000

def cost_of_changing_level_of_employement(difference):
    return 200 * (difference ** 2)

#########
# MODEL #
#########

State = namedtuple('State', ['season', 'operators'])
INITIAL_STATE  = State(season=FIRST_SEASON, operators=0)
Action = namedtuple('Action', ['delta'])

def S(s: State, a: Action) -> State:
    pass

def C(s: State, a: Action) -> int:
    pass


