import re

def rewrite_test_file(filename):
    with open(filename, "r") as f:
        content = f.read()

    # Import replacement
    content = content.replace(
        "from src.domain.rule_engine.compiled_rule import CompiledRule",
        "from src.domain.compiled_rule_schema import CompiledRule, RuleTarget, RuleMessage"
    )

    # 1. executor.execute fix
    content = re.sub(r'executor\.execute\("[^"]+",\s*compiled,', 'executor.execute(compiled,', content)

    # 2. regex replacement for return CompiledRule(...)
    def replace_compiled_rule(m):
        block = m.group(0)
        # extract rule_id, target_type, message template, severity
        # then rewrite it
        
        # We know we're in `_make_compiled_rule` which has variables: rule_id, target_type, severity, params
        # So we can just replace the entire block with the new format!
        
        # Determine which executor it is based on the file
        if "single_fact" in filename:
            exec_name = "single_fact"
            msg = "single_fact check"
        elif "threshold" in filename:
            exec_name = "threshold"
            msg = "threshold check"
        elif "group_consistency" in filename:
            exec_name = "group_consistency"
            msg = "consistency check"
        elif "topology" in filename:
            exec_name = "topology"
            msg = "topology check"
        else:
            exec_name = "unknown"
            msg = "check"
            
        new_str = f"""    return CompiledRule(
        rule_id=rule_id,
        rule_type="template",
        executor="{exec_name}",
        target=RuleTarget(type=target_type, filter=None),
        message=RuleMessage(template=f"Rule {{rule_id}} {msg}", severity=severity),
        params=params
    )"""
        return new_str

    content = re.sub(r'    return CompiledRule\([\s\S]*?\n    \)', replace_compiled_rule, content)

    if "test_topology_e2e.py" in filename:
        old_1 = re.search(r'        compiled = CompiledRule\([\s\S]*?rule_id="self_loop_check"[\s\S]*?\n        \)', content)
        if old_1:
            new_1 = """        compiled = CompiledRule(
            rule_id="self_loop_check",
            rule_type="template",
            executor="topology",
            target=RuleTarget(type="links", filter=None),
            message=RuleMessage(template="Self-loop detected", severity="critical"),
            params={"assertion_type": "self_loop"}
        )"""
            content = content.replace(old_1.group(0), new_1)
        
        old_2 = re.search(r'        compiled = CompiledRule\([\s\S]*?rule_id="isolated_check"[\s\S]*?\n        \)', content)
        if old_2:
            new_2 = """        compiled = CompiledRule(
            rule_id="isolated_check",
            rule_type="template",
            executor="topology",
            target=RuleTarget(type="devices", filter=None),
            message=RuleMessage(template="Isolated device detected", severity="high"),
            params={"assertion_type": "isolated_device"}
        )"""
            content = content.replace(old_2.group(0), new_2)

    with open(filename, "w") as f:
        f.write(content)

files = ["tests/test_single_fact_executor.py", "tests/test_threshold_executor.py", "tests/test_group_consistency_executor.py", "tests/test_topology_executor.py", "tests/test_topology_e2e.py"]
for f in files:
    rewrite_test_file(f)
