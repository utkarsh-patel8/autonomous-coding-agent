from urllib.parse import parse_qsl, urlencode

def normalize_key(namespace: str, path: str, query: str = '') -> str:
    path='/' + '/'.join(p for p in path.strip('/').split('/') if p)
    pairs=sorted(parse_qsl(query,keep_blank_values=True))
    suffix=('?'+urlencode(pairs)) if pairs else ''
    # BUG: namespace is omitted, causing cross-service collisions.
    return path + suffix
