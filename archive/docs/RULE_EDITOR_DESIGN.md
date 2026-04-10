# Rule Editor Design Document

## 1. 背景与目标
在完成规则治理平台（Governance）后，系统具备了规则查询与编译结果的透明化展示。为了进一步赋予领域专家和运维人员自主管理规则的能力，需要引入**规则编辑器（Rule Editor）**。
该编辑器旨在将系统从“只读治理平台”升级为“可编辑、可校验、可发布”的完整规则产品。它紧密依赖现有的 Compiler、Template Registry 和 Governance 模块，但在此基础上新增了草稿（Draft）管理和版本发布（Publish）机制，确保线上运行规则的稳定性和确定性。

## 2. 架构位置
Rule Editor 严格遵循五层架构设计：
- **Presentation (UI/Web)**: 负责提供编辑界面，响应用户交互，并调用 Application 层的 DTO 服务。**绝对禁止**直接解析 DSL、直接调用 RuleCompiler 或直接读写底层 Baseline Store。
- **Application (RuleEditorService)**: 协调 UI 请求，负责草稿数据的暂存、调用 Domain 层的 RuleCompiler 进行校验和预览、以及执行发布逻辑（版本升迁）。返回严格的 DTO 给 UI。
- **Domain (RuleCompiler / TemplateRegistry)**: 提供核心的规则编译与校验业务逻辑。编辑器功能完全复用现有 Compiler，保证“所见即所得”。
- **Infrastructure (BaselineRepository)**: 提供对规则集和基线数据的持久化支持。

## 3. 页面结构
规则编辑器 UI 采用经典的三栏布局：
1. **左栏：规则列表** - 列出当前基线（或草稿版本）下的所有规则，展示 `rule_id`、`source_form`、`enabled` 及当前草稿的 `compile_status`。
2. **中栏：规则编辑区** - 动态表单，根据 `source_form` 呈现 DSL 文本编辑器或 Template 参数表单，包含基础属性（severity、target_type 等）。
3. **右栏：编译结果 / 错误区** - 实时展示 `compile_preview` 返回的底层 `compiled_rule` JSON 结构，或在校验失败时显示具体的 `compile_errors`（类型及信息）。

## 4. 数据流
规则编辑的核心数据流向如下：
`rule_definition (UI Form)` → `validate / compile_preview (Application -> Domain)` → `UI Feedback` → `save_draft (Application -> Infra)` → `publish (Application -> Domain check -> Infra)`

## 5. 接口设计
- `validate`: 接收单条 rule_definition，调用 RuleCompiler，返回是否有错误。
- `compile_preview`: 接收单条 rule_definition，返回最终生成的 executor 配置结构。
- `save_draft`: 暂存规则修改到当前工作区，不变更基线版本，允许包含编译错误的规则被保存。
- `publish`: 检查工作区所有草稿，若全部 `compile_success`，则生成新的 `baseline_version`（原版本不可变）。若存在错误，拒绝发布。

## 6. DTO 设计
- `RuleEditorBaselineDTO`: 包含 `baseline_id`, `baseline_version`, `draft_rule_count`, `published_rule_count` 等。
- `RuleEditorDraftDTO`: 承载单条规则的编辑态数据，包含 `is_dirty`, `draft_status` 等。
- `RuleValidationResultDTO`: 包含 `is_valid` 和 `compile_errors` 列表。
- `RuleCompilePreviewDTO`: 包含 `compile_status`, `compiled_rule` 和 `compile_errors`。

## 7. 发布模型
- **Draft vs Published**: 用户所有的修改都在 Draft 区进行。
- **版本递增**: 当点击发布时，服务会校验所有的 Draft，通过后，创建一个全新的 Baseline 副本，并分配递增的 `baseline_version`（例如 v1.0 -> v1.1）。旧版本作为快照固化。
- **阻塞机制**: 只要 Draft 区存在一条无法通过 `RuleCompiler.compile` 的规则，`publish` 动作就会被拦截，保障线上基线永远合法。

## 8. 示例
- **DSL 规则编辑示例**:
  输入 DSL: `when: device_type == "Switch"`, `assert: status == "active"`。预览区实时输出 `executor: single_fact` 及 `scope_selector` 的底层配置。
- **Template 规则编辑示例**:
  选择 `group_consistency` 模板，输入 `group_key: device_type`。预览区输出编译后的模板参数映射。
