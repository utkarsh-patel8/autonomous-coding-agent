def encode_value(value):
    if isinstance(value, int):
        return str(value)

    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, str):
        return f'"{value}"'

    raise TypeError("unsupported value")
