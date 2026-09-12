from users.sort import sort_users


def test_sort_by_age_then_name():
    users = [
        {"name": "Cara", "age": 30},
        {"name": "Bob", "age": 20},
        {"name": "Alice", "age": 20},
    ]

    assert sort_users(users) == [
        {"name": "Alice", "age": 20},
        {"name": "Bob", "age": 20},
        {"name": "Cara", "age": 30},
    ]
