from .matcher import path_matches

class PolicyEvaluator:
    def evaluate(self, roles, action: str, resource_path: str) -> bool:
        matched=[]
        for role in roles:
            for rule in role.rules:
                if rule.action in {action, "*"} and path_matches(rule.pattern, resource_path):
                    matched.append(rule.effect)
        # BUG: any allow wins, but explicit deny must override allow.
        if "allow" in matched:
            return True
        return False
