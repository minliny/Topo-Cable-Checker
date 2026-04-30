# TopoChecker 前台原型冻结说明

## 冻结状态

```
READY_CANDIDATE_FRONTEND_PROTOTYPE_COMPLETE
```

文件：`TopoChecker 完整前台.html`

---

## 页面覆盖范围

| 页面 | 导航路径 | 说明 |
|---|---|---|
| A 基线详情页 | 规则基线 → 基线详情 | ParameterProfile / ThresholdProfile / ScopeSelector / RuleSet / 版本快照摘要 |
| B 规则编辑页 | 规则基线 → 规则编辑 | RuleSet 分组 / Profile 引用 / rule_overrides / 类型化输入 / 规则级 ScopeSelector |
| C 版本管理页 | 规则基线 → 版本管理 | 结构化变更记录 / 快照查看 / 版本间 diff / 回滚状态反馈 |
| D 执行配置页 | 检查执行 → 执行配置 | 5 步识别确认流程 / DataSource / ExecutionScope / Profile 快照 |
| 运行历史页 | 检查执行 → 运行历史 | CheckResultBundle 列表 |
| F 分析工作台 | 结果分析 → 分析工作台 | 只消费 CheckResultBundle / drilldown context |
| E 差异对比页 | 复检差异 → 差异对比 | RecheckDiffSnapshot / RecheckIssueDiffItem / Workbench 下钻 |

---

## P0/P1/P2 完成清单

### P0：执行与 Diff 边界修复

- [x] D 页必须完成识别确认（recognition_status=confirmed）才允许开始检查
- [x] D 页数据来源绑定 DataSource 模型，执行范围绑定 ExecutionScope 模型
- [x] E 页 diff 完全来自 RecheckDiffSnapshot，禁止 UI 集合差计算
- [x] E 页 diff_summary 基于当前选定 Run A → Run B 配对

### P1：模型绑定完成

- [x] A 页 ParameterProfile 卡片（profile_id / parameters）
- [x] A 页 ThresholdProfile 卡片（profile_id / thresholds）
- [x] A 页 ScopeSelector 展示（scope_id / method / scope_fields）
- [x] A 页 RuleSet 分组摘要
- [x] A 页版本快照摘要（rule_added/removed/param/threshold changed）
- [x] B 页规则按 RuleSet 分组
- [x] B 页 ParameterProfile 引用 + rule_overrides（不污染 Profile 默认值）
- [x] B 页 ThresholdProfile 只读展示
- [x] B 页规则级 ScopeSelector 只读展示
- [x] B 页参数输入类型化（number/boolean/enum/string）
- [x] D 页 ParameterProfile / ThresholdProfile 快照摘要
- [x] E 页 RecheckIssueDiffItem 详情面板（可点击 issue 行展开）
- [x] Workbench 支持 diff 来源下钻上下文 banner + 自动选中 issue + 明确空态

### P2：版本治理结构化

- [x] C 页 VERSION_CHANGE_SUMMARIES（替代 changes 自由文本）
- [x] C 页 VERSION_SNAPSHOTS（完整版本快照查看）
- [x] C 页 VERSION_DIFF_SNAPSHOTS（版本间 RuleSet diff，禁止 UI 集合差）
- [x] C 页结构化变更徽章展示（新增N/删除M/修改K/参数/阈值/范围）
- [x] C 页变更明细折叠（change_items）
- [x] C 页回滚按钮状态反馈

---

## 明确禁止回退项

| 禁止项 | 原因 |
|---|---|
| D 页跳过识别确认直接执行 | 业务流要求：识别确认后才允许提交执行 |
| E 页 UI 集合差计算 diff（idsA/idsB/filter） | diff 必须来自 RecheckDiffSnapshot |
| C 页 `changes` 自由文本替代 VersionChangeSummary | 版本变更必须结构化，可被审计和测试绑定 |
| E 页 `ra.diff_summary` 取 Run A 内置值 | diff_summary 必须基于 A→B 配对 snapshot |
| Workbench 增加基线编辑入口 | Workbench 只消费 CheckResultBundle |
| Workbench 增加规则编辑入口 | 同上 |
| Workbench 增加版本管理入口 | 同上 |
| Workbench 增加执行配置入口 | 同上 |
| 引入 AI/LLM/API 运行时依赖 | 离线工具，不允许云端依赖 |
| 散落硬编码字符串（"本地快照（离线）""全量（DC-A / DC-B）""~30s"） | 所有来源/范围必须绑定结构化模型字段 |

---

## 模型边界说明

```
UI 只展示结构化模型结果，不推导业务结果

diff 来源：
  RuleSet/Rule diff       → VersionDiffSnapshot
  Run 级 diff 摘要        → RecheckDiffSnapshot.summary
  Issue 级 diff           → RecheckDiffSnapshot.issue_changes[]

参数来源：                → ParameterProfile.parameters[]
阈值来源：                → ThresholdProfile.thresholds[]
作用范围来源：            → ScopeSelector
规则组织：                → RuleSet.rule_ids[]

执行识别结果：            → RecognitionResult（API mock）
数据来源：                → DataSource
执行范围：                → ExecutionScope
```

---

## 关键常量索引（TopoChecker 完整前台.html）

| 常量名 | 用途 |
|---|---|
| `PARAMETER_PROFILES` | 参数 Profile |
| `THRESHOLD_PROFILES` | 阈值 Profile |
| `SCOPE_SELECTORS` | 范围选择器 |
| `RULE_SETS` | 规则集分组 |
| `BASELINE_PROFILE_MAP` | baseline_id → profile 引用 |
| `RULE_PROFILE_MAP` | rule_id → profile 引用 |
| `DATA_SOURCES` | 数据来源 |
| `EXECUTION_SCOPES` | 执行范围 |
| `RECOGNITION_RESULTS` | 识别结果 mock |
| `RECHECK_DIFF_SNAPSHOTS` | Run 级 diff 快照 |
| `VERSION_CHANGE_SUMMARIES` | 版本变更摘要 |
| `VERSION_SNAPSHOTS` | 版本完整快照 |
| `VERSION_DIFF_SNAPSHOTS` | 版本间 diff |
| `BASELINE_VERSION_SNAPSHOTS` | A 页版本快照摘要（轻量） |
