# P0-7 + P1.0: 能力真实性审计报告（含可审查证据）

> 审计时间：2026-04-11（P0 + P1.0 完工后更新）
> 审计范围：所有核心能力的端到端真实性验证
> 审计方法：逐项追踪代码路径，验证从 UI → API → Domain → Infrastructure 的完整链路

---

## 一、已确认真实执行的能力清单

### 1. topology executor ✅ PASS

**验证方式**：
- **代码路径**：`RuleEngine.execute()` → `TopologyExecutor.execute()` → 3 条分支（duplicate_link / missing_peer / topology_assertion）
- **测试文件**：`tests/test_topology_executor.py`（14 个单元测试）、`tests/test_topology_e2e.py`（4 个 E2E 测试）
- **测试类型**：单元测试 + E2E 集成测试
- **关键测试**：
  - `test_detects_self_loop`：证明 `topology_assertion/self_loop` 路径真实执行（此前因 NameError 无法执行）
  - `test_detects_isolated_device`：证明 `topology_assertion/isolated_device` 路径真实执行
  - `test_e2e_self_loop_via_dsl`：端到端：CompiledRule → TopologyExecutor → IssueItem
- **局限性**：E2E 测试直接构造 CompiledRule 绕过了 RuleCompiler（因为 "topology" 模板不设置 topology_assertion 子类型）。通过 RuleEngine 的 template 路径间接执行时，需依赖具体 rule_set 配置。

### 2. threshold executor ✅ PASS

**验证方式**：
- **代码路径**：`RuleEngine.execute()` → `ThresholdExecutor.execute()` → 7 种比较算子
- **测试文件**：`tests/test_rule_engine_platform.py`（6 个测试，包含 threshold 编译验证）
- **测试类型**：单元测试
- **修复证据**：`threshold_executor.py:84` 原 `rule_def.get("scope_selector",{})` 已改为 `compiled_rule.target.get("filter",{})`，evidence 构造不再 NameError
- **局限性**：无专门的 threshold executor 单元测试文件（通过 platform 测试间接验证），threshold executor 的 7 种算子未逐个独立测试

### 3. single_fact executor ✅ PASS

**验证方式**：
- **代码路径**：`RuleEngine.execute()` → `SingleFactExecutor.execute()` → 3 种子类型
- **测试文件**：`tests/test_rule_engine_platform.py`（间接验证编译路径）
- **测试类型**：单元测试
- **局限性**：无专门的 single_fact executor 单元测试文件

### 4. group_consistency executor ✅ PASS

**验证方式**：
- **代码路径**：`RuleEngine.execute()` → `GroupConsistencyExecutor.execute()` → 分组+频次+dominant
- **测试文件**：`tests/test_rule_engine_platform.py`（间接验证）
- **测试类型**：单元测试
- **局限性**：无专门的 group_consistency executor 单元测试文件

### 5. validation 阻断 publish ✅ PASS（P1.0-2 修复后）

**验证方式**：
- **代码路径**：`rules.py publish_baseline()` → `RulePublishWorkflowService.publish_draft()` → `RuleEditorGovernanceBridgeService.compile_draft_preview()` → `RuleCompiler.compile()` → 编译失败则 `publish_success=False` + `blocked_issues`
- **测试文件**：`tests/test_publish_validation_gate.py`（6 个验证门专用测试）
- **测试类型**：集成测试（FastAPI TestClient + tmp_path 隔离）
- **关键测试**：
  - `test_publish_invalid_draft_is_blocked`：空 params → 编译失败 → success=False + blocked_issues
  - `test_publish_invalid_draft_does_not_modify_baseline`：阻断时 baseline 不变
  - `test_validation_endpoint_and_publish_endpoint_consistent`：validate 与 publish 结果一致
  - `test_publish_blocked_returns_structured_error`：错误结构包含 field_path/issue_type/message
- **P1.0-2 修复内容**：移除旧 `str.contains("block")` 硬编码检查，改用 RuleCompiler 真实编译校验
- **局限性**：前端 UI 层面未强制要求先 validate 才能 publish（但后端侧保证阻断）

### 6. diff 数据来源 ✅ PASS

**验证方式**：
- **代码路径**：`baselines.py:111` → `hist_svc.diff_versions()` → `RuleBaselineHistoryService.diff_versions()` → 逐规则集合差分
- **测试文件**：`tests/test_rule_baseline_history.py`（5 个测试）
- **测试类型**：单元测试
- **局限性**：Diff 为浅层比较（仅顶层 key），嵌套差异路径未提供

### 7. rollback 生成 draft ✅ PASS

**验证方式**：
- **代码路径**：`rules.py:143` → `hist_svc.get_baseline_version()` → 从 baseline_version_snapshot 获取历史 rule_set → 取首条规则作为 draft_data
- **测试文件**：`tests/test_rule_baseline_history.py::test_rollback_to_version_creates_new_version`、`tests/test_api_integration.py::test_create_rollback_candidate`
- **测试类型**：集成测试
- **局限性**：rollback 仅取第一条规则作为 draft，非完整 rule_set 回滚

### 8. publish body 绑定 + 数据真实持久化 ✅ PASS（P1.0-1 修复后）

