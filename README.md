# camel-up-solver

A terminal decision-support REPL for [Camel Up](https://boardgamegeek.com/boardgame/153938/camel-up).
Feed it the table state (rolls, tiles, ticket grabs) as the game plays out, then
ask `/sim` for the EV of each available bet (or `/sim verify` for an exact answer).

```
camelup> /setup random
camelup> /take g mine
camelup> /tile 5 oasis mine
camelup> /roll y 3
camelup> /sim
```

## Install

You need Python 3.9+. The recommended way is [`pipx`](https://pipx.pypa.io/),
which installs `camelup` into its own isolated environment and puts it on your
PATH:

```bash
pipx install camel-up-solver
camelup
```

Or with plain `pip`:

```bash
pip install camel-up-solver
camelup
```

Update later with `pipx upgrade camel-up-solver` (or `pip install -U
camel-up-solver`).

### From source

```bash
git clone https://github.com/mehularora8/camel-up
cd camel-up
pip install -e .   # editable: source edits take effect immediately
camelup
```

Or run it without installing:

```bash
PYTHONPATH=src python -m camel_up
```

## Commands

All commands start with `/`. Type `/help` inside the REPL for the full list.

| command | what it does |
| --- | --- |
| `/setup r=1 b=1 g=2 y=3 p=2 w=16 k=16` | seed each camel's starting space |
| `/setup random` | random rule-ish starting placement (debug) |
| `/roll <color> <1-3> [mine]` | a die popped this turn; `mine` = you pulled it (+1 pyramid coin) |
| `/tile <space> oasis\|mirage [mine]` | place a desert tile (`mine` = you placed it) |
| `/take <color> [mine]` | someone claimed the top leg-bet ticket (`mine` = you took it) |
| `/endleg` | manually end the leg; also fires automatically when the pyramid empties |
| `/show` | print the current board |
| `/undo` | undo the last action |
| `/sim [n] [verify]` | Monte Carlo EV of every leg bet + race odds (default 10,000 rollouts); add `verify` for EXACT leg-bet EV via full completion enumeration |
| `/help` | command reference |
| `/quit` | exit |

Colors: `r b g y p` for the racing camels (red/blue/green/yellow/purple);
`w` (white) and `k` (black) for the crazy/backward camels.

## How it works

- The leg is small enough to solve exactly (`/sim verify` enumerates every
  remaining permutation × outcome — tractable up to ~1M completions, instant
  once a die or two has been rolled).
- The full race spans many legs and is Monte Carlo only.
- Held tickets pay out automatically at `/endleg` from the final board:
  1st = +face value, 2nd = +1, 3rd-5th = -1.

## Programmatic use

```python
from camel_up import Game, run_sim, run_verify

g = Game()
g.do_setup(['random'])
g.dispatch('take g mine')
g.dispatch('roll y 3')
run_sim(g, 10_000)
run_verify(g)
```
