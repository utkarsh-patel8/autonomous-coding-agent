from collections import defaultdict
from decimal import Decimal
from .fees import FeeEngine
from .fx import FxTable
from .ledger import TransactionLedger
from .money import money
from .models import SettlementLine, Transaction

class SettlementService:
    def __init__(self, fx: FxTable, fees: FeeEngine):
        self.fx = fx
        self.fees = fees

    def settle(self, transactions: list[Transaction], currency: str) -> list[SettlementLine]:
        ledger = TransactionLedger()
        gross = defaultdict(lambda: Decimal("0"))
        fees = defaultdict(lambda: Decimal("0"))

        for tx in transactions:
            if tx.status != "captured" or not ledger.accept(tx):
                continue
            converted = self.fx.convert(tx.amount, tx.currency, currency)
            if tx.kind == "refund":
                gross[tx.merchant_id] -= converted
            else:
                gross[tx.merchant_id] += converted
                fee_local = self.fees.fee_for(tx)
                fees[tx.merchant_id] += self.fx.convert(fee_local, tx.currency, currency)

        lines = []
        for merchant_id in sorted(gross):
            g = money(gross[merchant_id])
            f = money(fees[merchant_id])
            lines.append(SettlementLine(merchant_id, g, f, money(g - f), currency))
        return lines
