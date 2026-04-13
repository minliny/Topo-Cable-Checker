# Usage Pain Log

> 真实使用痛点记录。所有后续迭代优先级由本日志驱动，非拍脑袋。
> 项目阶段：L4 稳定期 — Usage-Driven Optimization Mode

---

## 评分规则

### Frequency（频率）

| 值 | 含义 |
|----|------|
| 1 | 首次遇到 / 极罕见 |
| 2 | 偶尔（月度） |
| 3 | 经常（每周） |
| 4 | 频繁（每次使用） |

### Severity（严重度）

| 值 | 含义 |
|----|------|
| 1 | 轻微不便，不影响结果 |
| 2 | 需要额外操作绕过，但不丢数据 |
| 3 | 阻断部分工作流，需要手动修复 |
| 4 | 数据丢失 / 结果不可信 / 核心流程不可用 |

### Workflow Blocking（工作流阻断）

| 值 | 含义 |
|----|------|
| 1 | 纯视觉/提示问题 |
| 2 | 需要多点几次鼠标 |
| 3 | 需要查阅文档或找人问 |
| 4 | 完全卡死，必须提 Bug |

---

## 痛点记录

### 1. 前端 UI 历史版本与回滚界面存在假数据 (Rejected - Misleading)
- **发现时间**: 2026-04-13
- **发现方式**: 代码审计与真实使用
- **描述**: `HistoryDetailView` 和 `RollbackConfirmView` 存在硬编码的 Mock 数据，未真实调用后端 API 获取历史版本元数据和 Diff 详情，导致用户在回滚前无法看到真实的影响范围。
- **影响**: 严重误导用户，导致回滚操作存在极高风险，用户不敢点击回滚。
- **评分**: Frequency: 3 | Severity: 4 | Blocking: 3 | Total: 10
- **状态**: **已拒绝 (Rejected - 语义反转)**
- **解决方案**: 
  - `HistoryDetailView` 已接入 `getVersionMeta` 真实 API。（PASS）
  - `RollbackConfirmView` 已接入 `getBaselineDiff` API 并渲染真实变更表格，**但是 Diff 方向传反了**，导致 UI 上显示 "Added" 的规则实际上在回滚时会被 "Removed"。这构成了更危险的误导，必须重新修复。（FAIL）

### 2. 底层规则执行器 (GroupConsistencyExecutor) 在缺失配置时崩溃 (Rejected - Silent Failure)
- **发现时间**: 2026-04-13
- **发现方式**: 测试覆盖率补充
- **描述**: 当 `parameter_key` 指向的 Profile 不存在且 Rule 参数中未直接提供 `group_key` 时，`getattr` 抛出 `TypeError` 导致整个检查任务崩溃。
- **影响**: 用户配置错误导致整个任务失败，缺乏容错。
- **评分**: Frequency: 2 | Severity: 3 | Blocking: 3 | Total: 8
- **状态**: **已拒绝 (Rejected - 掩盖错误)**
- **解决方案**: 之前在 `GroupConsistencyExecutor` 中增加了配置缺失校验并优雅返回空 issue 列表。**独立验收指出这是静默失败 (Silent Failure)**。配置缺失应作为明确的 Execution Error 暴露给用户，而不是返回 0 违规让用户误以为网络健康。必须重新修复。（FAIL）

### 3. 测试体系方法签名漂移与引用过时 (Resolved)
- **发现时间**: 2026-04-13
- **发现方式**: 全局跑测试
- **描述**: `CompiledRule` 已迁移至 `compiled_rule_schema.py` 且构造方式大变，导致 113 个底层测试全部崩溃。
- **影响**: 研发过程失去保护网，任何重构都变成盲飞。
- **评分**: Frequency: 4 | Severity: 4 | Blocking: 4 | Total: 12
- **状态**: **已解决 (Resolved)**
- **解决方案**: 编写自动化脚本批量重构了 `tests/` 目录下的所有 `CompiledRule` 实例化与 Executor 执行签名，测试覆盖率恢复 100% 绿。