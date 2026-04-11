# 端到端人工验收清单 (Acceptance Checklist)

本文档旨在为 QA 或新接手的开发者提供一步步的操作指南，无需了解底层代码即可验证整个三栏工作台系统是否运行正常且后端业务逻辑是否闭环。

## 一、环境准备与启动

### 1. 启动真实后端 API
在终端执行：
```bash
chmod +x start_api.sh
./start_api.sh
```
**预期结果**：
- 自动安装依赖
- 自动运行 7 个 API 回归测试用例，结果为 `PASS`
- 最终提示 `Uvicorn running on http://0.0.0.0:8000`

### 2. 启动前端工作台
在另一个终端执行：
```bash
chmod +x start_frontend.sh
./start_frontend.sh
```
**预期结果**：
- 自动设置 `VITE_USE_MOCK_API=false`（对接刚才启动的 8000 端口）
- 最终提示 `Network: http://<ip>:5173/`

### 3. 打开页面
使用浏览器访问 `http://localhost:5173`。

---

## 二、验收执行步骤

### 步骤 1：验证基线加载与树状渲染
- **操作**：观察页面左侧栏。
- **预期结果**：
  - 出现 `Baseline B001` 根节点。
  - 下方展开 `Draft` 以及至少一个历史版本节点（如 `v1.0` 或 `v1.9` 等）。
  - 中间显示 `Select a baseline or version to view` 或默认选中 Draft 显示编辑器。

### 步骤 2：验证非法规则拦截与错误定位 (Validate)
- **操作**：
  1. 在左侧栏点击 `Draft` 节点。
  2. 在中栏编辑器的 `Rule Type` 下拉框中，选择任意选项。
  3. 在 `Rule Parameters (JSON)` 文本框中输入：`{"operator": "unknown"}`。
  4. 点击右上角的 **Validate** 按钮。
- **预期结果**：
  - 按钮变为 loading 状态约一秒。
  - 随后右侧面板切换到 `Validation Results`，并显示一条红色的错误：“Unsupported rule_type”。
  - （加分项：若实现了物理滚动，点击这条错误信息，中栏会高亮对应的输入框）。

### 步骤 3：验证 Publish 阻断拦截 (Publish Blocked)
- **操作**：
  1. 保持上一步的输入不变。
  2. （或在 JSON 中加入 `"block": true`）。
  3. 强制点击 **Prepare Publish** -> **Confirm Publish**。
- **预期结果**：
  - 界面进入全屏遮罩 `PUBLISH CHECKING...`。
  - 随后停留在一个带有大红叉的 **Publish Blocked** 界面，并列出具体的阻断原因。
  - 点击 `Return to Editor to Fix` 按钮能无缝退回之前的草稿编辑器，且输入的数据未丢失。

### 步骤 4：验证真实发布与新版本落盘 (Publish Success)
- **操作**：
  1. 在 JSON 文本框中输入合法配置，例如：`{"threshold_key": "T1"}`。
  2. 点击 **Prepare Publish** -> **Confirm Publish**。
- **预期结果**：
  - 界面显示短暂的 `PUBLISH CHECKING...`。
  - 随后显示绿色对勾 **Successfully Published!**。
  - **重要验收**：约 1.5 秒后，左栏树的下方会**自动长出一个全新的版本节点**（例如 `v1.10`），且页面自动跳转至这个新版本的历史详情页（右侧栏显示发布时间）。

### 步骤 5：验证历史差异计算 (Diff)
- **操作**：
  1. 在左栏选中刚刚发布的新版本节点。
  2. 点击历史详情页右上角的 **Compare Changes** 按钮。
- **预期结果**：
  - 页面进入 Diff 模式。
  - 右上角的摘要统计栏（Added/Modified/Removed）会有真实的数字变化。
  - 中栏会以列表形式展现规则的前后差异（比如新增了一条规则，或者某条规则的具体 JSON 被修改了）。

### 步骤 6：验证回滚候选语义 (Rollback)
- **操作**：
  1. 在左栏点击一个**非最新**的历史版本（例如 `v1.0`）。
  2. 点击右上角的 **Rollback to this** 按钮。
  3. 弹窗确认覆盖当前草稿。
- **预期结果**：
  - 左侧树中自动生成一个带紫色历史图标的 **Rollback Candidate** 节点。
  - 中栏编辑器被唤起，且参数输入框内**已经填充了该历史版本的真实 JSON 规则**。
  - 编辑器顶部有紫色标签提示：“This is a rollback candidate”。
  - 点击右上角的 **Discard Candidate** 可以安全放弃回滚并清理界面。

---

如果上述 6 个步骤全部按照“预期结果”发生，说明系统的**前端状态机 -> 接口转换 -> 后端领域逻辑 -> 持久化存储**的闭环已经完全畅通，达到生产验收标准。