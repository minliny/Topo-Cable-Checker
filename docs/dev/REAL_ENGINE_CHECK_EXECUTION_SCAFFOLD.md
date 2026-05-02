# REAL_ENGINE_CHECK_EXECUTION_SCAFFOLD

## 概述

本文档描述 RealEngineAdapter 的 check execution scaffold 实现。
当前版本生成空的 CheckResultBundle 骨架，不执行真实规则检查。

## 架构

```
Frontend / Backend Service
         │
         ▼
    ExecutionService
         │
         ▼
    Engine Adapter (RealEngineAdapter)
         │
         ├── start_check() ──────► workspace/runs/{run_id}.json
         ├── get_run_status() ◄─── workspace/runs/{run_id}.json
         └── get_bundle() ◄─────── workspace/runs/{run_id}.json
```

## 实现详情

### start_check()

**签名**：
```python
async def start_check(
    self,
    baseline_id: str,
    data_source_id: str,
    scope_id: str,
    parameter_profile_id: Optional[str] = None,
    threshold_profile_id: Optional[str] = None,
) -> str
```

**流程**：
1. 生成唯一的 `run_id` (格式: `run-{uuid[:8]}`)
2. 查找匹配的 recognition snapshot (通过 `data_source_id`)
3. 创建 run metadata 并保存到 `workspace/runs/{run_id}.json`
4. 返回 `run_id`

**Workspace Run Data**：
```json
{
  "run_id": "run-xxxxxxxx",
  "baseline_id": "baseline-001",
  "data_source_id": "sample_topology",
  "scope_id": "scope-full",
  "recognition_id": "rec-xxxxxxxx",
  "parameter_profile_id": null,
  "threshold_profile_id": null,
  "status": "scaffold_completed",
  "started_at": "2026-05-02T...",
  "completed_at": "2026-05-02T...",
  "device_count": 0,
  "issue_count": 0,
  "bundle_id": "bundle-xxxxxxxx"
}
```

### get_run_status()

**签名**：
```python
async def get_run_status(self, run_id: str) -> str
```

**返回值**：
- `scaffold_completed`：scaffold 生成的 run
- `completed`：mock data run (legacy)

### get_bundle()

**签名**：
```python
async def get_bundle(self, run_id: str) -> Optional[CheckResultBundle]
```

**返回**：
```python
CheckResultBundle(
    bundle_id="bundle-xxxxxxxx",
    run_id="run-xxxxxxxx",
    baseline_id="baseline-001",
    severity_summary=SeveritySummary(
        critical=0, high=0, medium=0, low=0, info=0
    ),
    issue_count=0,
    issues=[],  # 空列表，不生成 IssueItem
    created_at="2026-05-02T..."
)
```

## 约束

1. **不执行真实规则检查**
   - 不加载规则定义
   - 不遍历设备列表
   - 不计算任何问题

2. **不生成 IssueItem**
   - `issues` 始终为空列表
   - `issue_count` 始终为 0
   - 所有 `SeveritySummary` 字段为 0

3. **不使用数据库**
   - 所有数据存储在 workspace JSON 文件
   - 使用 FileRepository 管理

4. **不使用 AI/LLM**
   - 无外部 API 调用
   - 纯本地文件操作

## 与 MockEngineAdapter 的对比

| 功能 | MockEngineAdapter | RealEngineAdapter (scaffold) |
|------|------------------|-------------------------------|
| start_check | 返回 `run-new-001` | 生成唯一 run_id，写入 workspace |
| get_run_status | 返回 `completed` | 返回 `scaffold_completed` |
| get_bundle | 返回 mock data | 从 workspace 读取，生成空骨架 |

## 默认 Engine

默认 engine 仍然是 **MockEngineAdapter**。
使用 `TOPOCHECKER_ENGINE=real` 启动后端以使用 RealEngineAdapter。

## 文件清单

- `backend/engine/real_engine.py` - RealEngineAdapter 实现
- `backend/models/execution.py` - CheckResultBundle 模型
- `workspace/runs/{run_id}.json` - Run metadata
- `workspace/snapshots/recognition/{recognition_id}.json` - Recognition snapshot

## 未来扩展

1. 实现真实规则检查引擎
2. 生成真实 IssueItem
3. 支持规则参数配置
4. 支持阈值配置
5. 添加规则执行状态跟踪