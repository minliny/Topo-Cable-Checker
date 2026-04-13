import glob

def fix_context(filename):
    with open(filename, "r") as f:
        content = f.read()
    
    # replace ExecutionContext with dict
    content = content.replace("from src.domain.rule_engine.execution_context import ExecutionContext", "from typing import Dict, Any")
    
    if "test_threshold_executor.py" in filename:
        old_str = """def _make_context(threshold_profile=None, parameter_profile=None) -> ExecutionContext:
    return ExecutionContext(
        parameter_profile=parameter_profile or {},
        threshold_profile=threshold_profile or {},
        runtime_flags={},
    )"""
        new_str = """def _make_context(threshold_profile=None, parameter_profile=None) -> dict:
    return {
        "parameter_profile": parameter_profile or {},
        "threshold_profile": threshold_profile or {},
    }"""
        content = content.replace(old_str, new_str)
        
    if "test_group_consistency_executor.py" in filename:
        old_str = """def _make_context(parameter_profile=None) -> ExecutionContext:
    return ExecutionContext(
        parameter_profile=parameter_profile or {},
        threshold_profile={},
        runtime_flags={},
    )"""
        new_str = """def _make_context(parameter_profile=None) -> dict:
    return {
        "parameter_profile": parameter_profile or {},
        "threshold_profile": {},
    }"""
        content = content.replace(old_str, new_str)
        
    if "test_topology_executor.py" in filename:
        old_str = """def _make_context() -> ExecutionContext:
    return ExecutionContext(
        parameter_profile={},
        threshold_profile={},
        runtime_flags={},
    )"""
        new_str = """def _make_context() -> dict:
    return {
        "parameter_profile": {},
        "threshold_profile": {},
    }"""
        content = content.replace(old_str, new_str)
        
    if "test_single_fact_executor.py" in filename:
        old_str = """def _make_context() -> ExecutionContext:
    return ExecutionContext(
        parameter_profile={},
        threshold_profile={},
        runtime_flags={},
    )"""
        new_str = """def _make_context() -> dict:
    return {
        "parameter_profile": {},
        "threshold_profile": {},
    }"""
        content = content.replace(old_str, new_str)
        
    if "test_topology_e2e.py" in filename:
        content = content.replace("from src.domain.rule_engine.execution_context import ExecutionContext\n", "")
        old_str = "context = ExecutionContext(parameter_profile={}, threshold_profile={}, runtime_flags={})"
        new_str = 'context = {"parameter_profile": {}, "threshold_profile": {}}'
        content = content.replace(old_str, new_str)

    with open(filename, "w") as f:
        f.write(content)

for file in ["tests/test_single_fact_executor.py", "tests/test_threshold_executor.py", "tests/test_group_consistency_executor.py", "tests/test_topology_executor.py", "tests/test_topology_e2e.py"]:
    fix_context(file)