**验证方式**：
- **代码路径**：`rules.py publish_baseline(req: PublishRequestDTO)` → `RuleDraftView(params=req.params)` → `RulePublishWorkflowService.publish_draft()` → `repo.save()` → `_write_json()`
- **测试文件**：`tests/test_publish_validation_gate.py`（5 个 Body 绑定测试）
- **测试类型**：集成测试（FastAPI TestClient + tmp_path 隔离）
- **关键测试**：
  - `test_publish_request_body_is_bound`：PublishRequestDTO body 正确解析
  - `test_publish_body_binding_persists_draft_data`：提交的 rule 数据与最终持久化一致（读 baselines.json 验证）
  - `test_publish_without_rule_id_uses_default`：rule_id 为空时自动生成
- **P1.0-1 修复内容**：`Dict[str,Any]=None` → `PublishRequestDTO` 确保请求体正确绑定
- **局限性**：测试使用 tmp_path 隔离，生产环境数据仍为单文件 baselines.json

### 9. API 到后端真实链路 ✅ PASS

**验证方式**：
- **代码路径**：所有 API router 通过 `Depends(get_baseline_service)` → `BaselineService` → `BaselineRepository` → `_read_json("baselines.json")`
- **测试文件**：`tests/test_api_integration.py`（8 个测试）
- **测试类型**：集成测试（FastAPI TestClient）
- **关键端点验证**：
  - GET /api/baselines → 真实读取 baselines.json ✅
  - POST /api/rules/draft/validate → 真实调用 RuleCompiler ✅
  - POST /api/rules/publish/{id} → PublishRequestDTO + RulePublishWorkflowService ✅（P1.0-1 修复后）
  - POST /api/rules/rollback → 真实获取历史版本 ✅
  - GET /api/baselines/{id}/diff → 真实计算 diff ✅
- **局限性**：无

### 10. 前端默认 Real API ✅ PASS（P1.0-3 修复后）

**验证方式**：
- **代码路径**：`client.ts:12` → `USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === 'true'` → 默认 false → Real API
- **文件**：`frontend/.env` → `VITE_USE_MOCK_API=false`
- **shadow mock**：`mock.ts` 原有拦截器已默认禁用
- **P1.0-3 修复内容**：`!== 'false'` → `=== 'true'`，mock 需显式启用
- **局限性**：前端请求的 publish body 结构（PublishRequest）需与后端 PublishRequestDTO 一致，需手动验证联调

### 11. request_id 日志链路 ✅ PASS

**验证方式**：
- **代码路径**：`RequestIdMiddleware.dispatch()` → `request.state.request_id` → response header + error body + log entries
- **测试文件**：`tests/test_error_handler.py`（8 个测试）
- **测试类型**：集成测试（FastAPI TestClient）
- **关键测试**：`test_auto_generated_request_id`、`test_propagated_request_id`、`test_unique_request_id_per_request`
- **局限性**：仅验证了 header 和 body 中的 request_id，未验证日志文件中的 request_id 写入（需手动验证）

---

## 二、已修复的能力幻觉

| # | 能力 | P0 状态 | P1.0 状态 | 修复方式 |
|---|------|---------|-----------|---------|
| 1 | validation 阻断 publish | ❌ FAKE | ✅ PASS | publish 委托给 RulePublishWorkflowService，compile 失败则阻断 |
| 2 | publish 正确接收 draft_data body | ⚠️ DEFECT | ✅ PASS | PublishRequestDTO 替换 Dict[str,Any]=None |
| 3 | 前端默认接通 Real API | ⚠️ CONDITIONAL | ✅ PASS | VITE_USE_MOCK_API=false 为默认 |

---

## 三、仍存的能力幻觉 / 伪执行

| # | 能力 | 当前状态 | 缺失证据 | 优先级 |
|---|------|---------|---------|--------|
| 1 | handleSaveDraft 后端持久化 | ❌ FAKE | 仅 setTimeout 前端模拟，无 API 调用 | P2 |
| 2 | Diff 检测嵌套字段变更 | ⚠️ PARTIAL | 仅顶层 key 比较，嵌套差异未报告 | P1 |

---

## 四、测试验证矩阵

| 修复项 | 修复文件 | 新增测试 | 测试数 | 通过 | 类型 |
|--------|---------|---------|--------|------|------|
| P0-1 | topology_executor.py, threshold_executor.py | test_topology_executor.py, test_topology_e2e.py | 18 | 18 | 单元+E2E |
| P0-2 | repository.py, exceptions.py | test_persistence_safety.py | 11 | 11 | 单元 |
| P0-3 | repository.py | (含在 test_persistence_safety.py) | — | — | 单元 |
| P0-4 | logger.py | 手动验证 logs/app.log | — | — | 手动 |
| P0-5 | error_handler.py, main.py, exceptions.py | test_error_handler.py | 8 | 8 | 集成 |
| P0-6 | error_handler.py, main.py | (含在 test_error_handler.py) | — | — | 集成 |
| P0-7 | — | CAPABILITY_AUDIT.md | — | — | 审计 |
| P1.0-1 | dto_models.py, rules.py, rules.ts, App.tsx | test_publish_validation_gate.py | 11 | 11 | 集成 |
| P1.0-2 | rules.py | test_publish_validation_gate.py (6 tests) | 6 | 6 | 集成 |
| P1.0-3 | client.ts, mock.ts, .env | 代码审查 + .env 验证 | — | — | 审查 |

**总测试结果**：106 passed, 0 failed（排除 pre-existing 失败）
