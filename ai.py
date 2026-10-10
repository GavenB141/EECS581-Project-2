'''
ai.py
Description: AI solver functionality for Project 2
Author(s): Gaven Behrends
Created: 10.04.2026
'''

import random
from enum import Enum
from defs import Board, Tile
from backend import first_click, left_click_tile, right_click_tile, get_surrounding_tiles

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
        # takes the next turn with the chosen strength level
        if self.strength == AIStrength.EASY:
            self.run_easy(board)
        elif self.strength == AIStrength.MEDIUM:
            self.run_medium(board)
        elif self.strength == AIStrength.HARD:
            self.run_hard(board)
        return True

    # returns every tile that is still hidden and not flagged so the AI knows what it can actually select
    def get_hidden(self, board: Board) -> list[Tile]:
        hidden = []
        for row in range(board.rows):
            for col in range(board.cols):
                tile = board.tiles[row][col]
                if not tile.is_revealed and not tile.is_flagged:
                    hidden.append(tile)
        return hidden

    # allows the AI to select a random tile that is hidden
    # essential for every AI level, therefore I'm implementing as a seperate function
    def select_random(self, board: Board):
        if board.is_game_lost or board.is_game_won: 
            return
        available = self.get_hidden(board) # list of what can be used
        if not available:
            return
        tile = random.choice(available)
        # mines aren't placed until after the first click, so it makes sure to run that function so the board isn't blank
        if board.num_revealed == 0:
            first_click(tile, board)
        else:
            left_click_tile(tile, board)

    # Easy: uncovers a random cell, not including any flagged or already uncovered cells.
    def run_easy(self, board: Board):
        self.select_random(board)

    # Medium: The computer applies two basic rules. First, if the number of hidden neighbors of a revealed cell equals that cell’s number, 
    # the AI should flag all hidden neighbors. Second, if the number of flagged neighbors of a revealed cell equals that cell’s number, 
    # the AI should open all other hidden neighbors. If no rule applies, the AI should pick a random hidden cell.
    def run_medium(self, board: Board):
        if board.is_game_lost or board.is_game_won:
            return

        if board.num_revealed == 0:
            self.select_random(board)

        for row in range(board.rows):
            for col in range(board.cols):
                tile = board.tiles[row][col]
                if not tile.is_revealed or tile.value < 1 or tile.value > 8:
                    continue
                neighbors = get_surrounding_tiles(tile, board)
                flagged = [neighbor for neighbor in neighbors if neighbor.is_flagged]
                hidden = [neighbor for neighbor in neighbors if not neighbor.is_revealed and not neighbor.is_flagged]

                if hidden and len(flagged) + len(hidden) == tile.value:
                    for neighbor in hidden:
                        right_click_tile(neighbor, board)
                        if board.is_game_lost or board.is_game_won:
                            return
                    return

                if hidden and len(flagged) == tile.value:
                    for neighbor in hidden:
                        left_click_tile(neighbor,board)
                        if board.is_game_lost or board.is_game_won:
                            return     
                    return
        self.select_random(board)
                    


    # HARD: The computer applies all the rules from the Medium level, plus the 1-2-1 pattern rule. If three side-by-side revealed cells show “1-2-1,” 
    # the AI can logically deduce that the two outer hidden neighbors are mines (and should be flagged), while the inner hidden neighbor is safe (and should be opened). 
    # If no rule applies, the AI should fall back to a random click.
    def run_hard(self, board: Board):
        return # TODO

        # TODO: run the appropriate solving algorithm and return True when finished.
        # it may be desirable to have solver algorithms run over multiple ticks
        # with more delay logic so a user can follow along if, for example, the AI
        # flags multiple cells in a turn.
