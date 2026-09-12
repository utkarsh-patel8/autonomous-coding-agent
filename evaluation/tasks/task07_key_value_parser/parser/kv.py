def parse_config(text):
    result = {}

    for line in text.splitlines():
        key, value = line.split("=", 1)
        result[key] = value

    return result
