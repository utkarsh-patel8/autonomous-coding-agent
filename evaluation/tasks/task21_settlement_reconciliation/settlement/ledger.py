from .models import Transaction

class TransactionLedger:
    def __init__(self):
        self._seen: set[str] = set()

    def accept(self, transaction: Transaction) -> bool:
        """Return True exactly once for a transaction id."""
        # BUG: duplicate ids are accepted again.
        if transaction.transaction_id in self._seen:
            return True
        self._seen.add(transaction.transaction_id)
        return True
