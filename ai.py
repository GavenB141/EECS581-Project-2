'''
ai.py
Description: AI solver functionality for Project 2
Author(s): Gaven Behrends, Cooper Fish
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
        for row in range(10): # need to come back and change range for row and col to be adjustable to changing board size once implemented
            for col in range(10):
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

        for row in range(10):
            for col in range(10):
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
        # stop if the game is already over
        if board.is_game_lost or board.is_game_won: 
            return

        # click randomly first
        if board.num_revealed == 0:
            self.select_random(board)
            return

        rows, cols = len(board.tiles), len(board.tiles[0])

        # Medium rules
        for row in range(rows):
            for col in range(cols):
                tile = board.tiles[row][col]
                if not tile.is_revealed or tile.value < 1 or tile.value > 8:
                    continue
                neighbors = get_surrounding_tiles(tile, board)
                flagged = [n for n in neighbors if n.is_flagged]
                hidden = [n for n in neighbors if not n.is_revealed and not n.is_flagged]

                if hidden and len(flagged) + len(hidden) == tile.value:
                    for n in hidden:
                        right_click_tile(n, board)
                    return

                if hidden and len(flagged) == tile.value:
                    for n in hidden:
                        left_click_tile(n, board)
                        if board.is_game_lost or board.is_game_won:
                            return
                    return

        # look for three revealed tiles in a row showing 1, 2, 1
        for r in range(rows):
            for c in range(cols):
                # (0, 1) checks horizontal lines, (1, 0) checks vertical lines
                for dr, dc in ((0, 1), (1, 0)):
                    pr, pc = dc, dr
                    # skip if the line would go off the board
                    if r + 2 * dr >= rows or c + 2 * dc >= cols:
                        continue
                    line = [(r + dr * i, c + dc * i) for i in range(3)]
                    line_tiles = [board.tiles[x][y] for x, y in line]
                    if not all(t.is_revealed for t in line_tiles):
                        continue
                    if [t.value for t in line_tiles] != [1, 2, 1]:
                        continue

                    # try the hidden tiles on each side of the line
                    for side in (1, -1):
                        side_cells = [(x + pr * side, y + pc * side) for x, y in line]
                        first, last = side_cells[0], side_cells[2]
                        # skip if this side is off the board
                        if not (0 <= first[0] < rows and 0 <= first[1] < cols):
                            continue
                        if not (0 <= last[0] < rows and 0 <= last[1] < cols):
                            continue

                        # other neighbors must be revealed or the deduction isn't certain
                        clean = True
                        for x, y in line:
                            for ax in (-1, 0, 1):
                                for ay in (-1, 0, 1):
                                    nx, ny = x + ax, y + ay
                                    if (ax, ay) == (0, 0):
                                        continue
                                    if not (0 <= nx < rows and 0 <= ny < cols):
                                        continue
                                    if (nx, ny) in side_cells:
                                        continue
                                    if not board.tiles[nx][ny].is_revealed:
                                        clean = False
                        if not clean:
                            continue

                        # a and d are the outer tiles, b is the middle
                        a, b, d = (board.tiles[x][y] for x, y in side_cells)
                        if a.is_revealed or b.is_revealed or d.is_revealed or b.is_flagged:
                            continue

                        # flag the outer two, open the middle
                        for t in (a, d):
                            if not t.is_flagged:
                                right_click_tile(t, board)
                        left_click_tile(b, board)
                        return
        self.select_random(board)
