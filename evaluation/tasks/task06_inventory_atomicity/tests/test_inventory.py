import pytest

from inventory.service import Inventory


def test_successful_sale_updates_stock():
    inv = Inventory({"pen": 5})
    assert inv.sell("pen", 2) == 3
    assert inv.stock["pen"] == 3


def test_failed_sale_keeps_original_stock():
    inv = Inventory({"pen": 2})

    with pytest.raises(ValueError, match="insufficient stock"):
        inv.sell("pen", 3)

    assert inv.stock["pen"] == 2
