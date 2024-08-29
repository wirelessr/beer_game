import unittest

from beer_game.adapter import DictDB
from beer_game.game_repo import GameRepo
from beer_game.player_repo import PlayerRepo


class IntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.db = DictDB()
        self.game = GameRepo("Game 1", self.db)
        self.shop = PlayerRepo("Game 1", "Player 1", "shop", self.db)
        self.retailer = PlayerRepo("Game 1", "Player 1", "retailer", self.db)
        self.factory = PlayerRepo("Game 1", "Player 1", "factory", self.db)
        self.game.register("Player 1", "shop")
        self.game.register("Player 1", "retailer")
        self.game.register("Player 1", "factory")

    def test_game_start(self):
        w0 = self.shop.retrieveStat()
        self.assertEqual(w0["week"], 0)
        self.assertEqual(w0["inventory"], 4)
        self.assertEqual(w0["cost"], 4)

    def test_game_start_and_buy(self):
        self.game.dispatch(1)

        w0 = self.shop.retrieveStat()
        self.assertEqual(w0["week"], 0)
        self.assertEqual(w0["inventory"], 3)
        self.assertEqual(w0["cost"], 3)

    def test_game_start_and_buy_out_of_stock(self):
        self.game.dispatch(5)

        w0 = self.shop.retrieveStat()
        self.assertEqual(w0["week"], 0)
        self.assertEqual(w0["inventory"], 0)
        self.assertEqual(w0["out_of_stock"], 1)
        self.assertEqual(w0["cost"], 2)

    def test_idempotency(self):
        self.game.dispatch(1)
        self.game.dispatch(2)

        w0 = self.shop.retrieveStat()
        self.assertEqual(w0["week"], 0)
        self.assertEqual(w0["inventory"], 2)
        self.assertEqual(w0["out_of_stock"], 0)
        self.assertEqual(w0["cost"], 2)

        # retrieve again
        w0 = self.shop.retrieveStat()
        self.assertEqual(w0["week"], 0)
        self.assertEqual(w0["inventory"], 2)
        self.assertEqual(w0["out_of_stock"], 0)
        self.assertEqual(w0["cost"], 2)

    def test_game_next_week(self):
        self.game.nextWeek()
        self.game.dispatch(1)

        w1 = self.shop.retrieveStat()
        self.assertEqual(w1["week"], 1)
        self.assertEqual(w1["inventory"], 3)
        self.assertEqual(w1["cost"], 3)

        self.game.nextWeek()
        self.game.dispatch(5)

        w2 = self.shop.retrieveStat()
        self.assertEqual(w2["week"], 2)
        self.assertEqual(w2["inventory"], 0)
        self.assertEqual(w2["out_of_stock"], 2)
        self.assertEqual(w2["cost"], 3 + 2 * 2)

        self.game.nextWeek()
        self.game.dispatch(3)

        w3 = self.shop.retrieveStat()
        self.assertEqual(w3["week"], 3)
        self.assertEqual(w3["inventory"], 0)
        self.assertEqual(w3["out_of_stock"], 2 + 3)
        self.assertEqual(w3["cost"], 3 + 2 * 2 + (2 + 3) * 2)
