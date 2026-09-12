def sort_users(users):
    return sorted(
        users,
        key=lambda user: (user["age"], user["name"]),
        reverse=True,
    )
