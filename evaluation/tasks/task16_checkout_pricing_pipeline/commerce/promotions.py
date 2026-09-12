def percentage_discount(amount_cents: int, percent: int) -> int:
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    if amount_cents < 0:
        raise ValueError("amount_cents must be non-negative")
    return amount_cents * percent // 100
