from typing import List, Dict, Any, Optional, Tuple
from src.application.dto_models import RuleDefinitionDTO, CompiledRuleDTO, TemplateRegistryDTO, CompileErrorDTO
from src.domain.interfaces import IBaselineRepository
from src.domain.rule_compiler import RuleCompiler, RuleCompileError, TemplateRegistry

class RuleGovernanceService:
    def __init__(self, baseline_repo: IBaselineRepository = None):
        if baseline_repo is None:
            from src.infrastructure.repository import BaselineRepository
            self.repo = baseline_repo or BaselineRepository()
        else:
            self.repo = baseline_repo
        self._compiled_cache: Dict[str, Dict[str, Any]] = {}
        self._compile_errors: Dict[str, List[CompileErrorDTO]] = {}

    def _compile_baseline(self, baseline_id: str):
        if baseline_id in self._compiled_cache:
            return

        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            return

        compiled_rules = {}
        errors = []

        rule_set = getattr(baseline, "rule_set", baseline.get("rule_set", {})) if isinstance(baseline, dict) else baseline.rule_set

        for rule_id, rule_def in rule_set.items():
            try:
                compiled = RuleCompiler.compile(rule_id, rule_def)
                compiled_rules[rule_id] = compiled
            except RuleCompileError as e:
                errors.append(CompileErrorDTO(
                    rule_id=rule_id,
                    error_type=e.error_type,
                    message=e.message,
                    language_version=rule_def.get("language_version", "v1.0")
                ))

        self._compiled_cache[baseline_id] = compiled_rules
        self._compile_errors[baseline_id] = errors

    def list_rule_definitions(self, baseline_id: str) -> List[RuleDefinitionDTO]:
        baseline = self.repo.get_by_id(baseline_id)
        if not baseline:
            return []

        baseline_version = getattr(baseline, "baseline_version", baseline.get("baseline_version", "unknown")) if isinstance(baseline, dict) else baseline.baseline_version
        rule_set = getattr(baseline, "rule_set", baseline.get("rule_set", {})) if isinstance(baseline, dict) else baseline.rule_set

        dtos = []
        for rule_id, rule_def in rule_set.items():
            dtos.append(RuleDefinitionDTO(
                rule_id=rule_id,
                rule_type=rule_def.get("rule_type", "native"),
                language_version=rule_def.get("language_version", "v1.0"),
                target_type=rule_def.get("target_type", rule_def.get("scope_selector", {}).get("target_type", "devices")),
                source_form=rule_def.get("rule_type", "native"),
                severity=rule_def.get("severity", "medium"),
                enabled=rule_def.get("enabled", True),
                baseline_version=baseline_version,
                raw_definition=rule_def
            ))
        return dtos

    def get_rule_definition(self, baseline_id: str, rule_id: str) -> Optional[RuleDefinitionDTO]:
        rules = self.list_rule_definitions(baseline_id)
        for r in rules:
            if r.rule_id == rule_id:
                return r
        return None

    def get_compiled_rule(self, baseline_id: str, rule_id: str) -> Optional[CompiledRuleDTO]:
        self._compile_baseline(baseline_id)
        compiled = self._compiled_cache.get(baseline_id, {}).get(rule_id)
        if not compiled:
            return None

        # Determine parameter sources roughly based on executor keys (Governance view purpose)
        parameter_source = "inline"
        if "parameter_key" in compiled: parameter_source = "parameter_profile"
        threshold_source = "inline"
        if "threshold_key" in compiled: threshold_source = "threshold_profile"

        return CompiledRuleDTO(
            rule_id=rule_id,
            compiled_executor=compiled.get("executor", "unknown"),
            compiled_type=compiled.get("type", "unknown"),
            scope_selector=compiled.get("scope_selector", {}),
            parameter_source=parameter_source,
            threshold_source=threshold_source,
            compiled_config=compiled
        )

    def list_compile_errors(self, baseline_id: str) -> List[CompileErrorDTO]:
        self._compile_baseline(baseline_id)
        return self._compile_errors.get(baseline_id, [])

    def list_template_registry(self) -> List[TemplateRegistryDTO]:
        dtos = []
        for t_name, t_info in TemplateRegistry._templates.items():
            dtos.append(TemplateRegistryDTO(
                template_name=t_name,
                target_executor=t_info["target_executor"],
                supported_params=t_info["supported_params"],
                validation_rules=["(Callable validation rule)"] # Abstracted for DTO
            ))
        return dtos

    def validate_rule_definition(self, rule_def: Dict[str, Any]) -> Tuple[bool, Optional[CompileErrorDTO]]:
        try:
            RuleCompiler.compile("validation_test", rule_def)
            return True, None
        except RuleCompileError as e:
            return False, CompileErrorDTO(
                rule_id="validation_test",
                error_type=e.error_type,
                message=e.message,
                language_version=rule_def.get("language_version", "v1.0")
            )
