"""Validate menu choices and create independent game configurations.

Inputs: setting names and adjustment directions. Outputs: immutable settings
and a fresh Board. Created 2026-10-10 for Anthony Tran's settings task.
"""
from dataclasses import dataclass, replace

BOARD_SIZES = (8, 10, 12)
MAX_HINTS = 10
MAX_TIME_SECONDS = 1800


@dataclass(frozen=True)
class GameSettings:
    """One validated configuration; zero time means no time limit."""

    board_size: int = 10
    mines: int = 20
    max_hints: int = 0
    time_limit_seconds: int = 0

    @property
    def mine_limit(self):
        # Reserve the largest possible first-click safe area (3 by 3).
        # The existing flag counter has room for two digits.
        return min(99, self.board_size ** 2 - 9)

    def __post_init__(self):
        values = (self.board_size, self.mines, self.max_hints,
                  self.time_limit_seconds)
        if any(type(value) is not int for value in values):
            raise ValueError("Settings must be integers")
        if self.board_size not in BOARD_SIZES:
            raise ValueError("Board size must be 8, 10, or 12")
        if not 1 <= self.mines <= self.mine_limit:
            raise ValueError(f"Mine count must be between 1 and {self.mine_limit}")
        if not 0 <= self.max_hints <= MAX_HINTS:
            raise ValueError("Maximum hints must be between 0 and 10")
        if not 0 <= self.time_limit_seconds <= MAX_TIME_SECONDS:
            raise ValueError("Time limit must be between 0 and 1800 seconds")

    def adjusted(self, field, direction):
        """Return an adjusted copy, stopping at bounds without wrapping."""
        if direction not in (-1, 1):
            raise ValueError("Direction must be -1 or 1")
        if field == "board_size":
            index = max(0, min(len(BOARD_SIZES) - 1,
                               BOARD_SIZES.index(self.board_size) + direction))
            size = BOARD_SIZES[index]
            return replace(self, board_size=size,
                           mines=min(self.mines, min(99, size * size - 9)))
        limits = {"mines": (1, self.mine_limit, 1),
                  "max_hints": (0, MAX_HINTS, 1),
                  "time_limit_seconds": (0, MAX_TIME_SECONDS, 60)}
        if field not in limits:
            raise ValueError(f"Unknown setting: {field}")
        low, high, step = limits[field]
        value = max(low, min(high, getattr(self, field) + direction * step))
        return replace(self, **{field: value})

    def create_board(self):
        """Create a clean board carrying a snapshot for timer/hint consumers."""
        from defs import Board
        return Board(self.mines, self.board_size, settings=self)
