"""
test_minesweeper.py
Description - unit tests for the minesweeper backend and AI solver
Tests ... 
    1. first click cant contain a mine
    2. flagged cells cant be uncovered
    3. victory is correctly found 
    4. loss is correctly found 
    5. easy ai does not select revealed or flagged cells
    6. medium ai identifies a logically certain mine
    7. hard AI recognizes the 1-2-1 pattern
Author: Sakthivel Sivasubramanian
Created: 10/10/2026
Assitance - test strucutres and cases were written with help from chatgpt 6 ... 
"""

import unittest
from unittest.mock import patch

from defs import Board
from backend import (
    first_click ,
    left_click_tile ,
    right_click_tile ,
    check_win ,
    get_surrounding_tiles ,
)
from ai import AISolver , AIStrength


class TestMinesweeperBackend(unittest.TestCase):

    # ---------------------------------------------------------
    # TEST 1
    # the first clicked cell and its surroundings should not have miens . 
    # ---------------------------------------------------------
    def test_first_click_never_hits_mine(self):
        board = Board(20)
        # this has all the surroundings 
        clicked_tile = board.tiles[5][5]
        first_click(clicked_tile , board)
        self.assertFalse(
            clicked_tile.is_mine ,
            "the first clicked tile contained a mine."
        )
        # the first click should also be revealed.
        self.assertTrue(
            clicked_tile.is_revealed,
            "the first clicked tile was not revealed."
        )

        # every adjacent tile should also be safe.
        surrounding = get_surrounding_tiles(clicked_tile , board)

        for tile in surrounding:
            self.assertFalse(
                tile.is_mine,
                f"Adjacent Tile ({tile.row},{tile.col}) contained a mine"
            )
        mine_count = sum(
            tile.is_mine
            for row in board.tiles
            for tile in row
        )

        self.assertEqual(
            mine_count,
            20,
            "board did not contain the requested number of mines."
        )

    # ---------------------------------------------------------
    # TEST 2
    # the flagged tile should ignore left clicks
    # ---------------------------------------------------------
    def test_flagged_cell_cannot_be_uncovered(self):
        board = Board(10)
        tile = board.tiles[4][4]
        # flag the tile.
        right_click_tile(tile , board)
        self.assertTrue(tile.is_flagged)
        revealed_before = board.num_revealed
        # attempt to show the flagged tile
        left_click_tile(tile , board)

        self.assertFalse(
            tile.is_revealed,
            "the flagged tile was incorrectly revealed."
        )

        self.assertEqual(
            board.num_revealed,
            revealed_before,
            "revealed-cell count changed after clicking a flag."
        )

    # ---------------------------------------------------------
    # TEST 3
    # the game should be won once every non-mine tile has
    # been revealed
    # ---------------------------------------------------------
    def test_game_correctly_detects_victory(self):
        board = Board(1)
        board.tiles[0][0].is_mine = True

        # there are 99 safe cells on a board with one mine ... 
        # simulate 98 already being revealed
        safe_tiles = [
            tile
            for row in board.tiles
            for tile in row
            if not tile.is_mine
        ]
        for tile in safe_tiles[:-1]:
            tile.is_revealed = True
        board.num_revealed = 98

        # show the final safe tile.
        final_safe_tile = safe_tiles[-1]

        # use the nonzero value so recursive zero-cell expansion does not affect this isolated victory test 
        final_safe_tile.value = 1

        left_click_tile(final_safe_tile , board)

        self.assertTrue(
            board.is_game_won,
            "game did not detect victory after all safe cells were revealed."
        )

        self.assertFalse(
            board.is_game_lost,
            "game was incorrectly marked as lost."
        )

    # ---------------------------------------------------------
    # TEST 4
    # clicking the mine should immediately lose the game
    # ---------------------------------------------------------
    def test_game_correctly_detects_loss(self):
        board = Board(1)

        mine = board.tiles[3][3]
        mine.is_mine = True

        left_click_tile(mine , board)

        self.assertTrue(
            board.is_game_lost,
            "clicking the mine did not cause a loss."
        )

        self.assertIs(
            board.clicked_mine,
            mine,
            "the clicked mine was not recorded correctly."
        )

        self.assertTrue(
            mine.is_revealed,
            "the clicked mine was not revealed."
        )

        self.assertFalse(
            board.is_game_won,
            "game was incorrectly marked as won."
        )


