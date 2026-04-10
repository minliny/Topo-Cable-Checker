# 分支统一与接力说明 (Branch Unification Handoff)

## 1. 当前仓库主线状态
**当前唯一开发主线**：`main` 分支。
该分支已包含 `trae/solo-agent-s2OD1r` 中的全部最新 5 层 DDD 架构实现，包含 CLI、本地 Web UI、Rule Editor、以及 6 层结果模型等核心能力。

## 2. 废弃与保留的旧分支
在本次分支治理中：
- **`master`**：由于包含了完全不同的旧版遗留代码与平台化残留（在 `ee78ee9` 之前），被视为**高风险历史归档分支**。此分支不再用于开发，仅作旧版代码查阅保留。
- **`trae/solo-agent-s2OD1r`**：作为新架构最完整实现，已**全量合并**至 `main` 并删除远程分支。
- **`trae/solo-agent-5ifudw`**：仅为早期架构计划分支，已被 `s2OD1r` 实现覆盖，已**清理删除**。
- **`refactor/create-new-skeleton`**、**`internal-migration`**、**`copilot/analyze-current-repo-structure`**：基于旧版 `master` 的废弃重构与迁移尝试，已完全失效，均已**清理删除**。

## 3. 给下一位开发代理的接力指导
1. **后续开发基线**：所有新功能、修复或迭代，**必须且仅能基于 `main` 分支**继续开发。
2. **不再触碰的旧分支**：**绝对不要**检出、合并或基于 `master` 分支做任何开发，其包含的旧版架构（`legacy_core`, `legacy_ui` 等）与当前的 5 层架构存在破坏性冲突。
3. **必读状态说明**：
   - 请先阅读 `docs/PROJECT_STATE_SNAPSHOT.yaml` 和 `docs/NEXT_STEPS.md` 了解目前功能实现进度（当前处于 `RULE_EDITOR_IMPLEMENTATION` 完成阶段）。
   - 架构约定见 `docs/ARCHITECTURE_STATUS.md` 与 `docs/DIRECTORY_GUIDE.md`。
4. **下一步推荐任务**：按照 `NEXT_STEPS.md`，推荐开展规则版本的 Diff 可视化、发布历史追踪、或将 JSON 存储迁移为 SQLite/PostgreSQL 等工作。
