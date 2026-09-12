class Inventory:
    def __init__(self, stock):
        self.stock = dict(stock)

    def sell(self, item, quantity):
        self.stock[item] -= quantity

        if self.stock[item] < 0:
            raise ValueError("insufficient stock")

        return self.stock[item]
