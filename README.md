# 规则治理工作台（Rule Governance Workbench）

一个面向高风险规则配置场景的治理系统，提供规则编辑、校验、版本管理、差异对比、发布控制与安全回滚能力。

---

## 项目简介

本项目将“直接修改配置文件”的流程升级为**可验证、可追溯、可回滚的规则治理流程**，适用于对规则变更安全性要求较高的场景，例如：

* 风控规则
* 告警/阈值策略
* 网络/拓扑检查规则
* 任意高风险配置系统

当前版本为 **MVP（最小可用产品）**，已具备完整端到端闭环能力。

---

## 核心能力

* **规则编辑工作台**：三栏结构（导航 / 主视图 / 辅助面板）
* **结构化校验**：发布前拦截非法配置
* **字段级定位**：错误可反向定位到具体输入位置
* **版本化管理**：每次发布生成可追踪版本
* **差异对比（Diff）**：查看规则新增 / 删除 / 修改
* **安全回滚**：回滚生成候选草稿，不直接覆盖线上
* **状态机驱动 UI**：复杂流程可推导、可恢复、可测试

---

## 系统架构

```text
前端（React + TypeScript）
  ↓
API 层（FastAPI + DTO）
  ↓
应用层（发布 / 校验 / Diff / 回滚）
  ↓
领域层（规则模型 / 基线模型）
  ↓
基础设施层（JSON 持久化）
```

设计原则：

* 前后端解耦（API + DTO）
* 状态机驱动 UI
* 领域逻辑与接口分离
* 数据持久化具备安全写入能力

---

## 项目结构

```text
frontend/        前端工作台
src/             后端（应用 / 领域 / API）
data/            基线与版本数据
tests/           API 与集成测试
docs/            文档（架构 / 验收 / 路线图）
```

---

## 快速开始

### 启动后端

```bash
./start_api.sh
```

### 启动前端

```bash
./start_frontend.sh
```

### 手动方式

后端：

```bash
pip install fastapi uvicorn pydantic pytest httpx
uvicorn src.presentation.api.main:app --reload
```

前端：

```bash
cd frontend
npm install
VITE_USE_MOCK_API=false VITE_API_BASE_URL=http://localhost:8000/api npm run dev
```

---

## 基本使用流程

```text
编辑规则
  → 校验
  → 发布确认
  → 发布成功 / 阻断
  → 版本记录
  → 差异对比
  → 回滚候选
```

---

## 测试与验收

运行测试：

```bash
pytest -v
```

手工验收：

* [docs/ACCEPTANCE_CHECKLIST.md](docs/ACCEPTANCE_CHECKLIST.md)

演示流程：

* [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)

---

## 文档

建议阅读顺序：

1. [docs/PROJECT_STATUS_SUMMARY.md](docs/PROJECT_STATUS_SUMMARY.md)
2. [docs/PROJECT_POSITIONING.md](docs/PROJECT_POSITIONING.md)
3. [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)
4. [docs/ACCEPTANCE_CHECKLIST.md](docs/ACCEPTANCE_CHECKLIST.md)

---

## 已知限制

* 当前未接入用户身份与权限体系
* Diff 可进一步增强可读性
* 大规模配置输入体验仍可优化
* 持久化仍基于 JSON 文件（未接入数据库）

详见：

* [docs/KNOWN_GAPS.md](docs/KNOWN_GAPS.md)

---

## 路线图

下一阶段重点：

* 优化规则输入体验（如 Monaco Editor）
* 提升 Diff 可读性
* 引入权限与审批机制
* 引入数据库与并发控制

---

## 项目定位

> 一个具备规则发布、防错校验、版本追踪与安全回滚能力的规则治理工作台 MVP。

---

适用于：

* 规则治理系统开发
* 高风险配置管理场景
* 状态机驱动 UI 架构参考
* 前后端分离工作台设计参考