from beer_game.adapter import PLAYER_TEMPLATE
from beer_game.config import CONFIG
from beer_game.player_repo import ROLES, PlayerRepo
from typing import TypedDict


class PlayerStat(TypedDict):
    week: int
    inventory: int
    inventory_this_week: int
    order: int
    delivery: int
    cost: int
    cost_this_week: int
    out_of_stock: int
    out_of_stock_this_week: int
    can_sell: int
    should_sell: int
    sell: int
    enabled: bool
    purchased: bool


class GameRepo:
    def __init__(self, game: str, db):
        self.db = db
        self.game = game

    def newGame(self):
        self.db.createGame(self.game)

    def endGame(self):
        self.db.removeGame(self.game)

    def getDashboard(self) -> dict:
        return self.db.getDashboard(self.game)

    def dispatch(self, order: int):
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
    def retrievePlayer(self) -> dict[str, dict[str, bool]]:
        ret: dict[str, dict[str, bool]] = {}

        players = self.db.getPlayers(self.game)
        for p in players:
            ret[p] = PLAYER_TEMPLATE() | players[p]

        return ret

    # factory找四週後的delivery
    # 其他角色找下位當週buy
    # Return format
    # {
    #   player_id: {
    #       shop: <boolean>,
    #       retailer: <boolean>,
    #       factory: <boolean>,
    #   },
    #   ...
    # }
    def getPurchasedRole(self) -> dict[str, dict[str, bool]]:
        week = self.db.getDashboard(self.game)["week"]
        orders = self.db.getOrderByWeek(
            self.game, week, week + CONFIG.delivery_weeks
        )
        ret: dict[str, dict[str, bool]] = {}

        for p, roles in orders.get(week, {}).items():
            ret[p] = {}
            for role in roles:
                prev_role = ROLES[ROLES.index(role) - 1]
                ret[p][prev_role] = roles[role].get("buy") is not None

        for p, roles in orders.get(week + CONFIG.delivery_weeks, {}).items():
            ret.setdefault(p, {})
            ret[p]["factory"] = (
                roles.get("factory", {}).get("delivery") is not None
            )

        return ret

    # Reload player statistics
    # Return format
    # {
    #   player_id: {
    #       role: PlayerStat  # Specific fields are defined in PlayerStat
    #   },
    #   ...
    # }
    def reloadPlayerStat(self) -> dict[str, dict[str, PlayerStat]]:
        ret: dict[str, dict[str, PlayerStat]] = {}

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
