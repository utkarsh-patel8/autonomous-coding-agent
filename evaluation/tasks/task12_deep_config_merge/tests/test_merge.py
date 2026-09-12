from config.merge import merge_config


def test_nested_values_are_preserved():
    base = {
        "database": {
            "host": "localhost",
            "port": 5432,
        },
        "debug": False,
    }

    override = {
        "database": {
            "port": 6432,
        }
    }

    assert merge_config(base, override) == {
        "database": {
            "host": "localhost",
            "port": 6432,
        },
        "debug": False,
    }


def test_scalar_override():
    assert merge_config(
        {"debug": False},
        {"debug": True},
    ) == {"debug": True}
