# DIP 解耦与结构整理报告 (DIP & Structure Refactor)

## 1. 改造背景
项目已完成 P0 级工程治理，具备了基础运行条件，但架构层面仍存在一个显著缺陷：**Application 层的多个服务直接 `import` 了 Infrastructure 层的具体仓储实现（如 `TaskRepository` 等）**，这违反了领域驱动设计（DDD）中的依赖反转原则（DIP）。此外，目录结构也需要轻量梳理。

## 2. DIP 解耦实施
- **引入抽象边界**：在 `src/domain/interfaces.py` 中，定义了 `ITaskRepository`, `IBaselineRepository`, `IResultRepository`, `IExcelReader` 等 Protocol 接口。这些接口属于 Domain 层，代表了应用层所需要的仓储与设施能力。
- **解耦 Application**：全面修改了 `src/application/` 下的所有服务（如 `CheckRunService`, `QueryService`, `TaskService` 等），使其 `__init__` 函数不再强制依赖 `src.infrastructure` 的具体类，而是接受上述 Protocol 类型的依赖注入。为了向下兼容防止炸毁现有代码，保留了对未注入时的后备处理（内部局部导入兜底）。
- **入口组装 (Composition Root)**：在表现层的两个入口（`src/presentation/cli/main.py` 和 `src/presentation/local_web/main.py`）中，统一进行了依赖项的具体实例化，并将其注入到各个 Application Service 中。此时，整个 Application 实现了与 Infrastructure 的物理脱钩。

## 3. 结构轻量优化
- 清理了根目录，确保无用脚本不污染环境。
- `scripts/` 与 `scripts/manual/` 进一步明确了职责：`manual` 用于存放需要手工验证的测试或分析脚本。
- 新增 `tests/` 下的基础验证结构，并确保 `pytest` 跑通。
- 新增本说明文件以帮助后续开发者快速理解。

## 4. 遗留问题与接手建议
- **遗留风险**：当前 Repository 接口使用的是 `Protocol`，并且为兼容性在 Application 层保留了 fallback `import`，以保证最小风险改造。下阶段如果需要彻底更换存储层（例如换成 SQLite），可以直接在入口处传入新实现，无需再动 Application 层代码。
- **后续接手建议**：下一位开发者可以安全地开始进行**数据持久化层升级**或**规则引擎高级能力演进**。当前的 `src/application` 已经安全隔离，不需要再担心存储方式变化引发连锁反应。
