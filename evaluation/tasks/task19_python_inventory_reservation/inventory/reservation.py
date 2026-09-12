from dataclasses import dataclass

from inventory.stock import StockLedger


@dataclass(frozen=True)
class Allocation:
    warehouse: str
    sku: str
    quantity: int


class ReservationService:
    def __init__(self, ledger: StockLedger) -> None:
        self._ledger = ledger

    def reserve(
        self,
        sku: str,
        quantity: int,
        warehouse_order: list[str],
    ) -> list[Allocation]:
        if quantity <= 0:
            raise ValueError("quantity must be positive")

        if self._ledger.total_available(sku) < quantity:
            raise RuntimeError("insufficient stock")

        allocations: list[Allocation] = []
        remaining = quantity

        for warehouse in warehouse_order:
            if remaining == 0:
                break

            available = self._ledger.available(warehouse, sku)
            if available == 0:
                continue

            # BUG: later warehouses must allocate only the remaining quantity.
            take = min(available, quantity)
            self._ledger.adjust(warehouse, sku, -take)
            allocations.append(Allocation(warehouse, sku, take))
            remaining -= take

        if remaining != 0:
            raise RuntimeError("warehouse order does not cover enough stock")

        return allocations

    def release(self, allocations: list[Allocation]) -> None:
        for allocation in allocations:
            # BUG: releasing a reservation must restore stock.
            self._ledger.adjust(
                allocation.warehouse,
                allocation.sku,
                -allocation.quantity,
            )
