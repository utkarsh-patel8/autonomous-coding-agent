import pytest

from serializer.encode import encode_value


def test_boolean_true():
    assert encode_value(True) == "true"


def test_boolean_false():
    assert encode_value(False) == "false"


def test_integer():
    assert encode_value(12) == "12"


def test_string():
    assert encode_value("agent") == '"agent"'


def test_unsupported_type():
    with pytest.raises(TypeError):
        encode_value(3.14)
