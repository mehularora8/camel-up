"""Interactive REPL: parses lines, dispatches to Game, prints reports.

Each turn the screen is cleared and redrawn as a stable frame: the board on
top, then the last action's status log. Queries (/sim, /verify) redraw the
board and print their report beneath it."""
import shlex

from .constants import COLORS, BACKWARD
from .game import Game
from .board_view import render_board
from .reports import run_sim, run_verify
from .theme import clear_screen, glyph, paint


HELP = """
commands (all start with '/'):
  /setup r=1 b=1 g=2 y=3 p=2 w=16 k=16   seed starting spaces (run once)

  /setup random                          debug: random rule-ish initial placement

  /roll <color> <1-3> [mine]   a die popped: move camel, mark rolled.
       'mine' = YOU pulled the die (+1 pyramid coin to your bank).


  /tile <space> oasis|mirage [mine]   place a desert tile

  /take <color> [mine]         pop the top leg-bet ticket for <color>
                               ('mine' = you keep it)

  /endleg                      end the leg (also fires automatically
                               once all 5 racers + the grey die are rolled).

  /show                        redraw the current board/state

  /undo                        undo last action (replay from setup)

  /sim [n] [verify]            Monte Carlo EV of each play (default n=10000).
                               add 'verify' for EXACT leg-bet EV by enumerating
                               all completions (instant after 1+ dice rolled).
                               
  /help                        this
  /quit                        exit
colors: red blue green yellow purple (r/b/g/y/p); white=w black=k (backward)

(type /show to return to the board)
"""

# state-mutation commands routed to Game.dispatch (after the leading '/' is stripped)
_GAME_CMDS = {"/roll", "/tile", "/take", "/endleg"}


def _legend():
    """A one-line color key, doubling as a reminder of the camel glyphs."""
    racers = " ".join(glyph(c) for c in COLORS)
    backward = " ".join(glyph(c) for c in BACKWARD)
    return f"  racers: {racers}    backward: {backward}"


def _draw(g):
    """Clear and render the standard frame: board + this turn's status log."""
    clear_screen()
    print(render_board(g.state))
    for line in g.messages:
        print(line)


def main():
    g = Game()
    clear_screen()
    print(paint("Camel Up solver REPL", "yellow", bold=True))
    print(_legend())
    print("  type /help · start with a /setup line")
    while True:
        try:
            line = input("\ncamelup> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not line:
            continue
        low = line.lower()
        if not low.startswith("/"):
            print("error: commands start with '/'. try '/help'.")
            continue
        head = low.split(maxsplit=1)[0]
        try:
            if head in ("/quit", "/exit", "/q"):
                break
            elif head == "/help":
                clear_screen()
                print(HELP)
            elif head == "/setup":
                g.do_setup(shlex.split(line)[1:])
                _draw(g)
            elif head == "/show":
                _draw(g)
            elif head == "/undo":
                g.undo()
                _draw(g)
            elif head == "/sim":
                args = shlex.split(line)[1:]
                verify = any(a.lower() == "verify" for a in args)
                nums = [a for a in args if a.lower() != "verify"]
                n = int(nums[0]) if nums else 10_000
                clear_screen()
                print(render_board(g.state))
                run_verify(g) if verify else run_sim(g, n)
            elif head in _GAME_CMDS:
                g.dispatch(line[1:])   # strip leading '/'
                _draw(g)
            else:
                print(f"unknown command: {head}. try '/help'.")
        except Exception as e:
            print(f"error: {e}")
