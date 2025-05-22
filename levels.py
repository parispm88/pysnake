"""
Defines the level structures for the Pysnake Break game.

Each level is represented as a list of strings, where:
- 'S': Standard Brick (e.g., Blue)
- 'H': Harder Brick (e.g., Red - currently same as Standard for simplicity)
- 'P': Power-up Brick (guaranteed to drop a power-up)
- ' ': Empty space
"""

LEVEL_1 = [
    "       ",
    " SSSSS ",
    " SSSSS ",
    " SSSSS ",
    "       ",
    "   P   ",
    "       "
]

LEVEL_2 = [
    "HHHHHHH",
    "H     H",
    "H SSS H",
    "H SPH H",
    "H SSS H",
    "H     H",
    "HHHHHHH"
]

LEVEL_3 = [
    "P S H S P",
    " S H S H ",
    "H S H S H",
    " S H S H ",
    "P S H S P",
    "         ",
    "  SSSSS  "
]

LEVEL_4 = [
    " S S S S ",
    "S H P H S",
    " S H H S ",
    "S H P H S",
    " S S S S ",
    "    P    ",
    "  HHHHH  "
]

LEVEL_5 = [
    "P H S H P",
    " H     H ",
    "S   S   S",
    " H     H ",
    "P H S H P",
    "   SSS   ",
    "  S H S  "
]

ALL_LEVELS = [LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4, LEVEL_5]

# Define brick properties based on character codes
# This could be expanded (e.g., health, different points)
# For now, color and power-up potential.
# Colors are (R,G,B)
BRICK_CONFIG = {
    'S': {'color': (0, 0, 255), 'power_up_chance': 0.1},  # Blue, low chance
    'H': {'color': (255, 0, 0), 'power_up_chance': 0.15}, # Red, slightly higher chance
    'P': {'color': (0, 255, 0), 'power_up_chance': 1.0}   # Green, guaranteed power-up
}
