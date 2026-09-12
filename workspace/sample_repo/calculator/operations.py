def add(a, b):
    """Return the sum of a and b."""
    return a + b


def subtract(a, b):
    """Return the difference of a and b (a minus b)."""
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    """Return the division of a by b.

    The original implementation used floor division (``//``) which
    truncated the result to an integer.  The tests expect true
    division, so we use the ``/`` operator instead.
    """
    return a / b


import re


def evaluate(equation: str):
    """Evaluate a simple arithmetic equation.

    The function accepts a string containing numbers and the four
    basic arithmetic operators (+, -, *, /).  It performs the
    calculation following the normal mathematical precedence rules
    (multiplication/division before addition/subtraction).  Only
    characters that are digits, whitespace, the four operators,
    decimal points and parentheses are allowed; any other
    character will raise a :class:`ValueError`.

    Parameters
    ----------
    equation: str
        The arithmetic expression to evaluate.

    Returns
    -------
    float
        The result of the calculation.
    """
    # Basic validation – allow digits, whitespace, operators, decimal
    # points and parentheses only.
    if not re.fullmatch(r"[\d\s+\-*/.()]+", equation):
        raise ValueError("Equation contains invalid characters")

    try:
        # ``eval`` is used with a restricted globals dictionary to
        # prevent access to built‑ins.  This keeps the evaluation
        # safe while still respecting operator precedence.
        result = eval(equation, {"__builtins__": None}, {})
    except ZeroDivisionError:
        # Propagate division‑by‑zero errors to the caller.
        raise
    except Exception as exc:
        # Any other exception (e.g. syntax errors) is wrapped in a
        # ValueError to provide a clear error message.
        raise ValueError("Invalid equation") from exc

    # Convert integer results to int type for consistency with tests.
    if isinstance(result, float) and result.is_integer():
        return int(result)
    return result
