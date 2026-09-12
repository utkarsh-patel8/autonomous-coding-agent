from collections import defaultdict
from decimal import Decimal
from .models import Transaction

class Reconciler:
    def captured_by_merchant(self, transactions: list[Transaction]):
        totals = defaultdict(lambda: Decimal("0"))
        for tx in transactions:
            if tx.status != "captured":
                continue
            sign = Decimal("1")
            if tx.kind == "refund":
                # BUG: refunds must reduce captured gross.
                sign = Decimal("1")
            totals[tx.merchant_id] += sign * tx.amount
        return dict(totals)
