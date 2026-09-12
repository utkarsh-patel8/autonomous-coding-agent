import pytest

from inventory.report import available_to_sell
from inventory.reservation import ReservationService
from inventory.stock import StockLedger


def test_split_reservation_uses_remaining_quantity():
    ledger = StockLedger()
    ledger.set("east", "cpu", 3)
    ledger.set("west", "cpu", 10)
    service = ReservationService(ledger)

    allocations = service.reserve("cpu", 5, ["east", "west"])

    assert len(allocations) == 2
    assert allocations[0].quantity == 3
    assert allocations[1].quantity == 2
    assert ledger.available("east", "cpu") == 0
    assert ledger.available("west", "cpu") == 8
    assert available_to_sell(ledger, "cpu") == 8


def test_release_restores_all_allocated_stock():
    ledger = StockLedger()
    ledger.set("a", "gpu", 2)
    ledger.set("b", "gpu", 4)
    service = ReservationService(ledger)

    allocations = service.reserve("gpu", 5, ["a", "b"])

    assert available_to_sell(ledger, "gpu") == 1
    service.release(allocations)
    assert ledger.available("a", "gpu") == 2
    assert ledger.available("b", "gpu") == 4
    assert available_to_sell(ledger, "gpu") == 6


def test_insufficient_stock_is_atomic():
    ledger = StockLedger()
    ledger.set("a", "ram", 2)
    ledger.set("b", "ram", 1)
    service = ReservationService(ledger)

    with pytest.raises(RuntimeError):
        service.reserve("ram", 5, ["a", "b"])

    assert ledger.available("a", "ram") == 2
    assert ledger.available("b", "ram") == 1


def test_reservation_respects_warehouse_priority():
    ledger = StockLedger()
    ledger.set("primary", "ssd", 10)
    ledger.set("backup", "ssd", 10)
    service = ReservationService(ledger)

    allocations = service.reserve("ssd", 4, ["primary", "backup"])

    assert len(allocations) == 1
    assert allocations[0].warehouse == "primary"
    assert allocations[0].quantity == 4
    assert ledger.available("primary", "ssd") == 6
    assert ledger.available("backup", "ssd") == 10


def test_incomplete_warehouse_order_is_atomic():
    ledger = StockLedger()
    ledger.set("preferred", "nic", 2)
    ledger.set("other", "nic", 10)
    service = ReservationService(ledger)

    with pytest.raises(RuntimeError):
        service.reserve("nic", 5, ["preferred"])

    assert ledger.available("preferred", "nic") == 2
    assert ledger.available("other", "nic") == 10
