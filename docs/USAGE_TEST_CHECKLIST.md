# Usage Simulation Test Checklist

> 版本：1.0 | 创建：2026-04-12 | 配套文档：USAGE_SIMULATION_PLAN.md

---

## 使用说明

- 每个场景对应 `USAGE_SIMULATION_PLAN.md` 中的编号
- 数据集位于 `samples/usage_simulation/` 目录
- 执行者勾选 [ ] → [x] 并填写实际结果
- 任何失败需在备注中记录具体现象

---

## A. 单规则正确性验证

数据集：`dataset_A_single_rule.json`

| 编号 | 场景 | 期望结果 | 通过 | 实际结果 | 备注 |
|------|------|----------|------|----------|------|
| A-01 | Threshold gt/gte/lt/lte | 0 issue (全部 pass) | [ ] | | |
| A-02 | Threshold between/outside | between: 0 issue, outside: 1 issue | [ ] | | |
| A-03 | Threshold eq | 0 issue (5==5) | [ ] | | |
| A-04 | Threshold count vs distinct_count | 均为 0 issue | [ ] | | |
| A-05 | SingleFact field_equals | 1 issue (SW-02) | [ ] | | |
| A-06 | SingleFact regex_match | 2 issues (RT-01, FW-01) | [ ] | | |
| A-07 | SingleFact missing_value | 2 issues (null, empty) | [ ] | | |
| A-08 | GroupConsistency inconsistent | 1 issue (SW-03) | [ ] | | |
| A-09 | GroupConsistency all consistent | 0 issue | [ ] | | |
| A-10 | GroupConsistency single item | 0 issue (skip) | [ ] | | |

**A 类自动化测试覆盖**：`pytest tests/test_threshold_executor.py tests/test_single_fact_executor.py tests/test_group_consistency_executor.py -v`

---

## B. 多规则交互验证

数据集：`dataset_B_multi_rule.json`

| 编号 | 场景 | 期望结果 | 通过 | 实际结果 | 备注 |
|------|------|----------|------|----------|------|
| B-01 | 3 条 Threshold 并行 | 各自独立判定 | [ ] | | |
| B-02 | Threshold + SingleFact 混合 | 无交叉污染 | [ ] | | |
| B-03 | Threshold + GroupConsistency 混合 | 无交叉污染 | [ ] | | |
| B-04 | 3 种类型全混合 | 总计 2 issues | [ ] | | |
| B-05 | 重复 rule_id 冲突 | 后者覆盖前者 | [ ] | | |

**B 类验证方式**：手动构造多规则 baseline 并运行检查

---

## C. 边界与极端输入

数据集：`dataset_C_boundary.json`

| 编号 | 场景 | 期望结果 | 通过 | 实际结果 | 备注 |
|------|------|----------|------|----------|------|
| C-01 | 空数据集 (0 devices) | 1 issue (threshold fail) | [ ] | | |
| C-02 | 大数据集 (10000 devices) | 0 issue, <5s | [ ] | | |
| C-03 | None 字段值 | 安全处理不崩溃 | [ ] | | |
| C-04 | 空字符串字段值 | 区分 empty vs None | [ ] | | |
| C-05 | 缺失 threshold_key | 优雅降级 | [ ] | | |
| C-06 | 非法 metric_type | 默认 actual_value=0 | [ ] | | |
| C-07 | 不存在的 group_key 字段 | 按 None 分组 | [ ] | | |

**C 类验证方式**：手动构造 + 部分已覆盖于 executor 测试中

---

## D. Draft/Publish/Version 工作流压测

数据集：`dataset_D_workflow.json`

| 编号 | 场景 | 期望结果 | 通过 | 实际结果 | 备注 |
|------|------|----------|------|----------|------|
| D-01 | 连续 50 次 save draft | 全部成功，无数据损坏 | [ ] | | |
| D-02 | save↔publish 交替 20 轮 | 版本递增 v1.1~v1.20 | [ ] | | |
| D-03 | 10 次 rollback 不同版本 | rule_set 正确恢复 | [ ] | | |
| D-04 | 并发读写 draft | 无崩溃，最终一致 | [ ] | | |
| D-05 | publish 后 draft 自动清除 | has_draft=false | [ ] | | |

**D 类自动化测试覆盖**：`pytest tests/test_draft_save_api.py -v`

---

## E. API 端点压力测试

数据集：`dataset_E_api_stress.json`

| 编号 | 场景 | 期望结果 | 通过 | 实际结果 | 备注 |
|------|------|----------|------|----------|------|
| E-01 | 100 次 GET /baselines | 全 200, <100ms avg | [ ] | | |
| E-02 | 50 次 POST validate | 全 200, <200ms avg | [ ] | | |
| E-03 | 20 次 POST publish 串行 | 全成功, <300ms avg | [ ] | | |
| E-04 | validate+publish 混合 50 次 | 无 5xx, <400ms avg | [ ] | | |
| E-05 | diff+rollback 混合 40 次 | 无 5xx, <500ms avg | [ ] | | |

**E 类验证方式**：需要启动 API 服务后使用 ab/locust/脚本执行

---

## 总体结果汇总

| 类别 | 场景数 | 通过 | 失败 | 跳过 |
|------|--------|------|------|------|
| A | 10 | | | |
| B | 5 | | | |
| C | 7 | | | |
| D | 5 | | | |
| E | 5 | | | |
| **合计** | **32** | | | |

**签字**：___________  **日期**：___________
