from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    sku: str
    unit_price_cents: int
    taxable: bool = True
    discountable: bool = True

    def __post_init__(self):
        if self.unit_price_cents < 0:
            raise ValueError("unit_price_cents must be non-negative")


@dataclass(frozen=True)
class CartLine:
    product: Product
    quantity: int

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")

    @property
    def subtotal_cents(self) -> int:
        return self.product.unit_price_cents * self.quantity
