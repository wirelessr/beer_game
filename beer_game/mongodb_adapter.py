from beer_game.adapter import GAME_TEMPLATE, STAT_TEMPLATE


class MongoDB:
    def __init__(self, client):
        self.db = client.game
        self.stat = self.db.stat
        self.order = self.db.order
        self.game = self.db.game

    @staticmethod
    def _fam(coll, pk, value):
        return coll.find_one_and_update(pk, {"$set": value}, upsert=True)

    def getDashboard(self, game):
        return self.game.find_one({"name": game})

    # PlayerRepo
    def saveStat(self, identifier, week, inventory, cost, out_of_stock):
        game, player, role = identifier
        pk = {"game": game, "player": player, "role": role, "week": week}
        value = {
            "inventory": inventory,
            "cost": cost,
            "out_of_stock": out_of_stock,
        }
        return self._fam(self.stat, pk, value)

    def saveOrder(self, order, week, game, player, role):
        pk = {
            "game": game,
            "player": player,
            "role": role,
            "week": week,
            "type": "buy",
        }
        value = {"qty": order}
        return self._fam(self.order, pk, value)

    def saveDelivery(self, delivery, week, game, player, role):
        pk = {
            "game": game,
            "player": player,
            "role": role,
            "week": week,
            "type": "delivery",
        }
        value = {"qty": delivery}
        return self._fam(self.order, pk, value)

    def getStat(self, identifier, week):
        game, player, role = identifier
        pk = {"game": game, "player": player, "role": role, "week": week}
        return self.stat.find_one(pk) or STAT_TEMPLATE()

    def getOrder(self, identifier, week):
        game, player, role = identifier
        pk = {
            "game": game,
            "player": player,
            "role": role,
            "week": week,
            "type": "buy",
        }
        return (self.order.find_one(pk) or {}).get("qty", 0)

    def getDelivery(self, identifier, week):
        game, player, role = identifier
        pk = {
            "game": game,
            "player": player,
            "role": role,
            "week": week,
            "type": "delivery",
        }
        return (self.order.find_one(pk) or {}).get("qty", 0)

    def getDashBoard(self, game):
        return self.game.find_one({"name": game})

    # GameRepo
    def createGame(self, game):
        game_data = GAME_TEMPLATE()
        return self._fam(self.game, {"name": game}, game_data)

    def addPlayer(self, game, player, role):
        return self.game.update_one(
            {"name": game}, {"$set": {f"players.{player}.{role}": True}}
        )

    def getPlayers(self, game):
        return self.game.find_one({"name": game})["players"]

    def incrWeek(self, game):
        return self.game.update_one({"name": game}, {"$inc": {"week": 1}})
