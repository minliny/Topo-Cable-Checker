# Next Steps

1. **Phase RULE_ENGINE_RUNTIME_EXTERNALIZATION - Threshold First Complete**: The system has successfully externalized the `threshold` executor. `rule_engine_threshold` scope rules can now be loaded, compiled by `ThresholdRuleCompiler`, and executed by `CheckRunService` via `RuleEngineExternalRuleAssembler`.
2. **Phase RULE_ENGINE_RUNTIME_EXTERNALIZATION - GroupConsistency/Topology (Next Phase)**: Continue the externalization effort by targeting the `group_consistency` and `topology` executors.
3. **Rule Publish Workflow MVP**: Establish a minimal viable publish closed-loop for rule drafts. This includes:
   - Pre-publish `compile preview` + validate
   - `baseline` version generation
   - Publish summary and publish history
   - Laying the groundwork for `diff` and `rollback`
4. **Advanced Rule Logic**: The RuleEngine can be expanded to support complex boolean logic (AND/OR), custom python evaluators, or cross-sheet relational validations.
5. **AI Integration**: AI assisted drafting and rule generation.
6. **Performance Tuning**: As the dataset grows, Infrastructure persistence might need to be upgraded from local JSON files to a relational database like SQLite/PostgreSQL.
