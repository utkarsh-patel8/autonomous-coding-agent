def chunk(items, size):
    if size <= 0:
        raise ValueError("size must be positive")

    return [
        items[i * size:(i + 1) * size]
        for i in range(len(items) // size)
    ]
