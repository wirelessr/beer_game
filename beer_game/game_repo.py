from beer_game.player_repo import ROLES, PlayerRepo


class GameRepo:
    def __init__(self, game, db):
        self.db = db
        self.game = game

    def newGame(self):
        self.db.createGame(self.game)

    def register(self, player, role):
        self.db.addPlayer(self.game, player, role)

    def dispatch(self, order):
        for p in self.db.getDashboard(self.game)["players"]:
            player = PlayerRepo(self.game, p, "customer", self.db)
            player.purchase(order)

    def nextWeek(self):
        self.db.incrWeek(self.game)

    def retrievePlayer(self):
        return self.db.getPlayers(self.game)

    def reloadPlayerStat(self):
        ret = {}

        players = self.retrievePlayer()
        for p, roles in players.items():
            ret[p] = {}
            for role in roles:
                player = PlayerRepo(self.game, p, role, self.db)
                ret[p][role] = player.reloadStat()

        return ret


