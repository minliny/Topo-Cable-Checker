__all__ = ["RuleEngine", "rule_engine"]


def __getattr__(name: str):
    if name in ("RuleEngine", "rule_engine"):
        from .engine import RuleEngine, rule_engine
        return RuleEngine if name == "RuleEngine" else rule_engine
    raise AttributeError(name)
