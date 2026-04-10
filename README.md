# 连线端口检查工具

一个面向工程场景的本地化连线/端口检查与规则治理平台。

它不只是一个临时的 Excel 校验脚本，而是一个支持 **数据导入、规则检查、问题输出、规则编辑、编译校验、版本发布与持续演进** 的工程质检系统。

---

## 项目定位

本项目聚焦于设备、端口、链路、拓扑关系等工程数据的自动化检查，目标是把“写死在代码里的检查逻辑”升级为“可管理、可发布、可治理的规则平台”。

一句话概括：

> 以端口/链路检查为核心，以规则引擎为基础，以规则编辑与治理为长期能力方向的工程检查平台。

---

## 核心能力

- 工程表格数据导入与识别
- 数据标准化与基础契约校验
- 设备 / 端口 / 链路 / 拓扑规则检查
- 结构化问题输出与结果聚合
- Rule Catalog 驱动的规则定义与消费
- 规则编辑器（表单化创建规则）
- 草稿预编译与字段级错误映射
- 规则发布、版本治理、差异分析与回滚
- 后续支持 AI 辅助规则生成

---

## 当前进度

当前项目已完成或基本完成以下骨架能力：

- 底层规则协议重构
- `CompiledRule` 统一结构
- `RuleMeta / Capability` 语义定义
- `Rule Catalog` 目录与消费层
- `RuleEditor MVP`
- 表单校验与规则草稿生成
- 编辑器到治理链路桥接 (Governance Bridge)
- 草稿预编译 (compile preview)
- 编译与结构校验联通
- 字段级错误映射 (field-level error mapping)
- 发布候选摘要基础

当前阶段判断：

> 项目已经完成规则平台基础骨架，正从“架构验证期”进入“产品闭环期”。

---

## 下一步重点

当前最关键的下一步是：

### Rule Publish Workflow MVP

目标是把“规则草稿”真正发布为“正式 baseline”，建立最小可用的发布闭环，包括：

- 发布前 compile + validate
- baseline 版本生成
- 发布摘要
- 发布记录
- 为 diff / 回滚打基础

---

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

---

## 路线图

### 阶段 1：核心检查闭环
数据输入、输入契约、规则执行、基础结果输出

### 阶段 2：规则平台化
`CompiledRule`、`RuleMeta / Capability`、`Rule Catalog`

### 阶段 3：RuleEditor MVP
规则类型选择、表单渲染、草稿生成、表单校验

### 阶段 4：治理桥接 (Governance Bridge)
草稿预编译 (compile preview)、compile + validate 联调、字段级错误映射 (field-level error mapping)

### 阶段 5：发布治理闭环 (Rule Publish Workflow MVP)
发布服务、baseline 版本生成、发布摘要、发布记录

### 阶段 6：差异分析与回滚
版本 diff、历史版本、回滚机制、影响分析

### 阶段 7：产品增强与 AI 能力
GUI 集成、结果展示增强、AI 辅助规则生成

---

## 项目愿景

长期来看，本项目将从“端口检查工具”演进为：

**一个面向工程设备、端口、链路与拓扑数据的本地规则平台，支持从数据导入、结构化检查，到规则编辑、编译校验、版本发布、差异追踪与 AI 辅助生成的完整闭环。**
