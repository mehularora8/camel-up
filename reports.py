"""User-facing reports: /sim (Monte Carlo) and /verify (exact enumeration)."""
import math

from .constants import COLORS
from .engine import pending_dice
from .sim import simulate_leg, simulate_race, enumerate_leg


def _leg_ev(stats, color, ticket_value):
    """EV for taking a +ticket_value ticket on `color` given a LegStats.
    Payout: 1st=+v, 2nd=+1, 3rd-5th=-1."""
    p1 = stats.p_first[color]
    p2 = stats.p_second[color]
    return p1 * ticket_value + p2 * 1 + (1 - p1 - p2) * (-1)


def run_sim(game, n):
    s = game.state
    if not s.track:
        print("no state yet - run setup first."); return

    leg = simulate_leg(s, n)
    print(f"\n=== /sim  ({n:,} steps) ===")
    print("LEG bets (EV of claiming the current top ticket; "
          "payout: 1st=+v, 2nd=+1, else=-1):")
    print(f"  {'color':<8}{'top':>5}{'P(1st)':>9}{'P(2nd)':>10}{'legEV':>9}")
    rows, taken = [], []
    for c in COLORS:
        stack = s.leg_tickets[c]
        if not stack:
            taken.append(c); continue
        ticket = stack[0]
        rows.append((_leg_ev(leg, c, ticket), c, leg.p_first[c], leg.p_second[c], ticket))
    for ev, c, w, s2, t in sorted(rows, reverse=True):
        print(f"  {c:<8}{t:>5}{round(w,3):>9}{round(s2,3):>10}{round(ev,2):>9}")
    for c in taken:
        print(f"  {c:<8}{'-':>5}{round(leg.p_first[c],3):>9}"
              f"{round(leg.p_second[c],3):>10}{'(taken)':>9}")
    if rows:
        best = max(rows)
        print(f"  -> best leg bet: {best[1]} +{best[4]} (EV {best[0]:+.2f})")
    else:
        print("  -> all leg tickets taken this leg.")

    race = simulate_race(s, n)
    print("\nRACE odds (dice-only, from current state):")
    print(f"  {'color':<8}{'P(win)':>9}{'P(lose)':>10}")
    for c in sorted(COLORS, key=lambda x: race.p_win[x], reverse=True):
        print(f"  {c:<8}{round(race.p_win[c],3):>9}{round(race.p_lose[c],3):>10}")

    if any(t.mine for t in s.tiles.values()):
        print(f"\nYour tile landing EV: {leg.tile_ev:.3f} coins this leg")
    if s.held_tickets:
        held_ev = sum(_leg_ev(leg, h.color, h.value) for h in s.held_tickets)
        held_str = ", ".join(f"{h.color}+{h.value}" for h in s.held_tickets)
        print(f"\nHeld tickets ({held_str}) EV: {held_ev:+.2f} coins at endleg")
    print("=================\n")


def run_verify(game):
    """Exact leg-bet EV by enumerating every completion of the current leg.
    No race odds (race always needs MC). Use after /sim to sanity-check MC noise."""
    s = game.state
    if not s.track:
        print("no state yet - run setup first."); return
    pend = pending_dice(s.rolled)
    n_racer = sum(1 for t in pend if t != "grey")
    n_grey = sum(1 for t in pend if t == "grey")
    total = math.factorial(len(pend)) * (3 ** n_racer) * (6 ** n_grey)
    print(f"\n=== /verify  (exact, enumerating {total:,} completions) ===")
    if total > 500_000:
        print("  (this may take a bit; ctrl-C to abort)")
    leg = enumerate_leg(s)
    assert leg.completions == total, (leg.completions, total)
    print("LEG bets (EXACT EV; payout: 1st=+v, 2nd=+1, else=-1):")
    print(f"  {'color':<8}{'top':>5}{'P(1st)':>10}{'P(2nd)':>10}{'legEV':>10}")
    rows = []
    for c in COLORS:
        stack = s.leg_tickets[c]
        if not stack:
            print(f"  {c:<8}{'-':>5}{round(leg.p_first[c],4):>10}"
                  f"{round(leg.p_second[c],4):>10}{'(taken)':>10}")
            continue
        t = stack[0]
        rows.append((_leg_ev(leg, c, t), c, leg.p_first[c], leg.p_second[c], t))
    for ev, c, w, s2, t in sorted(rows, reverse=True):
        print(f"  {c:<8}{t:>5}{round(w,4):>10}{round(s2,4):>10}{round(ev,3):>10}")
    if rows:
        best = max(rows)
        print(f"  -> best leg bet: {best[1]} +{best[4]} (EV {best[0]:+.3f})")
    if s.held_tickets:
        held_ev = sum(_leg_ev(leg, h.color, h.value) for h in s.held_tickets)
        held_str = ", ".join(f"{h.color}+{h.value}" for h in s.held_tickets)
        print(f"\nHeld tickets ({held_str}) EXACT EV: {held_ev:+.3f} coins at endleg")
    if any(t.mine for t in s.tiles.values()):
        print(f"\nYour tile landing EV (exact): {leg.tile_ev:.4f} coins this leg")
    print("=========================\n")
