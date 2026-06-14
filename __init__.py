"""Camel Up - terminal decision-support REPL.

Run as a CLI:
    python -m camel_up

Programmatic use:
    from camel_up import Game, run_sim, run_verify
    g = Game()
    g.do_setup(['random'])
    run_sim(g, 10_000)
"""
from .constants import (
    COLORS, BACKWARD, ABBR, ALL_CAMELS, FINISH, START, LETTER,
    norm_color, is_backward,
)
from .state import State, TileSpec, HeldTicket
from .engine import move_camel, ranking, pending_dice, racer_max, roll_leg
from .sim import simulate_leg, simulate_race, enumerate_leg, LegStats, RaceStats
from .game import Game
from .board_view import render_board
from .reports import run_sim, run_verify
from .repl import main

__all__ = [
    "COLORS", "BACKWARD", "ABBR", "ALL_CAMELS", "FINISH", "START", "LETTER",
    "norm_color", "is_backward",
    "State", "TileSpec", "HeldTicket",
    "move_camel", "ranking", "pending_dice", "racer_max", "roll_leg",
    "simulate_leg", "simulate_race", "enumerate_leg", "LegStats", "RaceStats",
    "Game", "render_board",
    "run_sim", "run_verify",
    "main",
]
