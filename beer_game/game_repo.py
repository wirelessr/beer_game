from beer_game.player_repo import PlayerRepo


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

    def nextWeek(self, delta=1):
        self.db.incrWeek(self.game, delta)

    def retrievePlayer(self):
        return self.db.getPlayers(self.game)
