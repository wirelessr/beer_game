from beer_game.config import CONFIG


def GAME_TEMPLATE():
    return {"week": 0, "players": {}}


def ORDER_TEMPLATE():
    return {"buy": 0, "delivery": 0}


def STAT_TEMPLATE():
    return {
        "inventory": CONFIG.init_inventory,
        "cost": 0,
        "out_of_stock": 0,
    }  # 預先派發4個庫存


def PLAYER_TEMPLATE():
    return {
        "shop": False,
        "retailer": False,
        "factory": False,
    }


class DictDB:
    def __init__(self):
        self.data = {"stat": {}, "order": {}}

    def saveStat(self, identifier, week, inventory, cost, out_of_stock):
        pk = (identifier, week)
        self.data["stat"].setdefault(pk, STAT_TEMPLATE())
        self.data["stat"][pk]["inventory"] = inventory
        self.data["stat"][pk]["cost"] = cost
        self.data["stat"][pk]["out_of_stock"] = out_of_stock

    def saveOrder(self, order, week, game, player, role):
        pk = ((game, player, role), week)
        self.data["order"].setdefault(pk, ORDER_TEMPLATE())
        self.data["order"][pk]["buy"] = order

    def saveDelivery(self, delivery, week, game, player, role):
        pk = ((game, player, role), week)
        self.data["order"].setdefault(pk, ORDER_TEMPLATE())
        self.data["order"][pk]["delivery"] = delivery

    def getStat(self, identifier, week):
        pk = (identifier, week)
        return self.data["stat"].get(pk, STAT_TEMPLATE())

    def getInventory(self, identifier, week):
        return self.getStat(identifier, week)["inventory"]

    def getCost(self, identifier, week):
        return self.getStat(identifier, week)["cost"]

    def getOutOfStock(self, identifier, week):
        return self.getStat(identifier, week)["out_of_stock"]

    def getOrder(self, identifier, week):
        pk = (identifier, week)
        return self.data["order"].get(pk, ORDER_TEMPLATE())["buy"]

    def getDashboard(self, game):
        gameInfo = self.data.setdefault(game, GAME_TEMPLATE())
        return gameInfo

    def getDelivery(self, identifier, week):
        pk = (identifier, week)
        return self.data["order"].get(pk, ORDER_TEMPLATE())["delivery"]

    def createGame(self, game):
        self.data[game] = GAME_TEMPLATE()

    def addPlayer(self, game, player, role):
        gameInfo = self.data.setdefault(game, GAME_TEMPLATE())
        gameInfo["players"].setdefault(
            player, {"shop": False, "retailer": False, "factory": False}
        )
        gameInfo["players"][player][role] = True

    def getPlayers(self, game):
        gameInfo = self.data.setdefault(game, GAME_TEMPLATE())
        return gameInfo["players"]

    def incrWeek(self, game):
        gameInfo = self.data.setdefault(game, GAME_TEMPLATE())
        gameInfo["week"] += 1

    def getOrderByWeek(self, game, start_week, end_week):
        end_week = end_week or start_week
        ret = {} # {week: {player: {role: {buy, delivery}}}}
        players = self.getPlayers(game)

        for week in range(start_week, end_week + 1):
            ret[week] = {}
            for p, roles in players.items():
                ret[week][p] = {}
                for role in roles:
                    pk = ((game, p, role), week)
                    ret[week][p][role] = self.data["order"].get(pk, {})

        return ret
