"""Terminal theming for the REPL: per-camel ANSI colors + screen clearing.

Color/clear codes are emitted only for an interactive TTY (and when NO_COLOR is
unset), so piped or redirected output stays plain. FORCE_COLOR=1 overrides the
TTY check (handy for demos / capturing colored output)."""
import os
import sys

from .constants import LETTER

RESET = "\033[0m"

# camel color -> ANSI foreground code. Bright variants so camels pop on a dark
# terminal; 'black' maps to bright-black (grey) so it stays visible, and 'grey'
# (the shared backward die token) shares it.
_FG = {
    "red": "91",
    "blue": "94",
    "green": "92",
    "yellow": "93",
    "purple": "95",   # ANSI has no purple; bright magenta is the closest
    "white": "97",
    "black": "90",
    "grey": "90",
}


def _color_enabled():
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return sys.stdout.isatty()


COLOR = _color_enabled()


def paint(text, color, bold=False):
    """Wrap `text` in the ANSI color for camel `color`. No-op if color is
    disabled or `color` is unknown, so callers can paint unconditionally."""
    if not COLOR or color not in _FG:
        return text
    prefix = f"\033[{'1;' if bold else ''}{_FG[color]}m"
    return f"{prefix}{text}{RESET}"


def glyph(color):
    """The board glyph for `color` (e.g. 'R'), painted bold in its own color."""
    return paint(LETTER[color], color, bold=True)


def clear_screen():
    """Clear the terminal (screen + scrollback) and home the cursor."""
    if sys.stdout.isatty():
        print("\033[2J\033[3J\033[H", end="")
