from dataclasses import dataclass
from .cart import Cart
from .promotions import percentage_discount
from .tax import calculate_tax


@dataclass(frozen=True)
class Quote:
    subtotal_cents: int
    discount_cents: int
    taxable_base_cents: int
    tax_cents: int
    shipping_cents: int
    total_cents: int


class CheckoutService:
    def quote(
        self,
        cart: Cart,
        *,
        discount_percent: int,
        tax_rate_basis_points: int,
        shipping_cents: int = 0,
    ) -> Quote:
        if shipping_cents < 0:
            raise ValueError("shipping_cents must be non-negative")

        subtotal = cart.subtotal_cents

        # A promotion only applies to lines marked discountable.
        # BUG: the implementation discounts the whole cart.
        discount = percentage_discount(subtotal, discount_percent)

        # Tax is charged only on taxable merchandise and after discounts.
        # BUG: discounts are not reflected in this base.
        taxable_base = sum(
            line.subtotal_cents
            for line in cart.lines
            if line.product.taxable
        )
        tax = calculate_tax(taxable_base, tax_rate_basis_points)

        total = subtotal - discount + tax + shipping_cents
        return Quote(
            subtotal_cents=subtotal,
            discount_cents=discount,
            taxable_base_cents=taxable_base,
            tax_cents=tax,
            shipping_cents=shipping_cents,
            total_cents=total,
        )
