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
        self.shop.register()
        self.retailer.register()
        self.factory.register()

    def test_register(self):
        self.game.newGame()
        self.shop.register()

        r = self.game.retrievePlayer()
        self.assertIn("Player 1", r, "player not registered")
        self.assertTrue(r["Player 1"]["shop"], "wrong player type")
        self.assertFalse(r["Player 1"]["retailer"], "wrong player type")

        factory2 = PlayerRepo("Game 1", "Player 2", "factory", self.db)
        factory2.register()

        r = self.game.retrievePlayer()
        self.assertIn("Player 2", r, "player not registered")
        self.assertFalse(r["Player 2"]["shop"], "wrong player type")
        self.assertTrue(r["Player 2"]["factory"], "wrong player type")

        self.assertEqual(len(r), 2, "wrong number of players")

    def test_game_start(self):
        w0 = self.shop.reloadStat()
        self.assertEqual(w0["week"], 0)
        self.assertEqual(w0["inventory"], 4)
        self.assertEqual(w0["cost"], 4)

    def test_game_start_and_buy(self):
        self.game.dispatch(1)

        w0 = self.shop.reloadStat()
        self.assertEqual(w0["week"], 0)
        self.assertEqual(w0["inventory"], 3)
        self.assertEqual(w0["cost"], 3)

    def test_game_start_and_buy_out_of_stock(self):
        self.game.dispatch(5)

        w0 = self.shop.reloadStat()
        self.assertEqual(w0["week"], 0)
        self.assertEqual(w0["inventory"], 0)
        self.assertEqual(w0["out_of_stock"], 1)
        self.assertEqual(w0["cost"], 2)

    def test_idempotency(self):
        self.game.dispatch(1)
        self.game.dispatch(2)

        w0 = self.shop.reloadStat()
        self.assertEqual(w0["week"], 0)
        self.assertEqual(w0["inventory"], 2)
        self.assertEqual(w0["out_of_stock"], 0)
        self.assertEqual(w0["cost"], 2)

        # retrieve again
        w0 = self.shop.reloadStat()
        self.assertEqual(w0["week"], 0)
        self.assertEqual(w0["inventory"], 2)
        self.assertEqual(w0["out_of_stock"], 0)
        self.assertEqual(w0["cost"], 2)

    def test_purchase_idempotency(self):
        self.shop.purchase(1)
        self.shop.purchase(2)

        retailer_w0 = self.retailer.reloadStat()
        self.assertEqual(retailer_w0["week"], 0)
        self.assertEqual(retailer_w0["inventory"], 2)
        shop_w0 = self.shop.reloadStat()
        self.assertEqual(shop_w0["inventory"], 4)

        self.game.nextWeek()
        self.retailer.reloadStat()
        self.shop.reloadStat()

        self.game.nextWeek()
        self.retailer.reloadStat()
        self.shop.reloadStat()

        self.game.nextWeek()
        self.retailer.reloadStat()
        self.shop.reloadStat()

        self.game.nextWeek()
        self.retailer.reloadStat()
        self.shop.reloadStat()

        retailer_w4 = self.retailer.reloadStat()
        self.assertEqual(retailer_w4["week"], 4)
        self.assertEqual(retailer_w4["inventory"], 2)
        shop_w4 = self.shop.reloadStat()
        self.assertEqual(shop_w4["inventory"], 6)

    def test_game_next_week(self):
        self.game.nextWeek()
        self.game.dispatch(1)

        w1 = self.shop.reloadStat()
        self.assertEqual(w1["week"], 1)
        self.assertEqual(w1["inventory"], 3)
        self.assertEqual(w1["cost"], 3)

        self.game.nextWeek()
        self.game.dispatch(5)

        w2 = self.shop.reloadStat()
        self.assertEqual(w2["week"], 2)
        self.assertEqual(w2["inventory"], 0)
        self.assertEqual(w2["out_of_stock"], 2)
        self.assertEqual(w2["cost"], 3 + 2 * 2)

        self.game.nextWeek()
        self.game.dispatch(3)

        w3 = self.shop.reloadStat()
        self.assertEqual(w3["week"], 3)
        self.assertEqual(w3["inventory"], 0)
        self.assertEqual(w3["out_of_stock"], 2 + 3)
        self.assertEqual(w3["cost"], 3 + 2 * 2 + (2 + 3) * 2)

    def test_purchase_and_fulfill(self):
        self.shop.purchase(1)

        retailer_w0 = self.retailer.reloadStat()
        self.assertEqual(retailer_w0["week"], 0)
        self.assertEqual(retailer_w0["inventory"], 3)
        shop_w0 = self.shop.reloadStat()
        self.assertEqual(shop_w0["inventory"], 4)

        self.game.nextWeek()

        retailer_w1 = self.retailer.reloadStat()
        self.assertEqual(retailer_w1["week"], 1)
        self.assertEqual(retailer_w1["inventory"], 3)
        shop_w1 = self.shop.reloadStat()
        self.assertEqual(shop_w1["inventory"], 4)

        self.game.nextWeek()

        retailer_w2 = self.retailer.reloadStat()
        self.assertEqual(retailer_w2["week"], 2)
        self.assertEqual(retailer_w2["inventory"], 3)
        shop_w2 = self.shop.reloadStat()
        self.assertEqual(shop_w2["inventory"], 4)

        self.game.nextWeek()

        retailer_w3 = self.retailer.reloadStat()
        self.assertEqual(retailer_w3["week"], 3)
        self.assertEqual(retailer_w3["inventory"], 3)
        shop_w3 = self.shop.reloadStat()
        self.assertEqual(shop_w3["inventory"], 4)

        self.game.nextWeek()
        retailer_w4 = self.retailer.reloadStat()
        self.assertEqual(retailer_w4["week"], 4)
        self.assertEqual(retailer_w4["inventory"], 3)
        shop_w4 = self.shop.reloadStat()
        self.assertEqual(shop_w4["inventory"], 4 + 1)

    def test_factory_fulfill(self):
        self.factory.purchase(1)

        factory_w0 = self.factory.reloadStat()
        self.assertEqual(factory_w0["week"], 0)
        self.assertEqual(factory_w0["inventory"], 4)

        self.game.nextWeek()
        self.factory.reloadStat()

        self.game.nextWeek()
        self.factory.reloadStat()

        self.game.nextWeek()
        self.factory.reloadStat()

        self.game.nextWeek()
        factory_w4 = self.factory.reloadStat()
        self.assertEqual(factory_w4["week"], 4)
        self.assertEqual(factory_w4["inventory"], 4 + 1)

    def test_gm_reload_player(self):
        self.shop.purchase(1)

        r = self.game.reloadPlayerStat()
        self.assertEqual(r["Player 1"]["retailer"]["inventory"], 3)
