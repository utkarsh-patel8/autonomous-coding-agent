from decimal import Decimal
from settlement.models import Transaction
from settlement.reconciliation import Reconciler

def test_refunds_reduce_reconciled_captured_total():
    txs=[Transaction("1","m",Decimal("40"),"USD"), Transaction("2","m",Decimal("12"),"USD",kind="refund"), Transaction("3","m",Decimal("99"),"USD",status="failed")]
    assert Reconciler().captured_by_merchant(txs)["m"] == Decimal("28")
