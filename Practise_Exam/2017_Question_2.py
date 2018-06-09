__author__ = "Maxwell Bo"

from collections import namedtuple

Cards = frozenset(range(10))
C = range(10)

State = namedtuple('State', ['cards', 'grid'])
Grid = namedtuple('Grid', ['TL', 'TR', 'BL', 'BR'])

INITIAL_STATE = State(cards=Cards, grid=Grid(None, None, None, None))

Action = str

cache = {}

def S(s: State, a: Action, card: int) -> State:
    cards_1 = s.cards - {card}

    go = s.grid._asdict()
    go[a] = card

    grid_1 = Grid(
        *go
    )

    return State(
        cards=cards_1,
        grid=grid_1
    )

def V(s: State) -> int:
    if s in cache:
        return cache[s]

    TL, TR, BL, BR = s.grid

    if len(s.cards) == 9 - 4:
        cache[s] = (
            (TL * 10) + TR
            *
            (BL * 10) + BR,
            None
        )
    else:
        actions = [ 'TL', 'TR', 'BL', 'BR' ]

        weight = 1 / len(s.cards)

        cache[s] = min(
            (
                sum(weight * V(S(s, a, card)) for card in s.cards)
                ,
                a
            )
            for a in actions
        )

    return cache[s]

V(INITIAL_STATE)

print(cache[INITIAL_STATE])