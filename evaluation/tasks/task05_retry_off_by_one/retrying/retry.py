def run_with_retries(func, retries):
    last_error = None

    for _ in range(retries):
        try:
            return func()
        except Exception as exc:
            last_error = exc

    raise last_error
