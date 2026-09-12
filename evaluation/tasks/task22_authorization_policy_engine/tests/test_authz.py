from authz.directory import RoleDirectory
from authz.models import Resource, Role, Rule, User
from authz.service import AuthorizationService

def setup_service():
    roles={
      'reader': Role('reader',(Rule('read','/projects/**','allow'),)),
      'writer': Role('writer',(Rule('write','/projects/*','allow'),)),
      'blocked': Role('blocked',(Rule('*','/projects/secret/**','deny'),)),
    }
    directory=RoleDirectory(roles, user_roles={'u1':('reader','blocked')}, group_roles={'eng':('writer',)})
    return AuthorizationService(directory)

def test_group_role_is_inherited():
    service=setup_service(); user=User('u2',frozenset({'eng'}))
    assert service.is_allowed(user,'write',Resource('/projects/p2'))

def test_explicit_deny_overrides_allow():
    service=setup_service(); user=User('u1')
    assert service.is_allowed(user,'read',Resource('/projects/public/a'))
    assert not service.is_allowed(user,'read',Resource('/projects/secret/a'))

def test_cache_is_scoped_by_action():
    service=setup_service(); user=User('u1'); resource=Resource('/projects/public/a')
    assert service.is_allowed(user,'read',resource)
    assert not service.is_allowed(user,'write',resource)

def test_unmatched_action_defaults_to_deny():
    service=setup_service(); user=User('u1')
    assert not service.is_allowed(user,'delete',Resource('/projects/public/a'))

def test_group_and_direct_roles_are_combined():
    roles={'r':Role('r',(Rule('read','/**','allow'),)),'w':Role('w',(Rule('write','/**','allow'),))}
    d=RoleDirectory(roles,user_roles={'u':('r',)},group_roles={'g':('w',)})
    s=AuthorizationService(d); u=User('u',frozenset({'g'}))
    assert s.is_allowed(u,'read',Resource('/x')) and s.is_allowed(u,'write',Resource('/x'))
