"""Game-state DTOs."""
from dataclasses import dataclass, field
from .constants import COLORS


@dataclass
class TileSpec:
    """A desert tile placed on the board."""
    delta: int   # +1 oasis, -1 mirage
    mine: bool   # True if you placed it (you get the +1 coin on landings)


@dataclass
class HeldTicket:
    """A leg-bet ticket you've claimed; resolved at endleg."""
    color: str
    value: int


@dataclass
class State:
    track: dict = field(default_factory=dict)      # space -> [bottom..top]
    rolled: set = field(default_factory=set)       # die tokens spent this leg (colors + 'grey')
    tiles: dict = field(default_factory=dict)      # space -> TileSpec
    # leg_tickets[c] = remaining payout values, top-of-stack first
    # (base game: 5, 3, 2, 2 per color; the next bettor on c claims the head)
    leg_tickets: dict = field(default_factory=lambda: {c: [5, 3, 2, 2] for c in COLORS})
    held_tickets: list = field(default_factory=list)   # list[HeldTicket]
    coins: int = 3                                  # your bank (starting per house rule)

    def copy(self):
        return State(
            track={k: list(v) for k, v in self.track.items()},
            rolled=set(self.rolled),
            tiles={sp: TileSpec(t.delta, t.mine) for sp, t in self.tiles.items()},
            leg_tickets={c: list(v) for c, v in self.leg_tickets.items()},
            held_tickets=[HeldTicket(h.color, h.value) for h in self.held_tickets],
            coins=self.coins,
        )

    def leader_space(self):
        return max(self.track.keys()) if self.track else 0
