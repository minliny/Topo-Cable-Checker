此次合并主要进行了工程架构规范化和核心功能的完善。实施了 DIP（依赖倒置原则）重构以解耦业务逻辑和数据访问层，引入了结果交付（Result Delivery）模块及配套的 CLI 命令行集成。同时，对项目文件目录结构进行了全面治理，移除了废弃脚本至归档目录，并补充了自动化测试与工程基线配置。
| 文件 | 变更 |
|------|---------|
| __pycache__/test_rule_language_matrix.cpython-314-pytest-9.0.2.pyc | - 更新了 Python 编译缓存文件 |
| __pycache__/test_rule_productization.cpython-314-pytest-9.0.2.pyc | - 更新了 Python 编译缓存文件 |
| add_tags.py | - 新增用于添加标签的脚本文件 |
| archive/application/query_services.py | - 从 src 目录迁移了废弃的 application 服务文件至归档目录 |
| archive/application/rule_editor_service.py | - 从 src 目录迁移了废弃的 application 服务文件至归档目录 |
| archive/application/rule_governance_service.py | - 从 src 目录迁移了废弃的 application 服务文件至归档目录 |
| archive/docs/RULE_EDITOR_DESIGN.md | - 将规则编辑器设计文档迁移至归档目录 |
| archive/presentation/local_web/main.py | - 归档了本地 Web 展示层相关代码 |
| archive/presentation/local_web/templates/baseline_diff.html | - 将本地 Web 展示层模板文件迁移至归档目录 |
| archive/presentation/local_web/templates/baseline_version_detail.html | - 将本地 Web 展示层模板文件迁移至归档目录 |
| archive/presentation/local_web/templates/baselines_list.html | - 将本地 Web 展示层模板文件迁移至归档目录 |
| archive/presentation/local_web/templates/device_review.html | - 将本地 Web 展示层模板文件迁移至归档目录 |
| archive/presentation/local_web/templates/diff_summary.html | - 将本地 Web 展示层模板文件迁移至归档目录 |
| archive/presentation/local_web/templates/rule_detail.html | - 将本地 Web 展示层模板文件迁移至归档目录 |
| archive/presentation/local_web/templates/rule_editor_detail.html | - 将本地 Web 展示层模板文件迁移至归档目录 |
| archive/presentation/local_web/templates/rule_editor_list.html | - 将本地 Web 展示层模板文件迁移至归档目录 |
| archive/presentation/local_web/templates/rules_list.html | - 将本地 Web 展示层模板文件迁移至归档目录 |
| archive/presentation/local_web/templates/run_overview.html | - 将本地 Web 展示层模板文件迁移至归档目录 |
| archive/presentation/local_web/templates/task_detail.html | - 将本地 Web 展示层模板文件迁移至归档目录 |
| archive/presentation/local_web/templates/task_list.html | - 将本地 Web 展示层模板文件迁移至归档目录 |
| archive/presentation/local_web/templates/templates_list.html | - 将本地 Web 展示层模板文件迁移至归档目录 |
| archive/scripts/generate_advanced_data.py | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/generate_config_driven_data.py | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/generate_modified_data.py | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/generate_test_data.py | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/README.md | - 新增归档脚本的 README 说明文档 |
| archive/scripts/manual/debug.py | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/debug2.py | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/find_unused.py | - 新增用于查找未使用代码的工具脚本 |
| archive/scripts/manual/test_acceptance.py | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/test_advanced_rules.sh | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/test_analysis.sh | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/test_config_driven_rules.sh | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/test_diff.sh | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/test_engine.py | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/test_engine2.py | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/test_flow.sh | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/test_pipeline.sh | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/test_rule_compiler.py | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/test_rule_editor.py | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/test_rule_governance.py | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/test_rule_language_hardening.py | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/test_rule_language_matrix.py | - 将各类数据生成及测试脚本迁移至归档目录 |
| archive/scripts/manual/test_rule_productization.py | - 将各类数据生成及测试脚本迁移至归档目录 |
| data/baselines.json | - 更新了测试及运行状态的数据结果文件（移除多余字段或更新基线数据） |
| data/export_0713baf2-56b3-452b-8c19-7e69cd9d7e52.json | - 更新了测试及运行状态的数据结果文件（移除多余字段或更新基线数据） |
| data/export_666f8332-0688-4b8f-9252-7dbaae92acbe.json | - 更新了测试及运行状态的数据结果文件（移除多余字段或更新基线数据） |
| data/exports.json | - 更新了测试及运行状态的数据结果文件（移除多余字段或更新基线数据） |
| data/issue_aggregates.json | - 更新了测试及运行状态的数据结果文件（移除多余字段或更新基线数据） |
| data/recognitions.json | - 更新了测试及运行状态的数据结果文件（移除多余字段或更新基线数据） |
| data/reviews.json | - 更新了测试及运行状态的数据结果文件（移除多余字段或更新基线数据） |
| data/run_diffs.json | - 更新了测试及运行状态的数据结果文件（移除多余字段或更新基线数据） |
| data/run_executions.json | - 更新了测试及运行状态的数据结果文件（移除多余字段或更新基线数据） |
| data/run_statistics.json | - 更新了测试及运行状态的数据结果文件（移除多余字段或更新基线数据） |
| data/run_summaries.json | - 更新了测试及运行状态的数据结果文件（移除多余字段或更新基线数据） |
| data/samples/test.xlsx | - 更新或新增了测试用例的 Excel 样本数据文件 |
| data/samples/test_advanced_data.xlsx | - 更新或新增了测试用例的 Excel 样本数据文件 |
| data/samples/test_config_driven_data.xlsx | - 更新或新增了测试用例的 Excel 样本数据文件 |
| data/samples/test_network_data.xlsx | - 更新或新增了测试用例的 Excel 样本数据文件 |
| data/samples/test_network_data_v2.xlsx | - 更新或新增了测试用例的 Excel 样本数据文件 |
| data/tasks.json | - 更新了测试及运行状态的数据结果文件（移除多余字段或更新基线数据） |
| diff_output.txt | - 新增包含 diff 输出记录的文本文件 |
| docs/ARCHITECTURE_STATUS.md | - 更新了架构状态文档 |
| docs/CLI_USAGE.md | - 更新了命令行接口（CLI）的使用说明文档 |
| docs/DIP_AND_STRUCTURE_REFACTOR.md | - 新增 DIP 解耦与结构重构的设计说明文档 |
| docs/DIRECTORY_GUIDE.md | - 更新了项目目录结构指南文档 |
| docs/ENGINEERING_P0_FIX.md | - 新增关于工程 P0 级别问题修复的说明文档 |
| docs/RESULT_DELIVERY.md | - 新增关于结果交付模块的设计与使用说明文档 |
| gen_report.py | - 新增用于生成测试与分析报告的脚本文件 |
| generate_report.py | - 新增用于生成测试与分析报告的脚本文件 |
| pytest.ini | - 新增 pytest 配置文件，规范化测试执行标准 |
| report.md | - 新增生成的项目运行报告文档 |
| requirements.txt | - 新增项目依赖配置文件，明确第三方库版本 |
| src/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/__pycache__/dto_models.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/__pycache__/query_services.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/__pycache__/rule_editor_service.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/__pycache__/rule_governance_service.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/baseline_services/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/baseline_services/__pycache__/baseline_service.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/baseline_services/baseline_service.py | - 重构代码以支持依赖注入（DIP），将具体的仓储实现替换为 IRepository 接口调用 |
| src/application/check_run_services/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/check_run_services/__pycache__/check_run_service.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/check_run_services/check_run_service.py | - 重构代码以支持依赖注入（DIP），将具体的仓储实现替换为 IRepository 接口调用 |
| src/application/export_services/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/export_services/__pycache__/export_service.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/export_services/export_service.py | - 重构代码以支持依赖注入（DIP），将具体的仓储实现替换为 IRepository 接口调用 |
| src/application/normalization_services/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/normalization_services/__pycache__/normalization_service.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/normalization_services/normalization_service.py | - 重构代码以支持依赖注入（DIP），将具体的仓储实现替换为 IRepository 接口调用 |
| src/application/recheck_services/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/recheck_services/__pycache__/recheck_service.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/recheck_services/recheck_service.py | - 重构代码以支持依赖注入（DIP），将具体的仓储实现替换为 IRepository 接口调用 |
| src/application/recognition_services/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/recognition_services/__pycache__/recognition_service.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/recognition_services/recognition_service.py | - 重构代码以支持依赖注入（DIP），将具体的仓储实现替换为 IRepository 接口调用 |
| src/application/result_query_services/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/result_query_services/__pycache__/result_query_service.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/result_query_services/result_query_service.py | - 重构代码以支持依赖注入（DIP），将具体的仓储实现替换为 IRepository 接口调用 |
| src/application/review_services/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/review_services/__pycache__/review_service.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/review_services/review_service.py | - 重构代码以支持依赖注入（DIP），将具体的仓储实现替换为 IRepository 接口调用 |
| src/application/task_services/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/task_services/__pycache__/task_service.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/application/task_services/task_service.py | - 重构代码以支持依赖注入（DIP），将具体的仓储实现替换为 IRepository 接口调用 |
| src/crosscutting/__init__.py | - 新增横切关注点模块初始化文件 |
| src/crosscutting/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/crosscutting/__pycache__/clipboard.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/crosscutting/__pycache__/ide_launcher.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/crosscutting/__pycache__/temp_files.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/crosscutting/clipboard.py | - 新增剪贴板操作相关的工具类 |
| src/crosscutting/config/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/crosscutting/config/__pycache__/settings.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/crosscutting/config/settings.py | - 更新了全局配置设置 |
| src/crosscutting/errors/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/crosscutting/errors/__pycache__/exceptions.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/crosscutting/ide_launcher.py | - 新增用于启动 IDE 的工具类 |
| src/crosscutting/ids/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/crosscutting/ids/__pycache__/generator.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/crosscutting/logging/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/crosscutting/logging/__pycache__/logger.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/crosscutting/temp_files.py | - 新增临时文件管理的工具类 |
| src/crosscutting/time/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/crosscutting/time/__pycache__/clock.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/domain/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/domain/__pycache__/baseline_model.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/domain/__pycache__/fact_model.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/domain/__pycache__/interfaces.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/domain/__pycache__/result_model.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/domain/__pycache__/rule_compiler.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/domain/__pycache__/rule_engine.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/domain/__pycache__/task_model.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/domain/executors/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/domain/executors/__pycache__/base_executor.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/domain/executors/__pycache__/group_consistency_executor.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/domain/executors/__pycache__/single_fact_executor.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/domain/executors/__pycache__/threshold_executor.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/domain/executors/__pycache__/topology_executor.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/domain/interfaces.py | - 新增领域层接口定义（如 IRepository），支持依赖倒置原则 |
| src/infrastructure/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/infrastructure/__pycache__/excel_reader.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/infrastructure/__pycache__/repository.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/infrastructure/repository.py | - 更新数据仓储实现，使其实现 IRepository 接口 |
| src/presentation/__init__.py | - 新增展示层模块初始化文件 |
| src/presentation/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/presentation/__pycache__/result_delivery.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/presentation/cli/__pycache__/__init__.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/presentation/cli/__pycache__/main.cpython-314.pyc | - 更新了 Python 编译缓存文件 |
| src/presentation/cli/main.py | - 集成了结果交付功能，移除了硬编码路径，并优化了命令行交互逻辑 |
| src/presentation/result_delivery.py | - 新增结果交付核心逻辑模块，负责将运行结果输出并打包 |
| test.xlsx | - 更新或新增了测试用例的 Excel 样本数据文件 |
| tests/__pycache__/test_normalization.cpython-314-pytest-9.0.2.pyc | - 更新了 Python 编译缓存文件 |
| tests/__pycache__/test_run_core.cpython-314-pytest-9.0.2.pyc | - 更新了 Python 编译缓存文件 |
| tests/test_normalization.py | - 新增相关模块的自动化测试用例，完善测试覆盖率 |
| tests/test_result_delivery.py | - 新增相关模块的自动化测试用例，完善测试覆盖率 |
| tests/test_run_core.py | - 新增相关模块的自动化测试用例，完善测试覆盖率 |
| tests/test_smoke.py | - 新增相关模块的自动化测试用例，完善测试覆盖率 |
| user_input.json | - 空更改或未发生实际变动 |
