from decimal import Decimal
from settlement.fees import FeeEngine, FeePolicy
from settlement.fx import FxTable
from settlement.models import Transaction
from settlement.service import SettlementService

D=Decimal

def make_service():
    fx = FxTable({("EUR", "USD"): D("1.20"), ("USD", "INR"): D("80")})
    fees = FeeEngine({"m1": FeePolicy(D("0.02"), D("0.30")), "m2": FeePolicy(D("0.01"), D("0.10"))})
    return SettlementService(fx, fees)

def test_percentage_and_fixed_fee_are_charged_once():
    line = make_service().settle([Transaction("t1","m1",D("100"),"USD")], "USD")[0]
    assert line.gross == D("100.00")
    assert line.fees == D("2.30")
    assert line.net == D("97.70")

def test_duplicate_transaction_is_idempotent():
    tx = Transaction("same","m1",D("50"),"USD")
    line = make_service().settle([tx, tx], "USD")[0]
    assert line.gross == D("50.00")
    assert line.fees == D("1.30")

def test_refund_reduces_gross_and_does_not_add_fee():
    txs=[Transaction("s","m1",D("100"),"USD"), Transaction("r","m1",D("25"),"USD",kind="refund")]
    line=make_service().settle(txs,"USD")[0]
    assert (line.gross,line.fees,line.net)==(D("75.00"),D("2.30"),D("72.70"))

def test_settlement_converts_gross_and_fee_to_target_currency():
    line=make_service().settle([Transaction("e1","m1",D("10"),"EUR")],"INR")[0]
    assert line.gross == D("960.00")
    assert line.fees == D("48.00")  # EUR 0.50 * 96
    assert line.net == D("912.00")

def test_non_captured_transactions_are_ignored():
    txs=[Transaction("p","m1",D("100"),"USD",status="pending"), Transaction("c","m1",D("20"),"USD")]
    line=make_service().settle(txs,"USD")[0]
    assert line.gross == D("20.00")
