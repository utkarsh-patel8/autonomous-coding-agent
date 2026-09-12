from calculator.operations import (
    add,
    subtract,
    multiply,
    divide,
    evaluate,
)


def test_add():
    assert add(2, 3) == 5


def test_subtract():
    assert subtract(5, 3) == 2


def test_multiply():
    assert multiply(4, 3) == 12


def test_divide():
    assert divide(10, 2) == 5
    assert divide(5, 2) == 2.5


def test_divide_by_zero():
    try:
        divide(10, 0)
    except ZeroDivisionError:
        pass
    else:
        assert False, "Expected ZeroDivisionError"


# New tests for evaluate function

def test_evaluate_simple():
    assert evaluate("2+3") == 5
    assert evaluate("10-4") == 6
    assert evaluate("5*6") == 30
    assert evaluate("8/2") == 4


def test_evaluate_precedence():
    # multiplication before addition
    assert evaluate("2+3*4") == 14
    # division before subtraction
    assert evaluate("10-6/2") == 7


def test_evaluate_parentheses():
    assert evaluate("(2+3)*4") == 20
    assert evaluate("2*(3+4)") == 14
    assert evaluate("(1+2)*(3+4)") == 21


def test_evaluate_decimal_and_whitespace():
    assert evaluate("3.5 + 2.1") == 5.6
    assert evaluate("  2 + 3  ") == 5


def test_evaluate_invalid_characters():
    # Contains letter 'a'
    try:
        evaluate("2+3a")
    except ValueError:
        pass
    else:
        assert False, "Expected ValueError for invalid characters"


def test_evaluate_division_by_zero():
    try:
        evaluate("10/0")
    except ZeroDivisionError:
        pass
    else:
        assert False, "Expected ZeroDivisionError for division by zero"


def test_evaluate_invalid_syntax():
    # Invalid syntax: multiplication operator without left operand
    try:
        evaluate("2+*3")
    except ValueError:
        pass
    else:
        assert False, "Expected ValueError for invalid syntax"


def test_evaluate_empty_string():
    try:
        evaluate("")
    except ValueError:
        pass
    else:
        assert False, "Expected ValueError for empty string"
