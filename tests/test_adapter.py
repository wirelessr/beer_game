import unittest
import pymongo

from beer_game.mongodb_adapter import MongoDB


class AdapterTestCase(unittest.TestCase):
    def setUp(self):
        self.client = pymongo.MongoClient()
        self.adapter = MongoDB(self.client)

    def tearDown(self):
        self.client.drop_database("stat")
        self.client.drop_database("order")
        self.client.drop_database("game")

    def test_create_game(self):
        self.adapter.createGame("game1")
        game = self.adapter.getDashBoard("game1")
        self.assertEqual(game["name"], "game1")

        players = self.adapter.getPlayers("game1")
        self.assertEqual(len(players), 0)

        dashboard = self.adapter.getDashBoard("game1")
        self.assertEqual(dashboard["week"], 0)

    def test_add_player(self):
        self.adapter.createGame("game1")

        self.adapter.addPlayer("game1", "player1", "shop")
        players = self.adapter.getPlayers("game1")
        self.assertEqual(len(players), 1)
        self.assertEqual(players["player1"], {"shop": True})
        self.assertNotIn("retailer", players["player1"])

        self.adapter.addPlayer("game1", "player2", "factory")
        players = self.adapter.getPlayers("game1")
        self.assertEqual(len(players), 2)
        self.assertEqual(players["player2"], {"factory": True})
        self.assertNotIn("shop", players["player2"])

    def test_incr_week(self):
        self.adapter.createGame("game1")
        self.adapter.incrWeek("game1")

        game = self.adapter.getDashBoard("game1")
        self.assertEqual(game["week"], 1)

    def test_stat_normal(self):
        identifier = ("game1", "player1", "shop")

        stat = self.adapter.getStat(identifier, 0)
        self.assertEqual(stat["inventory"], 4)
        self.assertEqual(stat["cost"], 0)
        self.assertEqual(stat["out_of_stock"], 0)

        self.adapter.saveStat(identifier, 1, 1, 2, 3)

        stat1 = self.adapter.getStat(identifier, 1)
        self.assertEqual(stat1["inventory"], 1)
        self.assertEqual(stat1["cost"], 2)
        self.assertEqual(stat1["out_of_stock"], 3)

        stat = self.adapter.getStat(identifier, 0)
        self.assertEqual(stat["inventory"], 4)
        self.assertEqual(stat["cost"], 0)
        self.assertEqual(stat["out_of_stock"], 0)

    def test_order_normal(self):
        identifier = ("game1", "player1", "shop")

        order = self.adapter.getOrder(identifier, 0)
        self.assertEqual(order, 0)

        self.adapter.saveOrder(10, 1, *identifier)
        order1 = self.adapter.getOrder(identifier, 1)
        self.assertEqual(order1, 10)
        order0 = self.adapter.getOrder(identifier, 0)
        self.assertEqual(order0, 0)

        # test idenpotency
        self.adapter.saveOrder(10, 1, *identifier)
        order1 = self.adapter.getOrder(identifier, 1)
        self.assertEqual(order1, 10)

    def test_delivery_normal(self):
        identifier = ("game1", "player1", "shop")

        order = self.adapter.getDelivery(identifier, 0)
        self.assertEqual(order, 0)

        self.adapter.saveDelivery(10, 1, *identifier)
        order1 = self.adapter.getDelivery(identifier, 1)
        self.assertEqual(order1, 10)
        order0 = self.adapter.getDelivery(identifier, 0)
        self.assertEqual(order0, 0)

        # test idenpotency
        self.adapter.saveDelivery(10, 1, *identifier)
        order1 = self.adapter.getDelivery(identifier, 1)
        self.assertEqual(order1, 10)

    def test_get_order_by_week(self):
        identifier = ("game1", "player1", "shop")

        self.adapter.saveOrder(10, 1, *identifier)
        self.adapter.saveOrder(30, 3, *identifier)

        identifier = ("game1", "player2", "retailer")
        self.adapter.saveDelivery(10, 1, *identifier)
        self.adapter.saveDelivery(20, 2, *identifier)

        orders = self.adapter.getOrderByWeek("game1", 1, 3)

        self.assertEqual(len(orders), 3)
        self.assertEqual(
            orders[1],
            {
                "player1": {"shop": {"buy": 10}},
                "player2": {"retailer": {"delivery": 10}},
            },
        )
        self.assertEqual(
            orders[2], {"player2": {"retailer": {"delivery": 20}}}
        )
        self.assertEqual(
            orders[3],
            {
                "player1": {"shop": {"buy": 30}},
            },
        )

    def test_remove_game(self):
        # order
        identifier = ("game1", "player1", "shop")
        self.adapter.saveOrder(10, 1, *identifier)
        order1 = self.adapter.getOrder(identifier, 1)
        self.assertEqual(order1, 10)
        # stat
        self.adapter.saveStat(identifier, 1, 1, 2, 3)
        stat1 = self.adapter.getStat(identifier, 1)
        self.assertEqual(stat1["inventory"], 1)
        self.assertEqual(stat1["cost"], 2)
        self.assertEqual(stat1["out_of_stock"], 3)
        # game
        self.adapter.createGame("game1")
        self.adapter.addPlayer(*identifier)
        players = self.adapter.getPlayers("game1")
        self.assertEqual(len(players), 1)

        self.adapter.removeGame("game1")

        order1 = self.adapter.getOrder(identifier, 1)
        self.assertEqual(order1, 0)
        stat1 = self.adapter.getStat(identifier, 1)
        players = self.adapter.getPlayers("game1")
        self.assertIsNone(players)
