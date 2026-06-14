"""Interactive REPL: parses lines, dispatches to Game, prints reports."""
import shlex

from .game import Game
from .reports import run_sim, run_verify


HELP = """
commands (all start with '/'):
  /setup r=1 b=1 g=2 y=3 p=2 w=16 k=16   seed starting spaces (run once)
       (racers usually start near space 1; backward camels w/k start at the
        far end ~space 16 and move toward start)
  /setup random                          debug: random rule-ish initial placement
  /roll <color> <1-3> [mine]   a die popped: move camel, mark rolled.
       'mine' = YOU pulled the die (+1 pyramid coin to your bank).
       'mine' tile landings always credit you regardless of who rolled.
       racers: r b g y p   |   backward (grey die): w (white) k (black)
       a w/k roll consumes the single shared grey die for the leg
  /tile <space> oasis|mirage [mine]   place a desert tile
  /take <color> [mine]         pop the top leg-bet ticket for <color>
                               (5 -> 3 -> 2 -> 2 -> none; 'mine' = you keep it)
  /endleg                      end the leg manually (also fires automatically
                               once all 5 racers + the grey die are rolled).
                               auto-pays held tickets from the current board
                               (1st = +value, mid = +1, last = -1)
  /show                        print current board/state
  /undo                        undo last action (replay from setup)
  /sim [n]                     EV of each play (default n=10000)
  /verify                      EXACT leg-bet EV by enumerating all completions
                               (instant after 1+ dice rolled; ~1M at leg start)
  /help                        this
  /quit                        exit
colors: red blue green yellow purple (r/b/g/y/p); white=w black=k (backward)
"""

# state-mutation commands routed to Game.dispatch (after the leading '/' is stripped)
_GAME_CMDS = {"/roll", "/tile", "/take", "/endleg"}


def main():
    g = Game()
    print("Camel Up solver REPL. type '/help'. start with a /setup line.")
    while True:
        try:
            line = input("camelup> ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if not line:
            continue
        low = line.lower()
        if not low.startswith("/"):
            print(f"error: commands start with '/'. try '/help'.")
            continue
        head = low.split(maxsplit=1)[0]
        try:
            if head in ("/quit", "/exit", "/q"):
                break
            elif head == "/help":
                print(HELP)
            elif head == "/setup":
                g.do_setup(shlex.split(line)[1:])
                print("setup complete.")
                g.show()
            elif head == "/show":
                g.show()
            elif head == "/undo":
                g.undo(); g.show()
            elif head == "/sim":
                parts = shlex.split(line)
                n = int(parts[1]) if len(parts) > 1 else 10_000
                run_sim(g, n)
            elif head == "/verify":
                run_verify(g)
            elif head in _GAME_CMDS:
                g.dispatch(line[1:])   # strip leading '/'
                g.show()
            else:
                print(f"unknown command: {head}. try '/help'.")
        except Exception as e:
            print(f"error: {e}")
