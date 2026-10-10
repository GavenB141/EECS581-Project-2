"""Settings and gameplay regression checks. Created 2026-10-10.

Inputs: menu events and game configurations. Output: unittest assertions.
"""
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import unittest
import pygame as pg
from settings import GameSettings, BOARD_SIZES
from defs import Board
from backend import first_click, left_click_tile, right_click_tile, get_surrounding_tiles
import settings_menu


class SettingsTests(unittest.TestCase):
    def test_invalid_choices(self):
        for kwargs in ({"board_size": 9}, {"mines": 0}, {"mines": 100},
                       {"board_size": 8, "mines": 56}, {"max_hints": -1},
                       {"max_hints": 11}, {"time_limit_seconds": -1},
                       {"time_limit_seconds": 1801}, {"mines": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                GameSettings(**kwargs)

    def test_adjustments_and_shrink(self):
        settings = GameSettings(board_size=12, mines=99)
        settings = settings.adjusted("board_size", -1).adjusted("board_size", -1)
        self.assertEqual((settings.board_size, settings.mines), (8, 55))
        self.assertEqual(settings.adjusted("board_size", -1), settings)
        self.assertEqual(settings.adjusted("mines", 1), settings)
        self.assertEqual(GameSettings(mines=1).adjusted("mines", -1).mines, 1)
        self.assertEqual(GameSettings().adjusted("max_hints", -1).max_hints, 0)
        self.assertEqual(GameSettings(max_hints=10).adjusted("max_hints", 1).max_hints, 10)
        self.assertEqual(GameSettings().adjusted("time_limit_seconds", 1).time_limit_seconds, 60)
        self.assertEqual(GameSettings(time_limit_seconds=1800).adjusted("time_limit_seconds", 1).time_limit_seconds, 1800)

    def test_new_game_snapshot(self):
        settings = GameSettings(board_size=12, mines=35, max_hints=3, time_limit_seconds=120)
        first = settings.create_board()
        first_click(first.tiles[5][5], first)
        second = settings.create_board()
        self.assertEqual((second.rows, second.cols, second.mines), (12, 12, 35))
        self.assertEqual((second.max_hints, second.time_limit_seconds), (3, 120))
        self.assertEqual(second.num_revealed, 0)
        self.assertFalse(second.first_click)
        self.assertEqual(second.flags_remaining, 35)
        self.assertIsNot(first.tiles[0][0], second.tiles[0][0])
        settings = settings.adjusted("mines", 1)
        self.assertEqual(second.settings.mines, 35)

    def test_all_sizes_safe_start_and_win(self):
        for size in BOARD_SIZES:
            for mines in (1, 20, min(99, size * size - 9)):
                for row, col in ((0, 0), (size // 2, size // 2), (size - 1, size - 1)):
                    with self.subTest(size=size, mines=mines, start=(row, col)):
                        board = Board(mines, size)
                        clicked = board.tiles[row][col]
                        first_click(clicked, board)
                        self.assertEqual(sum(t.is_mine for r in board.tiles for t in r), mines)
                        self.assertFalse(any(t.is_mine for t in [clicked] + get_surrounding_tiles(clicked, board)))
                        self.assertTrue(board.first_click)
                        for tiles in board.tiles:
                            for tile in tiles:
                                if not tile.is_mine:
                                    self.assertEqual(tile.value, sum(t.is_mine for t in get_surrounding_tiles(tile, board)))
                                    left_click_tile(tile, board)
                        self.assertTrue(board.is_game_won)
                        self.assertFalse(board.is_game_lost)

    def test_flagged_first_click_does_not_initialize(self):
        board = Board(20)
        tile = board.tiles[0][0]
        right_click_tile(tile, board)
        first_click(tile, board)
        self.assertFalse(board.first_click)
        right_click_tile(tile, board)
        first_click(tile, board)
        self.assertTrue(board.first_click)

    def test_menu_controls(self):
        pg.init()
        surface = pg.Surface((768, 928))
        settings = GameSettings()
        rows, start = settings_menu.controls(surface)
        for field, _, minus, plus in rows:
            event = pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=plus.center)
            changed, requested = settings_menu.handle_event(event, settings, surface)
            self.assertFalse(requested)
            self.assertNotEqual(getattr(changed, field), getattr(settings, field))
            unchanged, requested = settings_menu.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, button=3, pos=plus.center), settings, surface)
            self.assertEqual(unchanged, settings)
            self.assertFalse(requested)
        result, requested = settings_menu.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=start.center), settings, surface)
        self.assertTrue(requested)
        self.assertEqual(result, settings)
        settings_menu.draw(surface, settings)

    def test_gui_geometry_and_ai(self):
        import gui
        from ai import AISolver, AIStrength
        pg.init()
        gui.configure_display()
        gui.init_sprites()
        for size in BOARD_SIZES:
            board = Board(20, size)
            gui.configure_display(size)
            self.assertEqual(gui.get_clicked_tile(((16 + (size-1)*16)*gui.SCALE, (56 + (size-1)*16)*gui.SCALE)), (size-1, size-1))
            self.assertIsNone(gui.get_clicked_tile(((16 + size*16)*gui.SCALE, 56*gui.SCALE)))
            gui.draw_background()
            gui.draw_board(board)
            gui.draw_flags_left_numbers(board)
            solver = AISolver(AIStrength.EASY)
            self.assertEqual(len(solver.get_hidden(board)), size*size)
            solver.run_easy(board)
            self.assertTrue(board.first_click)
            solver.run_medium(board)
        gui.configure_display()

    def test_game_loop_return_to_menu(self):
        from unittest.mock import patch
        import gui
        pg.init()
        gui.configure_display()
        chosen = GameSettings(board_size=12, mines=30, max_hints=2, time_limit_seconds=180)
        gui.selected_settings = chosen
        gui.game_state = "menu"
        boards = []
        create = GameSettings.create_board

        def capture(settings):
            board = create(settings)
            boards.append(board)
            return board

        step = 0

        def events():
            nonlocal step
            step += 1
            if step == 1:
                pos = settings_menu.controls(gui.screen)[1].center
            elif step == 2:
                pos = (16 * gui.SCALE, 56 * gui.SCALE)
            elif step == 3:
                tile = next(t for row in boards[0].tiles for t in row if t.is_mine)
                pos = ((16 + tile.col * 16) * gui.SCALE,
                       (56 + tile.row * 16) * gui.SCALE)
            elif step == 4:
                self.assertEqual(gui.game_state, "game_over")
                pos = gui.MENU_BUTTON_RECT.center
            else:
                self.assertEqual(gui.game_state, "menu")
                return [pg.event.Event(pg.QUIT)]
            return [pg.event.Event(pg.MOUSEBUTTONDOWN, button=1, pos=pos)]

        with patch.object(GameSettings, "create_board", capture), patch.object(pg.event, "get", events):
            gui.main()
        self.assertEqual(gui.selected_settings, chosen)
        self.assertEqual((gui.SCREEN_WIDTH, gui.SCREEN_HEIGHT), (192, 232))


if __name__ == "__main__":
    unittest.main()
