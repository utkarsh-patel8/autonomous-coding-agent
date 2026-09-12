from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    merchant_id: str
    amount: Decimal
    currency: str
    kind: str = "sale"  # sale | refund
    status: str = "captured"

@dataclass(frozen=True)
class SettlementLine:
    merchant_id: str
    gross: Decimal
    fees: Decimal
    net: Decimal
    currency: str
