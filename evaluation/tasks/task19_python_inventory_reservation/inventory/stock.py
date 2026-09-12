class StockLedger:
    def __init__(self) -> None:
        self._stock: dict[str, dict[str, int]] = {}

    def set(self, warehouse: str, sku: str, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("quantity cannot be negative")

        self._stock.setdefault(warehouse, {})[sku] = quantity

    def available(self, warehouse: str, sku: str) -> int:
        return self._stock.get(warehouse, {}).get(sku, 0)

    def total_available(self, sku: str) -> int:
        return sum(
            items.get(sku, 0)
            for items in self._stock.values()
        )

    def adjust(self, warehouse: str, sku: str, delta: int) -> None:
        next_quantity = self.available(warehouse, sku) + delta

        if next_quantity < 0:
            raise ValueError("stock cannot become negative")

        self._stock.setdefault(warehouse, {})[sku] = next_quantity
