ROLES = ["customer", "shop", "retailer", "factory"]


class PlayerRepo:
    def __init__(self, game, player, role, db):
        self.db = db  # 訂單表(下單、回補)、狀態表(庫存、成本)
        self.game = game
        self.player = player
        self.role = role
        self.identifier = (game, player, role)

    def reloadStat(self):
        # 當週的初始狀態
        week = self.db.getDashboard(self.game)["week"]
        order_this_week = self.db.getOrder(
            self.identifier, week
        )  # 來自上週上一個角色的訂單 (訂單表)
        delivery_this_week = self.db.getDelivery(
            self.identifier, week
        )  # 來自四週前下單 (訂單表)
        stat_this_week = self.db.getStat(self.identifier, week)
        # 來自上週庫存結果 (狀態表)
        inventory_this_week = stat_this_week["inventory"]
        cost_this_week = stat_this_week["cost"]  # 來自自己上週結果 (狀態表)
        # 來自自己上週結果 (狀態表)
        out_of_stock_this_week = stat_this_week["out_of_stock"]

        # 當下的庫存是上週庫存 + 這週到貨 - 這週售出
        # 若是上週庫存 + 這週到貨不足以售出
        # 那缺項要計入成本

        can_sell = inventory_this_week + delivery_this_week  # 當週可賣
        should_sell = order_this_week + out_of_stock_this_week  # 當週應賣
        sell = should_sell if can_sell >= should_sell else can_sell  # 當週賣出
        self._fulfill(sell, week + 4)  # 四週到貨

        inventory = can_sell - sell
        out_of_stock = should_sell - sell

        cost = cost_this_week + out_of_stock * 2 + inventory

        # 顯示週數、庫存、成本、這週到貨、這週訂單、總欠貨
        stat = {
            "week": week,
            "inventory": inventory,
            "inventory_this_week": inventory_this_week,
            "order": order_this_week,
            "delivery": delivery_this_week,
            "cost": cost,
            "cost_this_week": cost_this_week,
            "out_of_stock": out_of_stock,
            "out_of_stock_this_week": out_of_stock_this_week,
            "can_sell": can_sell,
            "should_sell": should_sell,
            "sell": sell,
        }

        # Save for next week
        self._saveStat(stat, week + 1)
        return stat

    def purchase(self, order):
        gameInfo = self.db.getDashboard(self.game)
        week = gameInfo["week"]

        self._sendOrder(order, week)

    def _fulfill(self, sell, week):
        if sell <= 0:
            return

        prev_role = ROLES[ROLES.index(self.role) - 1]

        self.db.saveDelivery(sell, week, self.game, self.player, prev_role)

    def _saveStat(self, stat, week):
        self.db.saveStat(
            self.identifier,
            week,
            stat["inventory"],
            stat["cost"],
            stat["out_of_stock"],
        )

    def _sendOrder(self, order, week):
        if order <= 0:
            return

        if self.role == "factory":
            self.db.saveDelivery(
                order, week + 4, self.game, self.player, "factory"
            )
        else:
            next_role = ROLES[ROLES.index(self.role) + 1]
            self.db.saveOrder(order, week, self.game, self.player, next_role)
