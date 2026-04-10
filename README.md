# CheckTool

CheckTool 是一个基于 Python 的规则检查与编排工具，采用严格的五层领域驱动设计（DDD）架构。它提供了从基线管理、任务创建、数据识别、规则执行到结果交付的完整生命周期管理。

## 架构设计

项目遵循严格的 5 层架构模型，确保关注点分离与高可维护性：
1. **Presentation (展示层)**: 提供 CLI 命令行交互界面 (`src/presentation/cli/main.py`) 以及结果交付模块 (`Result Delivery`)。
2. **Application (应用层)**: 包含核心服务的编排逻辑与查询服务，作为防腐层（ACL）负责领域实体与 DTO 的转换。
3. **Domain (领域层)**: 核心业务逻辑与模型，包含规则引擎 (Rule Engine)、事实模型 (Facts) 以及结构化的结果模型。
4. **Infrastructure (基础设施层)**: 外部依赖适配器，如 Excel 读取器 (`ExcelReader`) 和基于 JSON 的数据仓储 (`Repository`)。
5. **Cross-cutting (横切关注点)**: 提供通用的工具类支持（如日志、剪贴板、IDE 启动器、临时文件管理等）。

## 核心特性

- **完整的检查流编排**: 支持基线管理、任务创建、自动识别、执行检查和结果汇总。
- **灵活的结果交付 (Result Delivery)**: 
  - 支持将检查结果格式化为 Markdown 或纯文本。
  - 自动将结果复制到系统剪贴板。
  - 自动创建临时文件，并尝试使用 IDE（如 PyCharm）或系统默认编辑器打开结果。
  - 具备优雅降级能力（剪贴板或 IDE 启动失败不影响主流程）。
- **依赖倒置原则 (DIP)**: 核心业务逻辑不依赖于具体的数据存储实现，通过 `IRepository` 接口进行解耦。

## 安装与配置

1. **环境要求**: Python 3.8+
2. **安装依赖**:
   ```bash
   pip install -r requirements.txt
   ```

## 快速开始

使用 CLI 入口点进行各种操作：

```bash
# 1. 查看基线列表
python src/presentation/cli/main.py baseline list

# 2. 创建检查任务
python src/presentation/cli/main.py task create --baseline <id> --file <path>

# 3. 执行识别
python src/presentation/cli/main.py recognize --task <task_id>

# 4. 确认识别结果
python src/presentation/cli/main.py confirm-recognition --task <task_id>

# 5. 执行检查规则并交付结果
python src/presentation/cli/main.py run --task <task_id>
```

### 结果交付高级选项

`run` 命令支持多种结果交付相关的参数控制：

```bash
# 默认行为：将结果复制到剪贴板，并在 PyCharm/IDE 中打开 Markdown 格式报告
python src/presentation/cli/main.py run --task <task_id>

# 禁用所有交付行为（不复制剪贴板，不打开 IDE）
python src/presentation/cli/main.py run --task <task_id> --no-copy-result --no-open-result

# 指定输出为纯文本格式，并限制最多显示 10 个 Issue
python src/presentation/cli/main.py run --task <task_id> --result-format text --max-issues 10
```

## 测试与开发

- **自动化测试**: 项目使用 `pytest` 进行测试，运行以下命令执行所有测试：
  ```bash
  pytest
  ```
- **探索性测试**: 位于 `archive/scripts/manual/` 的脚本用于手动的调试与流程验证。
