import unittest

from beer_game.adapter import DictDB
from beer_game.game_repo import GameRepo


class GameTestCase(unittest.TestCase):
    def setUp(self):
        self.db = DictDB()
        self.game_name = "BaseGame"
        self.game = GameRepo(self.game_name, self.db)

    def test_new_game(self):
        self.game.newGame()
        self.assertIn(self.game_name, self.db.data.keys(), "game not created")

        game2 = GameRepo("Game2", self.db)
        game2.newGame()
        self.assertIn(self.game_name, self.db.data.keys(), "game not created")
        self.assertIn("Game2", self.db.data.keys(), "game not created")

    def test_next_week(self):
        self.game.newGame()
        self.game.nextWeek()
        self.assertEqual(
            self.db.data[self.game_name]["week"], 1, "week not incremented"
        )

        self.game.nextWeek()
        self.assertEqual(
            self.db.data[self.game_name]["week"], 2, "week not incremented"
        )
