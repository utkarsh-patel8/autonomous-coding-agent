from dataclasses import dataclass
from decimal import Decimal
from .money import money
from .models import Transaction

@dataclass(frozen=True)
class FeePolicy:
    percentage: Decimal
    fixed: Decimal

class FeeEngine:
    def __init__(self, policies: dict[str, FeePolicy]):
        self.policies = policies

    def fee_for(self, transaction: Transaction) -> Decimal:
        if transaction.kind == "refund":
            return Decimal("0.00")
        policy = self.policies[transaction.merchant_id]
        # BUG: fixed fee is incorrectly charged twice.
        return money(transaction.amount * policy.percentage + policy.fixed * 2)
