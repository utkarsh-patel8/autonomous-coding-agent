from inventory.stock import StockLedger


def available_to_sell(ledger: StockLedger, sku: str) -> int:
    return ledger.total_available(sku)
