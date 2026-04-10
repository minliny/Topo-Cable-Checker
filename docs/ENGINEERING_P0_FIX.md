# 工程治理 P0 修复报告

## 1. 补齐依赖清单
新增了 `requirements.txt`，补齐了由于缺乏依赖管理导致的“落地即死”问题。涵盖的核心包包括：`fastapi`, `uvicorn`, `jinja2`, `python-multipart`, `openpyxl`, `requests`, `pyyaml`, `pytest`。

## 2. 修复硬编码路径
修复了 `src/crosscutting/config/settings.py` 中写死绝对路径 `/workspace` 的致命缺陷。现在 `BASE_DIR` 是通过 `Path(__file__).resolve().parent.parent.parent.parent` 向上动态推导的。项目无论被 Clone 到哪个层级的目录下都能正常定位到根目录进行读写。

## 3. 根目录大扫除
清理了近 20 个散落的测试与辅助脚本。
- **样本数据**（如 `test_advanced_data.xlsx`）归档到了 `data/samples/`。
- **辅助生成脚本**（如 `generate_*.py`）归档到了 `scripts/`。
- **手工执行脚本**（如 `test_engine.py`, `test_flow.sh`）归档到了 `scripts/manual/`。
现在的根目录非常清爽，只留下 `src/`, `data/`, `docs/`, `scripts/`, `tests/` 和核心配置文件。

## 4. 自动化测试基线 (pytest)
建立了正规的自动化测试体系基线。
- 新增 `pytest.ini` 以规范收集路径。
- 在 `tests/` 下建立了 `test_smoke.py`，成功跑通了配置路径解析与 Domain 核心 `TemplateRegistry` 的可用性校验断言。后续可基于此直接追加业务单测。
