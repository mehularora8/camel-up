"""Pure movement / ranking primitives. Operates on plain dicts and lists so
the same code drives the live Game, MC sims, and exact enumeration."""
import random
from .constants import COLORS, BACKWARD, is_backward


def move_camel(track, color, steps, tiles=None, credit=None):
    """Move a camel. Racing camels go forward (+) and land on TOP. Backward
    camels go backward (-) and slide UNDER the stack (bottom), carrying anyone
    above them backward too.

    `credit` is an optional [0]-style mutable counter that gets +1 for every
    landing on a `mine` tile (your tile bonus)."""
    src = next(sp for sp, st in track.items() if color in st)
    idx = track[src].index(color)
    moving = track[src][idx:]
    track[src] = track[src][:idx]
    if not track[src]:
        del track[src]

    if is_backward(color):
        dst = src - steps                          # backward = toward start
        if tiles and dst in tiles:
            tile = tiles[dst]
            if tile.mine and credit is not None:
                credit[0] += 1
            dst += tile.delta
        track.setdefault(dst, [])
        track[dst] = moving + track[dst]           # backward -> land on BOTTOM
        return

    # forward racer
    dst = src + steps
    if tiles and dst in tiles:
        tile = tiles[dst]
        if tile.mine and credit is not None:
            credit[0] += 1
        dst += tile.delta
        track.setdefault(dst, [])
        if tile.delta < 0:
            track[dst] = moving + track[dst]       # mirage -> bottom
        else:
            track[dst].extend(moving)              # oasis  -> top
    else:
        track.setdefault(dst, [])
        track[dst].extend(moving)


def roll_leg(track, pending, tiles, credit):
    """Roll the remainder of a leg in random order. `pending` is the list of
    die tokens still to pop: racer colors and/or the 'grey' token. Grey moves
    white OR black (50/50) by 1..3."""
    order = pending[:]
    random.shuffle(order)
    for token in order:
        if token == "grey":
            color = random.choice(BACKWARD)
            if color not in {c for st in track.values() for c in st}:
                continue                            # chosen camel already off
            move_camel(track, color, random.randint(1, 3), tiles, credit)
        else:
            move_camel(track, token, random.randint(1, 3), tiles, credit)


def ranking(track):
    """Front-to-back order of RACING camels only (backward camels can't win/lose)."""
    out = []
    for sp in sorted(track, reverse=True):
        for c in reversed(track[sp]):
            if c in COLORS:
                out.append(c)
    return out


def pending_dice(rolled):
    """Dice still to pop this leg given the set of spent die tokens."""
    pend = [c for c in COLORS if c not in rolled]
    if "grey" not in rolled:
        pend.append("grey")
    return pend


def racer_max(track):
    """Furthest space occupied by a RACING camel (ignores backward camels)."""
    best = None
    for sp, st in track.items():
        if any(c in COLORS for c in st):
            best = sp if best is None else max(best, sp)
    return best if best is not None else 0
