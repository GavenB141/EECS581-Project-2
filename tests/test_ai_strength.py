import unittest
from unittest.mock import patch

from ai import AISolver, AIStrength
from settings import AI_STRENGTHS, GameSettings


class AIStrengthTests(unittest.TestCase):
    def test_strength_adjustments_stop_at_bounds(self):
        self.assertEqual(GameSettings().strength, "hard")
        self.assertEqual(
            GameSettings(strength="easy").adjusted("strength", -1).strength,
            "easy",
        )
        self.assertEqual(
            GameSettings(strength="hard").adjusted("strength", 1).strength,
            "hard",
        )
        self.assertEqual(
            GameSettings(strength="easy").adjusted("strength", 1).strength,
            "medium",
        )
        self.assertEqual(
            GameSettings(strength="medium").adjusted("strength", 1).strength,
            "hard",
        )
        self.assertEqual(
            GameSettings(strength="medium").adjusted("strength", -1).strength,
            "easy",
        )

    def test_invalid_strength_is_rejected(self):
        for strength in ("unknown", "EASY", 1):
            with self.subTest(strength=strength), self.assertRaises(ValueError):
                GameSettings(strength=strength)
        self.assertEqual(AI_STRENGTHS, ("easy", "medium", "hard"))

    def test_solver_dispatches_to_selected_strategy(self):
        strategies = {
            AIStrength.EASY: "run_easy",
            AIStrength.MEDIUM: "run_medium",
            AIStrength.HARD: "run_hard",
        }
        for strength, selected_method in strategies.items():
            with self.subTest(strength=strength):
                solver = AISolver(strength)
                solver._delay = 1
                with (
                    patch.object(solver, "run_easy") as run_easy,
                    patch.object(solver, "run_medium") as run_medium,
                    patch.object(solver, "run_hard") as run_hard,
                ):
                    self.assertTrue(solver.run(None))
                for method_name, method in (
                    ("run_easy", run_easy),
                    ("run_medium", run_medium),
                    ("run_hard", run_hard),
                ):
                    if method_name == selected_method:
                        method.assert_called_once_with(None)
                    else:
                        method.assert_not_called()


if __name__ == "__main__":
    unittest.main()
