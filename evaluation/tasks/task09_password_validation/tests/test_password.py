from auth.password import is_valid_password


def test_valid_password():
    assert is_valid_password("Agent123") is True


def test_too_short():
    assert is_valid_password("Abc123") is False


def test_missing_digit():
    assert is_valid_password("AgentPass") is False


def test_missing_uppercase():
    assert is_valid_password("agent123") is False
