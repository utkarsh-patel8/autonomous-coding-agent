class DecisionCache:
    def __init__(self):
        self._values = {}

    def _key(self, user_id: str, action: str, resource_path: str):
        # BUG: action is missing, so a read decision can leak into write.
        return (user_id, resource_path)

    def get(self, user_id, action, resource_path):
        return self._values.get(self._key(user_id, action, resource_path))

    def put(self, user_id, action, resource_path, value):
        self._values[self._key(user_id, action, resource_path)] = value
