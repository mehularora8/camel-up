"""Domain constants for Camel Up: colors, board size, name normalization."""

COLORS = ["red", "blue", "green", "yellow", "purple"]   # racing camels
BACKWARD = ["white", "black"]                            # crazy/backward camels
ABBR = {"r": "red", "b": "blue", "g": "green", "y": "yellow", "p": "purple",
        "w": "white", "k": "black"}                       # k = black (b taken)
ALL_CAMELS = COLORS + BACKWARD
FINISH = 16
START = 0                                                 # backward camels exit if they cross below

# single-letter board glyphs (used by board_view rendering)
LETTER = {"red": "R", "blue": "B", "green": "G", "yellow": "Y", "purple": "P",
          "white": "W", "black": "K"}


def is_backward(color):
    return color in BACKWARD


def norm_color(s):
    s = s.lower()
    if s in COLORS:
        return s
    if s in ABBR:
        return ABBR[s]
    raise ValueError(f"unknown color '{s}'")
