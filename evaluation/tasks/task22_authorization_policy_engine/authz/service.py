from .cache import DecisionCache
from .directory import RoleDirectory
from .evaluator import PolicyEvaluator
from .models import Resource, User

class AuthorizationService:
    def __init__(self, directory: RoleDirectory, evaluator=None, cache=None):
        self.directory=directory
        self.evaluator=evaluator or PolicyEvaluator()
        self.cache=cache or DecisionCache()

    def is_allowed(self, user: User, action: str, resource: Resource) -> bool:
        cached=self.cache.get(user.user_id, action, resource.path)
        if cached is not None:
            return cached
        roles=self.directory.roles_for(user)
        result=self.evaluator.evaluate(roles, action, resource.path)
        self.cache.put(user.user_id, action, resource.path, result)
        return result
