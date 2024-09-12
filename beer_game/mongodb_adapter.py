from beer_game.adapter import GAME_TEMPLATE, STAT_TEMPLATE

import time
from functools import wraps


def retry(retries=3, delay=1, exception_to_check=Exception):
    def decorator_retry(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except exception_to_check as e:
                    last_exception = e
                    print(f"Attempt {attempt + 1}/{retries} failed: {e}")
                    time.sleep(delay)
            raise last_exception

        return wrapper

    return decorator_retry


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
    @retry(retries=3, delay=0.1)
    def saveStat(self, identifier, week, inventory, cost, out_of_stock):
        game, player, role = identifier
        pk = {"game": game, "player": player, "role": role, "week": week}
        value = {
            "inventory": inventory,
            "cost": cost,
            "out_of_stock": out_of_stock,
        }
        return self._fam(self.stat, pk, value)

    @retry(retries=3, delay=0.1)
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

    @retry(retries=3, delay=0.1)
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
    @retry(retries=3, delay=0.1)
    def createGame(self, game):
        game_data = GAME_TEMPLATE()
        return self._fam(self.game, {"name": game}, game_data)

    @retry(retries=3, delay=0.1)
    def removeGame(self, game):
        self.game.delete_one({"name": game})
        self.order.delete_many({"game": game})
        self.stat.delete_many({"game": game})

    @retry(retries=3, delay=0.1)
    def addPlayer(self, game, player, role):
        return self.game.update_one(
            {"name": game}, {"$set": {f"players.{player}.{role}": True}}
        )

    def getPlayers(self, game):
        game = self.game.find_one({"name": game})
        return game["players"] if game else None

    @retry(retries=3, delay=0.1)
    def incrWeek(self, game):
        return self.game.update_one({"name": game}, {"$inc": {"week": 1}})

    def getOrderByWeek(self, game, start_week, end_week):
        end_week = end_week or start_week
        ret = {} # {week: {player: {role: {buy, delivery}}}}

        orders = self.order.find({
            "game": game,
            "week": {"$gte": start_week, "$lte": end_week}
        })

        for order in orders:
            week = order["week"]
            player = order["player"]
            role = order["role"]
            order_type = order["type"]

            if week not in ret:
                ret[week] = {}

            if player not in ret[week]:
                ret[week][player] = {}

            if role not in ret[week][player]:
                ret[week][player][role] = {}

            ret[week][player][role][order_type] = order["qty"]

        return ret
