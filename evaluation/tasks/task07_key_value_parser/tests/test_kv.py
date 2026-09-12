from parser.kv import parse_config


def test_basic_pairs():
    assert parse_config("host=localhost\nport=8080") == {
        "host": "localhost",
        "port": "8080",
    }


def test_blank_lines_and_whitespace():
    text = " host = localhost \n\n port= 8080 \n"
    assert parse_config(text) == {
        "host": "localhost",
        "port": "8080",
    }
