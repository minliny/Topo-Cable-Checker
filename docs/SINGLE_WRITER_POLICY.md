# Single-writer Policy（File-based Persistence Reality）

## 1. 目的

本项目当前采用 file-based JSON persistence（`data/*.json`）+ revision OCC（`expected_revision`）来保护 baseline shared-state。

由于底层是“全量读 → 修改 → 全量写回”的文件写模式，**在多 writer（多进程/多实例/多 worker）下无法提供真实的并发正确性**。

因此，本项目在 Route C（Hybrid Transitional Route）阶段，必须把 single-writer 从“隐含假设”升级为“可执行现实约束”。

## 2. 支持的运行拓扑（Allowed）

- 单实例 API（单进程/单 worker）写入 `data/` 目录
- 或仅运行 CLI（单进程）写入 `data/` 目录
- 同一时刻只允许一个 writer 访问 `baselines.json`（通过文件锁强制）

## 3. 禁止的运行拓扑（Forbidden）

- 多 worker / 多进程 / 多副本同时指向同一 `data/` 目录写入
- API 与 CLI 并行写同一 `data/` 目录（尤其是 `baselines.json`）

## 4. 技术互斥策略（Baseline shared-state）

- `baselines.json` 写入采用进程间文件锁：`data/baselines.json.lock`
- 加锁失败（超时）会返回：
  - HTTP `423 Locked`
  - error_code `P1010`
  - 并记录 observation event：`single_writer_lock_timeout`

## 5. 如何观察违规/压力信号

- `single_writer_lock_timeout`：有并发 writer 尝试写入（应立即排查运行拓扑）
- `single_writer_lock_wait`：写入发生等待（说明有竞争或写操作变慢）
- `occ_conflict`：revision stale（并非 writer 互斥问题；更多是多会话编辑的“版本冲突”）

## 6. 何时应进入 DB / 多实例迁移阶段（Trigger）

满足任一即可视为触发：

- 单实例约束已成为交付阻碍（需要多实例部署或并发协作写入）
- `single_writer_lock_timeout` 开始在真实使用中反复出现
- `baselines.json` 文件体积增长导致写入等待明显上升（`single_writer_lock_wait` 持续上升）

该 policy 是过渡性现实硬化，不代表系统已支持多 writer。

