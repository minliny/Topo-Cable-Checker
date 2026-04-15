# Minimal Observation Instrumentation

## 1. 目标

为 Observation / Product Usage Window 提供“足够用”的审计证据，不建设 analytics 平台，不引入外部 infra。

设计原则：

- best-effort：任何记录失败不影响主业务流程（仅 warning，吞掉异常）
- 最小侵入：仅在少数高价值写/查看路径埋点
- 可审计：append-only JSONL
- 本地/单实例友好：不为分布式提前设计

## 2. 数据落点（Append-only JSONL）

- 路径：`data/observations/events.jsonl`
- 格式：JSON Lines（每行一条 JSON）

事件示例：

```json
{"ts":"2026-04-15T12:00:00.000Z","event_type":"draft_saved","baseline_id":"B001","request_id":"...","actor":"alice","context":{"rule_id":"r1","rule_type":"threshold"}}
```

## 3. 事件清单（Selected Signals）

- `draft_saved`
- `draft_overwritten`
- `draft_diff_viewed`
- `publish_executed`
- `clear_draft`
- `occ_conflict`

Actor / Session：

- `actor`：可选，来自 `X-Actor` 请求头
- `request_id`：来自 `X-Request-ID` 或服务端自动生成

## 4. Retention / Rotation 策略

为避免无限增长，事件日志采用文件级 rotation：

- 单文件阈值：5MB（`MAX_BYTES`）
- 保留份数：3（`BACKUP_COUNT`）
- 轮转文件：
  - `events.jsonl`（当前）
  - `events.jsonl.1`（最近一次轮转）
  - `events.jsonl.2`
  - `events.jsonl.3`

轮转策略为 best-effort：轮转失败不会阻断写入路径。

## 5. 如何消费（最小分析方法）

### 5.1 统计多规则覆盖频率（draft_overwritten）

```bash
jq -r 'select(.event_type=="draft_overwritten") | .baseline_id' data/observations/events.jsonl | sort | uniq -c | sort -nr | head
```

### 5.2 统计发布前是否看过 draft diff（publish_without_diff 的派生）

最小做法：用 `request_id`/时间窗口做 join（推荐后续用一个小脚本在 Observation 周期内离线跑）。

### 5.3 连续发布聚类（consecutive_publish_cluster 的派生）

按 baseline_id 分组后，以时间窗口（例如 10 分钟）聚类连续 `publish_executed` 即可得到 workaround 强度证据。

## 6. 触发判定建议（示例）

- Draft Model Evolution Trigger（候选）：
  - `draft_overwritten` 高且持续
  - `publish_executed` 在短时间窗口内高频聚类（同 baseline）
  - 结合 Stakeholder/UAT 原话确认后升级为 “Confirmed Product Requirement”

