# Iteration Review

> 每轮迭代的审视记录。周期建议：weekly 或 biweekly。
> 项目阶段：L4 稳定期 — Pain Log 驱动迭代

---

## 迭代审视模板

复制以下模板，填入当轮数据：

```markdown
## Iteration YYYY-WXX / YYYY-MM-DD

### 本周期使用概况
- 使用频次：_N 次_
- 使用场景：_简述本周用工具做了什么_
- 核心操作路径：_编辑→校验→发布 / Diff / 回滚 / 执行 等_

### 新发现 Pain
| Pain ID | 一句话描述 | Pain Score | 优先级 |
|---------|-----------|------------|--------|
| _PAIN-XXX_ | _..._ | _N_ | _Critical/High/Medium/Low_ |

### Pain 合并/去重
- _PAIN-XXX 与 PAIN-YYY 合并为 PAIN-XXX，因为..._
- _PAIN-XXX 关闭，因为..._

### Top Priority This Cycle
1. **PAIN-XXX**：_一句话目标_
2. **PAIN-YYY**：_一句话目标_

### Deferred Items
| Pain ID | 原因 |
|---------|------|
| _PAIN-XXX_ | _暂缓原因_ |

### 本轮优化目标
- [ ] _PAIN-XXX：具体可交付结果_
- [ ] _PAIN-YYY：具体可交付结果_

### 完成结果
| 目标 | 状态 | 产出 |
|------|------|------|
| _PAIN-XXX_ | Done / Partial / Skipped | _文件/测试/验证_ |

### 下一轮验证点
- _使用 PAIN-XXX 修复后的功能，确认 Pain 是否消除_
- _...
```

---

## 示例迭代记录

## Iteration 2026-W15 / 2026-04-12

### 本周期使用概况
- 使用频次：3 次
- 使用场景：编辑 threshold 规则、发布新版本、从 v1.1 回滚到 v1.0
- 核心操作路径：编辑→校验→发布 / Diff / 回滚

### 新发现 Pain
| Pain ID | 一句话描述 | Pain Score | 优先级 |
|---------|-----------|------------|--------|
| PAIN-001 | RuleEditor JSON 手工编辑易出错 | 26 | High |
| PAIN-002 | 回滚候选只展示第一条规则 | 30 | Critical |

### Pain 合并/去重
- 无合并

### Top Priority This Cycle
1. **PAIN-002**：前端展示回滚候选完整 rule_set
2. **PAIN-001**：调查 Monaco Editor 集成可行性

### Deferred Items
| Pain ID | 原因 |
|---------|------|
| — | 首轮，暂无 Deferred |

### 本轮优化目标
- [ ] PAIN-002：RollbackConfirmView 展示完整规则列表
- [ ] PAIN-001：Monaco Editor 技术方案调研

### 完成结果
| 目标 | 状态 | 产出 |
|------|------|------|
| PAIN-002 | — | 本轮为初始化，尚未开始 |
| PAIN-001 | — | 本轮为初始化，尚未开始 |

### 下一轮验证点
- 回滚确认页是否能展示完整规则列表
- 编辑体验是否有改善

---

## Iteration 2026-W16 / 2026-04-14

### 本周期使用概况
- 使用场景：回滚确认语义验收 + executor 配置错误可观测性验收

### Pain 合并/去重
- PAIN-003 关闭：Rollback 预览 Diff 方向已修复为“Current Production → Target Historical”

### Top Priority This Cycle
1. **PAIN-003**：Rollback Preview Diff 方向修复
2. **RISK-008**：GroupConsistencyExecutor 缺配置不允许静默 false negative

### 本轮优化目标
- [x] PAIN-003：新增 rollback-effect-diff 专用 API，RollbackConfirmView 使用 rollback_effect_diff 展示真实 rollback effect
- [x] RISK-008：缺失 group_consistency 必要配置时返回 execution_error issue，不得 silent no-op

### 完成结果
| 目标 | 状态 | 产出 |
|------|------|------|
| PAIN-003 | Done | `GET /api/baselines/{id}/rollback-effect-diff` + `tests/test_diff_governance.py` + `frontend/src/__tests__/rollbackEffectDiffAdapter.test.ts` |
| RISK-008 | Done | `src/domain/executors/group_consistency_executor.py` + `tests/test_group_consistency_executor.py` |

### 下一轮验证点
- RollbackConfirmView 中 Added/Removed/Modified 是否与真实 rollback effect 一致（含 Modified before/after）
- group_consistency 缺配置时 UI/结果是否能明确看到 execution_error
