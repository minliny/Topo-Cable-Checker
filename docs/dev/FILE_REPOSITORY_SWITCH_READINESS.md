# FileRepository Switch Readiness Audit

> **Status:** AUDIT PHASE — Default repository is still MockRepository  
> **Scope:** Local file persistence only — no database, no SQLite, no ORM.  
> **Last updated:** 2026-05-01

---

## 1. 概述

本文档记录从 MockRepository 切换到 FileRepository 作为默认 repository 的准备度审计结果。

**当前默认：MockRepository**
**目标：评估 FileRepository 是否可成为默认**

---

## 2. 切换前必须满足的条件

### 2.1 功能完整性

| 条件 | 状态 | 说明 |
|------|------|------|
| FileRepository 实现所有 Repository 接口方法 | ✅ | 已实现 |
| 优先读取 workspace JSON 文件 | ✅ | 已实现 |
| 缺失时 fallback 到 MockRepository | ✅ | 已实现 |
| workspace fixtures 可正常导出 | ✅ | 30 items |

### 2.2 API 兼容性

| 条件 | 状态 | 说明 |
|------|------|------|
| FileRepository 模式 smoke test 通过 | ✅ | 18/18 |
| FileRepository 模式 API snapshot 匹配 | ✅ | 21/21 |
| MockRepository 与 FileRepository 响应一致 | 待审计 | 运行 audit_repository_response_parity.sh |
| Health 响应无数据库引用 | ✅ | 通过 |

### 2.3 运行时稳定性

| 条件 | 状态 | 说明 |
|------|------|------|
| FileRepository 模式后端可正常启动 | ✅ | 通过 |
| FileRepository 模式后端可正常停止 | ✅ | 通过 |
| 环境变量 TOPOCHECKER_REPO=file 生效 | ✅ | 通过 |
| CI 包含 FileRepository runtime 检查 | ✅ | 通过 |

### 2.4 文档和脚本

| 条件 | 状态 | 说明 |
|------|------|------|
| dev_start_backend_file_repo.sh 存在 | ✅ | 通过 |
| check_file_repository_runtime.sh 存在 | ✅ | 通过 |
| WORKSPACE_FIXTURES.md 文档完整 | ✅ | 通过 |
| LOCAL_DEV_WORKFLOW.md 包含 FileRepository 说明 | ✅ | 通过 |

---

## 3. 当前审计结果

### 3.1 如何运行审计

```bash
bash scripts/audit_repository_response_parity.sh
```

### 3.2 审计内容

审计脚本会：
1. 导出 workspace fixtures
2. 启动 MockRepository 模式后端
3. 收集 20 个 API 端点的响应
4. 停止 MockRepository 后端
5. 启动 FileRepository 模式后端
6. 收集同样的 20 个 API 端点的响应
7. 逐条对比响应内容
8. 输出差异摘要

### 3.3 审计覆盖的端点

| 端点 | 说明 |
|------|------|
| `/health` | 健康检查 |
| `/api/baselines` | Baseline 列表 |
| `/api/baselines/baseline-001` | Baseline 详情 |
| `/api/rules/definitions` | Rule Definitions |
| `/api/rulesets` | Rule Sets |
| `/api/profiles/parameters` | Parameter Profiles |
| `/api/profiles/thresholds` | Threshold Profiles |
| `/api/scopes/selectors` | Scope Selectors |
| `/api/data-sources` | Data Sources |
| `/api/scopes` | Execution Scopes |
| `/api/recognition/status` | Recognition Status |
| `/api/baselines/baseline-001/versions` | Version 列表 |
| `/api/versions/baseline-001::v1.0.0` | Version Snapshot |
| `/api/versions/diff` | Version Diff |
| `/api/runs` | Run 历史 |
| `/api/runs/run-001` | Run 详情 |
| `/api/bundles/bundle-001` | Bundle |
| `/api/issues/issue-001` | Issue Detail |
| `/api/diff/recheck` | Recheck Diff |

### 3.4 审计结果解读

- **全部匹配**：MockRepository 和 FileRepository 返回完全相同的 JSON 响应，具备默认切换条件
- **存在差异**：需要修复 FileRepository 的实现，直到响应完全一致

---

## 4. 已知限制

### 4.1 Health 响应差异

MockRepository 模式的 health 响应包含 `"mode": "mock"`，FileRepository 模式可能包含不同的 mode 标识。这是预期行为，不影响功能。

### 4.2 字段顺序差异

JSON 字段顺序不同不影响语义等价性。审计脚本使用字符串精确匹配，因此字段顺序差异会被标记为不匹配。实际切换时应使用语义比较。

### 4.3 动态字段差异

某些字段（如时间戳、随机 ID）可能在两种模式下不同。这些差异不影响功能等价性。

---

## 5. 切换决策矩阵

| 条件 | 要求 | 当前状态 |
|------|------|----------|
| 功能完整性 | 100% | ✅ |
| API 兼容性 | 100% | 待审计 |
| 运行时稳定性 | 100% | ✅ |
| 文档完整 | 100% | ✅ |
| CI 覆盖 | 100% | ✅ |
| **综合评估** | **全部满足** | **待审计后决定** |

---

## 6. 切换流程（未来执行）

当审计确认响应完全一致后，按以下步骤切换：

1. 更新 `provider.py` 默认值为 `file`
2. 更新 `dev_start_backend.sh` 不再显式设置 `TOPOCHECKER_REPO`
3. 更新文档说明默认已是 FileRepository
4. 运行全量检查验证
5. 提交并推送

---

## 7. 回滚方案

如果切换后发现问题，可立即回滚：

```bash
# 设置环境变量回退到 MockRepository
export TOPOCHECKER_REPO=mock

# 或使用旧脚本启动
bash scripts/dev_start_backend.sh
```

---

## 8. 禁止事项

- ❌ 禁止在审计阶段切换默认 repository
- ❌ 禁止移除 MockRepository fallback
- ❌ 禁止引入数据库 / SQLite / ORM
- ❌ 禁止修改 API response 结构
- ❌ 禁止切换默认 repository 直到审计全部通过
