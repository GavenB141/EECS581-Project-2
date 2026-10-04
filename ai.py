'''
ai.py
Description: AI solver functionality for Project 2
Author(s): Gaven Behrends
Created: 10.04.2026
'''

import random
from enum import Enum
from defs import Board

# delay ranges from 1 to 4 seconds at 60 FPS
MIN_DELAY = 60
MAX_DELAY = 240

# encodes the strength levels of the AI solvers
class AIStrength(Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2


class AISolver:
    
    def __init__(self, strength: AIStrength):
        self.strength = strength
        self._delay = 0

    # run the AI on the board for one tick, returning True if its turn is finished
    def run(self, board: Board):
        # select a random amount of ticks to delay for
        # in order to make it feel a bit more natural
        if self._delay == 0:
            self._delay = random.randint(MIN_DELAY, MAX_DELAY)
            return False
        self._delay -= 1
        if self._delay != 0:
            return False

        # TODO: run the appropriate solving algorithm and return True when finished.
        # it may be desirable to have solver algorithms run over multiple ticks
        # with more delay logic so a user can follow along if, for example, the AI
        # flags multiple cells in a turn.
