# Project Status — AI Handoff

> **审计时间**：2026-04-11  
> **审计方法**：基于本地文件实际内容，逐文件读取，证据绑定  
> **审计基准**：不引用设计文档承诺，不将 TODO 视为已实现

---

## 1. 项目一句话定位

**Topo-Cable-Checker = 规则治理工作台（Rule Governance Workbench）**

用于编辑、校验、版本化、Diff、发布和回滚拓扑线缆校验规则的个人开发者工具。

**当前成熟度：L4-（稳固）** — 核心能力真实有效 + 主链路闭环 + 数据安全 + 可观测 + 2 项伪实现待修复

---

## 2. 项目健康度总览

| 维度 | 评级 | 说明 |
|------|------|------|
| 主链路完整性 | L4 | Draft→Validate→Publish→Diff→Rollback 全闭环真实 |
| 输入体验 | L2.5 | 仅 rule_type select + JSON TextArea，无结构化表单 |
| 错误/校验体验 | L4 | 全局错误处理 + request ID + 编译校验门 |
| Diff/发布/回滚体验 | L3.5 | Diff 浅层比较拉低评分 |
| 数据可靠性 | L4 | fail-fast + backup + recovery + schema migration |
| 自维护性 | L3 | 文档较全，根目录脚本待归档 |
| 可观测性 | L4 | 文件日志 + 错误码 + request_id + schema version |

---

## 3. 已验证的真实能力

### 3.1 后端（全部真实执行）

| 能力 | 证据（文件:函数） | 测试 |
|------|-----------------|------|
| 规则编译（DSL + Template 6 种） | `rule_compiler.py:RuleCompiler.compile()` | test_rule_engine_platform.py |
| SingleFact 执行器（3 子类型） | `single_fact_executor.py:SingleFactExecutor.execute()` | 间接 |
| GroupConsistency 执行器 | `group_consistency_executor.py:GroupConsistencyExecutor.execute()` | 间接 |
| Threshold 执行器（7 算子） | `threshold_executor.py:ThresholdExecutor.execute()` | 间接 |
| Topology 执行器（3 子类型） | `topology_executor.py:TopologyExecutor.execute()` | 直接 18 tests |
| 规则引擎调度（compile→validate→scope→dispatch） | `engine.py:RuleEngine.execute()` | 多文件 |
| JSON 损坏检测+恢复+备份 | `repository.py:_read_json()/_backup_file()` | 11 tests |
| Schema 迁移（baselines.json v0→v1.0→v1.1） | `repository.py:_apply_schema_migration()` | 5 tests |
| 全局异常处理+错误码 | `error_handler.py:register_error_handlers()` | 8 tests |
| Request ID 追踪 | `error_handler.py:RequestIdMiddleware` | 8 tests |
| Publish Body 绑定+校验门 | `rules.py:publish_baseline()` → `RulePublishWorkflowService` | 11 tests |
| Diff（含 field_changes + human_summary） | `baselines.py:get_baseline_diff()` → `hist_svc.diff_versions()` | 5 tests |
| Rollback 候选创建 | `rules.py:create_rollback_candidate()` | 集成测试 |
| 7 个 API 端点 | `routers/baselines.py` + `routers/rules.py` | 8 tests |
| CLI 10+ 命令 | `cli/main.py:main()` | 1 test (pre-existing failure) |

### 3.2 前端（全部真实交互，除 Save Draft）

| 能力 | 证据 |
|------|------|
| 三栏布局 + useReducer 状态机 | `App.tsx:300-374`, `pageReducer.ts:28-222` |
| 基线导航树 | `BaselineList.tsx` → 真实 API 调用 |
| 规则编辑器 | `RuleEditor.tsx:25-145` |
| 校验流程 | `App.tsx:122-155` → POST /api/rules/draft/validate |
| 发布流程（含确认/阻断） | `App.tsx:157-198` → POST /api/rules/publish/{id} |
| Diff 查看 | `App.tsx:200-218` → GET /api/baselines/{id}/diff |
| Rollback 流程 | `App.tsx:220-262` → POST /api/rules/rollback |
| 默认 Real API | `client.ts:16` USE_MOCK_API==='true' 才启用 Mock |

---

## 4. 仍存的能力幻觉

| # | 功能 | 状态 | 证据 | 修复方案 |
|---|------|------|------|---------|
| 1 | handleSaveDraft | ❌ FAKE | `App.tsx:264-272`: setTimeout 模拟，无后端 API | 新增 POST /api/rules/draft/save |
| 2 | Diff 嵌套字段检测 | ⚠️ PARTIAL | `rule_baseline_history_service.py:126-131`: 仅顶层 key | 递归比较嵌套结构 |

---

## 5. 下一迭代开发计划

### P1（优先修复）

| # | 问题 | 修改位置 | 验收标准 |
|---|------|---------|---------|
| P1-1 | handleSaveDraft 伪实现 | `App.tsx` + 新增 API + Service | Save Draft 调用真实后端 |
| P1-2 | Diff 浅层比较 | `rule_baseline_history_service.py` | 递归比较，changed_fields 含完整路径 |
| P1-3 | Executor 独立测试 | `tests/test_*_executor.py`（3 个新文件） | 每个执行器独立测试覆盖 |
| P1-4 | tasks.json schema 迁移 | `repository.py` | 同 baselines.json 模式 |

### P2（后续优化）

| # | 问题 | 修改位置 |
|---|------|---------|
| P2-1 | 根目录脚本归档 | 移动到 archive/scripts/ |
| P2-2 | 前端 bundle 优化 | vite.config.ts code splitting |
| P2-3 | 前端 E2E 测试 | Playwright/Vitest |
| P2-4 | Rollback 完整 rule_set | rules.py:create_rollback_candidate() |
| P2-5 | test_run_core 修复 | task lifecycle 状态机 |
| P2-6 | 日志 request_id 验证 | 集成测试 |

---

## 6. 架构约束（勿违反）

1. **DIP**：Domain 层不 import Infrastructure 层，通过 Protocol 接口解耦
2. **原子写入**：所有 JSON 持久化通过 `_write_json()`（备份 → temp → os.replace）
3. **Fail-Fast**：`_read_json()` 不允许静默吞掉损坏数据
4. **状态机守卫**：`pageReducer` 每个 case 有状态守卫，新加 Action 必须同步
5. **DTO 隔离**：API 入参出参经过 Pydantic DTO 验证
6. **错误码**：新增异常必须分配 ErrorCode
7. **Validation Gate**：publish 必须经过 RuleCompiler 编译校验
8. **Schema Version**：修改数据结构时必须 bump version + 添加迁移函数
9. **Diff DTO 统一**：前端使用 `rules[]` + `change_type`，不假设旧格式

---

## 7. 启动方式

```bash
# 后端
python -m uvicorn src.presentation.api.main:app --reload --host 0.0.0.0 --port 8000

# 前端
cd frontend && npm install && npm run dev
# 默认 Real API，Mock 需设置 VITE_USE_MOCK_API=true
```

---

## 8. 测试方式

```bash
# 后端全量（排除 pre-existing failure）
python -m pytest tests/ --ignore=tests/test_run_core.py --ignore=tests/test_ai_rule_generation_legacy.py -v

# 前端构建验证
cd frontend && npx tsc --noEmit && npm run build
```

---

## 9. 修改文件清单

| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `docs/PROJECT_STATE_SNAPSHOT.yaml` | 更新 | 审计后全面更新 |
| `docs/AI_HANDOFF/PROJECT_STATUS.md` | 新建 | 本文件 — 审计结构化状态 |
