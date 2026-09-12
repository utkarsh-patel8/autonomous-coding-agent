from .models import Role, User

class RoleDirectory:
    def __init__(self, roles: dict[str, Role], user_roles=None, group_roles=None):
        self.roles = roles
        self.user_roles = user_roles or {}
        self.group_roles = group_roles or {}

    def roles_for(self, user: User) -> list[Role]:
        names = set(self.user_roles.get(user.user_id, ()))
        # BUG: group-based assignments are not included.
        return [self.roles[name] for name in sorted(names)]
