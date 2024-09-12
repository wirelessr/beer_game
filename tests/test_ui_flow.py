import unittest

import pymongo

from beer_game.game_repo import GameRepo
from beer_game.mongodb_adapter import MongoDB
from beer_game.player_repo import PlayerRepo


class IntegrationTestCase(unittest.TestCase):

    def setUp(self):
        self.client = pymongo.MongoClient()
        self.adapter = MongoDB(self.client)
        self.game = GameRepo("game1", self.adapter)
        self.player = PlayerRepo("game1", "player1", "shop", self.adapter)

    def tearDown(self) -> None:
        self.game.endGame()

    def test_do_nothing(self):
        self.assertEqual(1, 1)

    def test_create_game__noraml(self):
        self.game.newGame()
        self.game.reloadPlayerStat()

    def test_create_game__with_player(self):
        self.game.newGame()
        self.player.register()
        self.game.reloadPlayerStat()

    def test_create_game__with_player__with_buy(self):
        self.game.newGame()
        self.player.register()
        self.player.purchase(10)
        self.game.reloadPlayerStat()
