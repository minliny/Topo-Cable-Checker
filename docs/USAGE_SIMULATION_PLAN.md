# Usage Simulation & Stress Testing Plan

> 版本：1.0 | 创建：2026-04-12 | 状态：Active

---

## 1. 目的

通过构造仿真数据集和测试场景，验证 Topo-Cable-Checker 规则引擎在以下维度的健壮性：

- **正确性**：规则执行器在不同输入下的判定逻辑是否正确
- **边界性**：极端/边界值是否被正确处理
- **并发性**：多规则同时运行时是否有状态污染
- **数据完整性**：大规模数据下的持久化与恢复
- **API 压力**：高频 API 调用下的稳定性和响应时间

---

## 2. 场景分类

### A. 单规则正确性验证（Single Rule Correctness）

**目标**：验证每个 Executor 子类型在各种参数组合下的判定结果

| 编号 | 场景 | Executor | 覆盖点 |
|------|------|----------|--------|
| A-01 | gt/gte/lt/lte 四则比较 | Threshold | 全算子覆盖 |
| A-02 | between/outside 区间判断 | Threshold | 双边界 |
| A-03 | eq 等值判断 | Threshold | 精确匹配 |
| A-04 | count vs distinct_count | Threshold | 两种 metric_type |
| A-05 | field_equals 正/反例 | SingleFact | 等值校验 |
| A-06 | regex_match 正/反例 | SingleFact | 正则匹配 |
| A-07 | missing_value 检测 | SingleFact | 空值/None |
| A-08 | dominant value 一致性 | GroupConsistency | 多组不一致 |
| A-09 | 单组全部一致 | GroupConsistency | 无 issue |
| A-10 | 单组仅 1 条 | GroupConsistency | 跳过 |

**数据集**：`samples/usage_simulation/dataset_A_single_rule.json`

### B. 多规则交互验证（Multi-Rule Interaction）

**目标**：验证多条规则同时执行时是否存在状态污染或交叉影响

| 编号 | 场景 | 覆盖点 |
|------|------|--------|
| B-01 | 3 条 Threshold 规则并行 | 不同 operator + 不同 target |
| B-02 | Threshold + SingleFact 混合 | 跨类型无污染 |
| B-03 | Threshold + GroupConsistency 混合 | 跨类型无污染 |
| B-04 | 3 种类型各 1 条 | 全类型混合 |
| B-05 | 重复 rule_id 不同 rule_type | ID 冲突处理 |

**数据集**：`samples/usage_simulation/dataset_B_multi_rule.json`

### C. 边界与极端输入（Boundary & Extreme Input）

**目标**：验证系统在极端数据下的行为

| 编号 | 场景 | 覆盖点 |
|------|------|--------|
| C-01 | 0 条设备数据 | 空数据集 |
| C-02 | 10000 条设备数据 | 大数据集 |
| C-03 | 字段值为 None | None 安全 |
| C-04 | 字段值为空字符串 | 空串 vs None |
| C-05 | threshold_key 指向不存在的 T 定义 | 缺失配置降级 |
| C-06 | metric_type 为非法值 | 未知 metric_type |
| C-07 | group_key 字段在数据中不存在 | 属性缺失 |

**数据集**：`samples/usage_simulation/dataset_C_boundary.json`

### D. Draft/Publish/Version 工作流压测（Workflow Stress）

**目标**：验证高频 draft-save + publish + rollback 的稳定性

| 编号 | 场景 | 覆盖点 |
|------|------|--------|
| D-01 | 连续 50 次 save draft | 持久化吞吐 |
| D-02 | save → publish → save → publish 交替 20 轮 | 状态切换 |
| D-03 | 连续 10 次 rollback 到不同版本 | 版本恢复 |
| D-04 | draft save 期间读取 draft | 并发读写 |
| D-05 | publish 后 draft 自动清除验证 | A1-7 逻辑 |

**数据集**：`samples/usage_simulation/dataset_D_workflow.json`

### E. API 端点压力测试（API Stress）

**目标**：验证 REST API 在高频调用下的稳定性

| 编号 | 场景 | 覆盖点 |
|------|------|--------|
| E-01 | 100 次 GET /baselines | 只读吞吐 |
| E-02 | 50 次 POST /rules/draft/validate | 校验吞吐 |
| E-03 | 20 次 POST /rules/publish 串行 | 发布吞吐 |
| E-04 | validate + publish 混合 50 次 | 混合负载 |
| E-05 | 30 次 GET diff + 10 次 rollback | 查询+写入混合 |

**数据集**：`samples/usage_simulation/dataset_E_api_stress.json`

---

## 3. 执行方式

### 3.1 自动化测试（A/B/C 类）

```bash
# 单规则 + 多规则 + 边界 测试
pytest tests/test_threshold_executor.py tests/test_single_fact_executor.py \
       tests/test_group_consistency_executor.py tests/test_deep_diff.py \
       tests/test_rollback_completeness.py -v
```

### 3.2 半自动化工作流测试（D 类）

使用 `dataset_D_workflow.json` 中的参数，通过 pytest + FastAPI TestClient 执行：

```bash
pytest tests/test_draft_save_api.py -v
```

### 3.3 API 压力测试（E 类）

使用 locust 或 ab（Apache Benchmark）执行，参考 `dataset_E_api_stress.json` 配置：

```bash
# 示例：使用 ab 对 validate 端点压测
ab -n 50 -c 5 -p dataset_E_api_stress.json -T application/json \
   http://localhost:8000/api/rules/draft/validate
```

---

## 4. 验收标准

| 维度 | 标准 |
|------|------|
| 正确性 | A 类所有场景的期望 issue 数、category、severity 全部匹配 |
| 交互性 | B 类所有场景无状态污染，各规则独立判定 |
| 边界性 | C 类所有场景不崩溃，返回合理结果或空 issue 列表 |
| 工作流 | D 类所有场景 draft 持久化/清除/恢复正确 |
| API 压力 | E 类所有场景无 5xx 错误，平均响应 < 500ms |

---

## 5. 与现有测试的关系

| 现有测试 | 对应 SIM 场景 |
|----------|---------------|
| `test_threshold_executor.py` | A-01 ~ A-04 |
| `test_single_fact_executor.py` | A-05 ~ A-07 |
| `test_group_consistency_executor.py` | A-08 ~ A-10 |
| `test_deep_diff.py` | B-04 (部分) |
| `test_rollback_completeness.py` | D-03 (部分) |
| `test_draft_save_api.py` | D-01, D-04, D-05 |

SIM 数据集作为**补充**，提供手动/半自动测试的标准化输入，不替代自动化测试。
