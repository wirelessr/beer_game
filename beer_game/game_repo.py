from beer_game.adapter import PLAYER_TEMPLATE
from beer_game.config import CONFIG
from beer_game.player_repo import ROLES, PlayerRepo


class GameRepo:
    def __init__(self, game, db):
        self.db = db
        self.game = game

    def newGame(self):
        self.db.createGame(self.game)

    def endGame(self):
        self.db.removeGame(self.game)

    def getDashboard(self):
        return self.db.getDashboard(self.game)

    def dispatch(self, order):
        for p in self.getDashboard()["players"]:
            player = PlayerRepo(self.game, p, "customer", self.db)
            player.purchase(order)

    def nextWeek(self):
        self.db.incrWeek(self.game)

    # Get all players' online status
    # Return format
    # {
    #   player_id: {
    #       shop: <boolean>,
    #       retailer: <boolean>,
    #       factory: <boolean>,
    #   },
    #   ...
    # }
    def retrievePlayer(self):
        ret = {}

        players = self.db.getPlayers(self.game)
        for p in players:
            ret[p] = PLAYER_TEMPLATE() | players[p]

        return ret

    # factory找四週後的delivery
    # 其他角色找下位當週buy
    def getPurchasedRole(self):
        week = self.db.getDashboard(self.game)["week"]
        orders = self.db.getOrderByWeek(
            self.game, week, week + CONFIG.delivery_weeks
        )
        ret = {}

        for p, roles in orders.get(week, {}).items():
            ret[p] = {}
            for role in roles:
                prev_role = ROLES[ROLES.index(role) - 1]
                ret[p][prev_role] = (roles[role].get("buy") is not None)

        for p, roles in orders.get(week + CONFIG.delivery_weeks, {}).items():
            ret.setdefault(p, {})
            ret[p]["factory"] = (
                roles.get("factory", {}).get("delivery") is not None
            )

        return ret

    def reloadPlayerStat(self):
        ret = {}

        players = self.retrievePlayer()
        orders = self.getPurchasedRole()

        for p, roles in players.items():
            ret[p] = {}
            for role in roles:
                player = PlayerRepo(self.game, p, role, self.db)
                ret[p][role] = player.reloadStat() | {"enabled": roles[role]}
                ret[p][role] |= {
                    "purchased": orders.get(p, {}).get(role, False)
                }

        return ret
