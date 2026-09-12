def calculate_tax(amount_cents: int, rate_basis_points: int) -> int:
    if amount_cents < 0:
        raise ValueError("amount_cents must be non-negative")
    if rate_basis_points < 0:
        raise ValueError("rate_basis_points must be non-negative")
    return amount_cents * rate_basis_points // 10_000
