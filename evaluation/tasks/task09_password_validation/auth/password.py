def is_valid_password(password):
    too_short = len(password) < 8
    missing_digit = not any(ch.isdigit() for ch in password)
    missing_upper = not any(ch.isupper() for ch in password)

    if too_short and missing_digit and missing_upper:
        return False

    return True
