"""Leg-bet and race probability estimators.

Two leg engines share the LegStats return DTO:
  - simulate_leg: Monte Carlo over the remaining dice (fast, noisy)
  - enumerate_leg: exact, enumerates all permutations * outcomes (tractable to ~1M)

Race odds are MC-only (multi-leg state space is too big to enumerate)."""
from collections import defaultdict
from dataclasses import dataclass
from itertools import permutations, product

from .constants import COLORS, BACKWARD, FINISH
from .engine import move_camel, roll_leg, ranking, pending_dice, racer_max


@dataclass
class LegStats:
    """Probabilities of leg outcomes per racing color, plus tile EV."""
    p_first: dict           # color -> P(1st)
    p_second: dict          # color -> P(2nd)
    p_last: dict            # color -> P(last)
    tile_ev: float          # expected count of 'mine' tile landings this leg
    completions: int = 0    # exact-enumeration count; 0 when produced by MC


@dataclass
class RaceStats:
    p_win: dict             # color -> P(race winner)
    p_lose: dict            # color -> P(race last)


def simulate_leg(state, n) -> LegStats:
    win, second, lose, credit = (defaultdict(int), defaultdict(int),
                                 defaultdict(int), [0])
    pend = pending_dice(state.rolled)
    for _ in range(n):
        tr = {k: list(v) for k, v in state.track.items()}
        roll_leg(tr, pend, state.tiles, credit)
        order = ranking(tr)
        win[order[0]] += 1
        if len(order) > 1:
            second[order[1]] += 1
        lose[order[-1]] += 1
    return LegStats(
        p_first={c: win[c] / n for c in COLORS},
        p_second={c: second[c] / n for c in COLORS},
        p_last={c: lose[c] / n for c in COLORS},
        tile_ev=credit[0] / n,
    )


def enumerate_leg(state) -> LegStats:
    """Exact P(1st), P(2nd), P(last) per racing color over ALL leg completions
    given the current pending dice. A completion = (permutation of pending dice)
    x (outcome of each die). Per Camel Up 2nd ed, the grey die has 6 equally
    likely outcomes: (white|black, 1|2|3). Racer dice have 3 each."""
    pend = pending_dice(state.rolled)

    def die_outcomes(token):
        if token == "grey":
            return [(c, v) for c in BACKWARD for v in (1, 2, 3)]
        return [(token, v) for v in (1, 2, 3)]

    outcome_lists = [die_outcomes(t) for t in pend]
    win, second, lose = defaultdict(int), defaultdict(int), defaultdict(int)
    tile_credit = 0
    total = 0

    for order in permutations(range(len(pend))):
        for outcomes in product(*outcome_lists):
            tr = {k: list(v) for k, v in state.track.items()}
            credit = [0]
            for idx in order:
                color, val = outcomes[idx]
                # grey die where the chosen backward camel is already off the
                # board: die is still spent but no movement happens (mirrors
                # roll_leg's `continue`).
                if color in BACKWARD and color not in {c for st in tr.values() for c in st}:
                    continue
                move_camel(tr, color, val, state.tiles, credit)
            ord_ = ranking(tr)
            if ord_:
                win[ord_[0]] += 1
                if len(ord_) > 1:
                    second[ord_[1]] += 1
                lose[ord_[-1]] += 1
            tile_credit += credit[0]
            total += 1

    return LegStats(
        p_first={c: win[c] / total for c in COLORS},
        p_second={c: second[c] / total for c in COLORS},
        p_last={c: lose[c] / total for c in COLORS},
        tile_ev=tile_credit / total,
        completions=total,
    )


def simulate_race(state, n) -> RaceStats:
    win, lose = defaultdict(int), defaultdict(int)
    pend = pending_dice(state.rolled)
    full_leg = COLORS + ["grey"]
    for _ in range(n):
        tr = {k: list(v) for k, v in state.track.items()}
        # current (partial) leg uses the tiles actually on the board...
        roll_leg(tr, pend, state.tiles, None)
        # ...but future legs have no tiles (opponents haven't placed them yet,
        # and tiles are returned at each leg end).
        while racer_max(tr) < FINISH:
            roll_leg(tr, full_leg, {}, None)
        order = ranking(tr)
        win[order[0]] += 1
        lose[order[-1]] += 1
    return RaceStats(
        p_win={c: win[c] / n for c in COLORS},
        p_lose={c: lose[c] / n for c in COLORS},
    )
