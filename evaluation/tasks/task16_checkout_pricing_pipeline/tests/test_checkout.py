from commerce.cart import Cart
from commerce.checkout import CheckoutService
from commerce.models import CartLine, Product


def make_cart(*lines):
    return Cart(list(lines))


def test_discount_applies_only_to_discountable_lines():
    regular = Product("book", 1000, taxable=True, discountable=True)
    gift_card = Product("gift", 2000, taxable=False, discountable=False)
    cart = make_cart(CartLine(regular, 2), CartLine(gift_card, 1))

    quote = CheckoutService().quote(
        cart,
        discount_percent=25,
        tax_rate_basis_points=0,
    )

    assert quote.subtotal_cents == 4000
    assert quote.discount_cents == 500
    assert quote.total_cents == 3500


def test_tax_is_computed_on_post_discount_taxable_amount():
    taxable = Product("desk", 10_000, taxable=True, discountable=True)
    cart = make_cart(CartLine(taxable, 1))

    quote = CheckoutService().quote(
        cart,
        discount_percent=20,
        tax_rate_basis_points=500,
    )

    assert quote.taxable_base_cents == 8000
    assert quote.tax_cents == 400
    assert quote.total_cents == 8400


def test_nontaxable_discounted_line_does_not_enter_tax_base():
    taxable = Product("lamp", 4000, taxable=True, discountable=True)
    nontaxable = Product("service", 3000, taxable=False, discountable=True)
    cart = make_cart(CartLine(taxable, 1), CartLine(nontaxable, 1))

    quote = CheckoutService().quote(
        cart,
        discount_percent=10,
        tax_rate_basis_points=1000,
        shipping_cents=500,
    )

    assert quote.discount_cents == 700
    assert quote.taxable_base_cents == 3600
    assert quote.tax_cents == 360
    assert quote.total_cents == 7160


def test_nondiscountable_taxable_line_remains_fully_taxable():
    sale = Product("sale", 2000, taxable=True, discountable=True)
    protected = Product("protected", 3000, taxable=True, discountable=False)
    cart = make_cart(CartLine(sale, 1), CartLine(protected, 1))

    quote = CheckoutService().quote(
        cart,
        discount_percent=50,
        tax_rate_basis_points=1000,
    )

    assert quote.discount_cents == 1000
    assert quote.taxable_base_cents == 4000
    assert quote.tax_cents == 400
    assert quote.total_cents == 4400
