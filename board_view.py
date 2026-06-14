"""Board rendering: visual stack-up-from-track diagram for the REPL."""
from .constants import COLORS, FINISH, LETTER


def render_board(state) -> str:
    """Return the multi-line board view as a string."""
    out = ["--- board ---"]

    occupied = list(state.track.keys()) + list(state.tiles.keys())
    lo = min([1] + occupied)
    hi = max([FINISH] + occupied)
    spaces = list(range(lo, hi + 1))

    # stack rows, top of stack at the top of the column
    max_h = max((len(state.track.get(sp, [])) for sp in spaces), default=0)
    for h in range(max_h, 0, -1):
        row = "".join(
            f" {LETTER[state.track[sp][h-1]]} " if len(state.track.get(sp, [])) >= h else "   "
            for sp in spaces
        )
        out.append("  " + row.rstrip())

    # track + space numbers
    out.append("  " + "__ " * len(spaces))
    out.append("  " + "".join(f"{sp:>2} " for sp in spaces).rstrip())

    # tile row + optional 'mine' marker row
    if state.tiles:
        tile_row, mine_row, has_mine = "", "", False
        for sp in spaces:
            if sp in state.tiles:
                t = state.tiles[sp]
                tile_row += f"{'+1' if t.delta > 0 else '-1'} "
                mine_row += " * " if t.mine else "   "
                has_mine = has_mine or t.mine
            else:
                tile_row += "   "
                mine_row += "   "
        out.append("  " + tile_row.rstrip())
        if has_mine:
            out.append("  " + mine_row.rstrip() + "    (* = your tile)")

    rolled = ", ".join(sorted(state.rolled)) or "none"
    out.append("")
    out.append(f"  rolled this leg: {rolled}")
    ticket_bits = []
    for c in COLORS:
        stack = state.leg_tickets[c]
        ticket_bits.append(f"{LETTER[c]}=[{','.join(str(v) for v in stack) or '-'}]")
    out.append(f"  leg tickets:     {'  '.join(ticket_bits)}")
    if state.held_tickets:
        held = "  ".join(f"{LETTER[h.color]}+{h.value}" for h in state.held_tickets)
        out.append(f"  you hold:        {held}")
    out.append(f"  your coins: {state.coins}")
    out.append("-------------")
    return "\n".join(out)