class TestMinesweeperAI(unittest.TestCase):

    # ---------------------------------------------------------
    # TEST 5
    # Easy AI should only choose from hidden , unflagged cells . 
    # ---------------------------------------------------------
    def test_easy_ai_never_selects_revealed_or_flagged_cells(self):
        board = Board(10)
        solver = AISolver(AIStrength.EASY)

        # pretend the game has already started so select_random() does not trigger first_click() . 
        board.num_revealed = 1

        revealed_tile = board.tiles[0][0]
        revealed_tile.is_revealed = True

        flagged_tile = board.tiles[0][1]
        flagged_tile.is_flagged = True

        valid_tile = board.tiles[0][2]

        hidden = solver.get_hidden(board)

        self.assertNotIn(
            revealed_tile,
            hidden,
            "Easy AI considered a revealed tile selectable."
        )

        self.assertNotIn(
            flagged_tile,
            hidden,
            "Easy AI considered a flagged tile selectable."
        )

        self.assertIn(
            valid_tile,
            hidden,
            "Easy AI failed to include a valid hidden tile."
        )

        # force random.choice to choose a known valid cell.
        with patch("ai.random.choice" , return_value=valid_tile):
            solver.run_easy(board)

        self.assertTrue(
            valid_tile.is_revealed,
            "Easy AI failed to reveal its selected valid tile."
        )

        self.assertTrue(
            revealed_tile.is_revealed,
            "existing revealed tile was unexpectedly modified."
        )

        self.assertTrue(
            flagged_tile.is_flagged,
            "Easy AI incorrectly modified a flagged tile."
        )

    # ---------------------------------------------------------
    # TEST 6
    # Medium A
    # if hidden + flagged neighbors == displayed number ... 
    # then every remaining hidden neighbor must be a mine 
    # ---------------------------------------------------------
    def test_medium_ai_correctly_identifies_mine(self):
        board = Board(10)
        solver = AISolver(AIStrength.MEDIUM)

        # center revealed tile displaying "1"
        center = board.tiles[5][5]
        center.is_revealed = True
        center.value = 1

        board.num_revealed = 1

        neighbors = get_surrounding_tiles(center, board)

        # show every neighbor except one 
        suspected_mine = board.tiles[5][6]

        for tile in neighbors:
            if tile is not suspected_mine:
                tile.is_revealed = True

        # onle one hidden neighbor remains around a "1"
        solver.run_medium(board)

        self.assertTrue(
            suspected_mine.is_flagged,
            "Medium AI failed to flag the logically certain mine."
        )

    # ---------------------------------------------------------
    # TEST 7
    # Hard AI should recognize:
    #
    #       1 2 1
    #       ? ? ?
    # and guess ... SAFE FLAG
    # ---------------------------------------------------------
    def test_hard_ai_handles_121_pattern(self):
        board = Board(10)
        solver = AISolver(AIStrength.HARD)

        # create the revealed 1-2-1 sequence.
        left = board.tiles[1][1]
        middle = board.tiles[1][2]
        right = board.tiles[1][3]

        left.is_revealed = True
        middle.is_revealed = True
        right.is_revealed = True

        left.value = 1
        middle.value = 2
        right.value = 1

        board.num_revealed = 3

        # these are the three hidden cells immediately below the 1-2-1 sequence 
        outer_left = board.tiles[2][1]
        safe_middle = board.tiles[2][2]
        outer_right = board.tiles[2][3]

        cells_to_reveal = [
            board.tiles[0][0],
            board.tiles[0][1],
            board.tiles[0][2],
            board.tiles[0][3],
            board.tiles[0][4],
            board.tiles[1][0],
            board.tiles[1][4],
            board.tiles[2][0],
            board.tiles[2][4],
        ]

        for tile in cells_to_reveal:
            tile.is_revealed = True

        solver.run_hard(board)

        self.assertTrue(
            outer_left.is_flagged,
            "Hard AI failed to flag the left mine in the 1-2-1 pattern."
        )

        self.assertTrue(
            outer_right.is_flagged,
            "Hard AI failed to flag the right mine in the 1-2-1 pattern."
        )

        self.assertTrue(
            safe_middle.is_revealed,
            "Hard AI failed to reveal the safe middle tile in the 1-2-1 pattern."
        )

        self.assertFalse(
            safe_middle.is_flagged,
            "Hard AI incorrectly flagged the safe middle tile."
        )


if __name__ == "__main__":
    unittest.main()