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

        self.game.nextWeek(3)
        self.assertEqual(
            self.db.data[self.game_name]["week"], 4, "week not incremented"
        )

    def test_register(self):
        self.game.newGame()
        self.game.register("player1", "shop")

        r = self.db.getPlayers(self.game_name)
        self.assertIn("player1", r, "player not registered")
        self.assertTrue(r["player1"]["shop"], "wrong player type")

        self.game.register("player2", "factory")

        r = self.db.getPlayers(self.game_name)
        self.assertIn("player2", r, "player not registered")
        self.assertTrue(r["player2"]["factory"], "wrong player type")

        self.assertEqual(len(r), 2, "wrong number of players")
