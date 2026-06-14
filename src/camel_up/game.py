"""Game: orchestrates state mutations through discrete actions, with a
replay-based undo. Mutates state in place; history of raw command strings
lets undo rebuild from the setup snapshot."""
import random
import shlex
from collections import defaultdict

from .constants import COLORS, FINISH, is_backward, norm_color
from .state import State, TileSpec, HeldTicket
from .engine import move_camel, ranking
from .board_view import render_board


class Game:
    def __init__(self):
        self.state = State()
        self.setup_done = False
        self.history = []          # raw command strings (post-setup)
        self._setup_state = None   # snapshot for undo replay

    # ----- setup -----
    def do_setup(self, args):
        """setup r=1 b=1 g=2 y=3 p=2 w=16 k=16    each camel's starting space
        setup random                               random rule-ish placement"""
        if len(args) == 1 and args[0].lower() == "random":
            order = COLORS[:]
            random.shuffle(order)
            placed = [(random.randint(1, 3), c) for c in order]
            placed += [(FINISH, "white"), (FINISH, "black")]
        else:
            placed = []
            for tok in args:
                k, v = tok.split("=")
                placed.append((int(v), norm_color(k)))
        track = defaultdict(list)
        for sp, color in placed:
            track[sp].append(color)
        self.state = State(track=dict(track))
        self.setup_done = True
        self._setup_state = self.state.copy()
        self.history = []

    # ----- actions (mutate state in place) -----
    def act_roll(self, color, steps, mine):
        credit = [0]
        move_camel(self.state.track, color, steps, self.state.tiles, credit)
        self.state.coins += credit[0]          # mine-tile landings always credit you
        if mine:
            self.state.coins += 1              # +1 pyramid coin only if YOU rolled
        if is_backward(color):
            self.state.rolled.add("grey")
        else:
            self.state.rolled.add(color)
        # pyramid empty -> leg ends automatically
        if self.state.rolled >= set(COLORS) | {"grey"}:
            print("(pyramid empty -> auto endleg)")
            self.act_endleg()

    def act_tile(self, space, kind, mine):
        delta = +1 if kind == "oasis" else -1
        self.state.tiles[space] = TileSpec(delta, mine)

    def act_take(self, color, mine):
        stack = self.state.leg_tickets.get(color, [])
        if not stack:
            print(f"no {color} leg-bet tickets left this leg.")
            return
        val = stack.pop(0)
        if mine:
            self.state.held_tickets.append(HeldTicket(color, val))
            print(f"you took {color} +{val} leg ticket (held until endleg).")
        else:
            print(f"opponent took {color} +{val} leg ticket.")

    def act_endleg(self):
        held = self.state.held_tickets
        if held:
            order = ranking(self.state.track)
            winner = order[0]
            second = order[1] if len(order) > 1 else None
            delta = 0
            for ht in held:
                if ht.color == winner:    delta += ht.value
                elif ht.color == second:  delta += 1
                else:                     delta -= 1
            self.state.coins += delta
            print(f"leg result: 1st={winner}, 2nd={second}. "
                  f"payout {delta:+d} -> you now have {self.state.coins} coins.")
        self.state.held_tickets = []
        self.state.rolled = set()
        self.state.tiles = {}                  # tiles returned each leg
        self.state.leg_tickets = {c: [5, 3, 2, 2] for c in COLORS}

    # ----- dispatch (live input + replay) -----
    def dispatch(self, line, record=True):
        parts = shlex.split(line)
        if not parts:
            return
        cmd, args = parts[0].lower(), parts[1:]

        if cmd == "roll":
            color = norm_color(args[0])
            steps = int(args[1])
            mine = len(args) > 2 and args[2].lower() == "mine"
            self.act_roll(color, steps, mine)
        elif cmd == "tile":
            sp = int(args[0]); kind = args[1].lower()
            mine = len(args) > 2 and args[2].lower() == "mine"
            self.act_tile(sp, kind, mine)
        elif cmd == "endleg":
            self.act_endleg()
        elif cmd == "take":
            color = norm_color(args[0])
            mine = len(args) > 1 and args[1].lower() == "mine"
            self.act_take(color, mine)
        else:
            raise ValueError(f"not a state action: {cmd}")

        if record:
            self.history.append(line)

    def undo(self):
        if not self.history:
            print("nothing to undo."); return
        dropped = self.history.pop()
        self.state = self._setup_state.copy()
        for line in self.history:
            self.dispatch(line, record=False)
        print(f"undid: {dropped}")

    def show(self):
        """Convenience: print the board view of the current state."""
        print(render_board(self.state))
