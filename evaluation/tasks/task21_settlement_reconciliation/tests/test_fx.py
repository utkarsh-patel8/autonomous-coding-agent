from decimal import Decimal
from settlement.fx import FxTable

def test_cross_currency_route_multiplies_both_legs():
    fx = FxTable({("EUR", "USD"): Decimal("1.20"), ("USD", "INR"): Decimal("80")})
    assert fx.rate("EUR", "INR") == Decimal("96.00")
    assert fx.convert(Decimal("10"), "EUR", "INR") == Decimal("960.00")

def test_inverse_rate_is_supported():
    fx = FxTable({("EUR", "USD"): Decimal("1.25")})
    assert fx.convert(Decimal("10"), "USD", "EUR") == Decimal("8.00")
