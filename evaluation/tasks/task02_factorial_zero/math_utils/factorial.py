def factorial(n):
    if n < 0:
        raise ValueError("factorial is undefined for negative numbers")

    if n <= 1:
        return n

    return n * factorial(n - 1)
