def _parts(path: str) -> list[str]:
    return [p for p in path.strip("/").split("/") if p]

def path_matches(pattern: str, path: str) -> bool:
    """* matches one segment; ** matches zero or more trailing segments."""
    p = _parts(pattern)
    x = _parts(path)
    i = j = 0
    while i < len(p) and j < len(x):
        if p[i] == "**":
            # BUG: ** is treated like * and matches exactly one segment.
            i += 1; j += 1; continue
        if p[i] != "*" and p[i] != x[j]:
            return False
        i += 1; j += 1
    return i == len(p) and j == len(x)
