from decimal import Decimal
from .money import money

class FxTable:
    """Rates are expressed as units of quote currency per one unit of base."""
    def __init__(self, rates: dict[tuple[str, str], Decimal]):
        self.rates = dict(rates)

    def _direct(self, source: str, target: str):
        if source == target:
            return Decimal("1")
        if (source, target) in self.rates:
            return self.rates[(source, target)]
        if (target, source) in self.rates:
            return Decimal("1") / self.rates[(target, source)]
        return None

    def rate(self, source: str, target: str) -> Decimal:
        direct = self._direct(source, target)
        if direct is not None:
            return direct
        # Cross-currency conversion is routed through USD.
        to_usd = self._direct(source, "USD")
        from_usd = self._direct("USD", target)
        if to_usd is None or from_usd is None:
            raise KeyError(f"No FX route from {source} to {target}")
        # BUG: the second leg is divided instead of multiplied.
        return to_usd / from_usd

    def convert(self, amount: Decimal, source: str, target: str) -> Decimal:
        return money(amount * self.rate(source, target))
