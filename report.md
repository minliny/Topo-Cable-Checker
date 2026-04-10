此次合并主要引入了 Result Delivery 模块以支持检查结果的剪贴板复制和 IDE 自动打开功能，并对项目架构进行了领域驱动设计（DDD）的依赖反转（DIP）解耦，使得应用层不再强依赖具体的基础设施层实现。此外，合并还修复了硬编码路径配置，补充了项目依赖清单，并对项目目录结构进行了轻量化梳理和测试基线的建立。

| 文件 | 变更 |
|------|---------|
| __pycache__/test_rule_language_hardening.cpython-314-pytest-9.0.2.pyc | - 更新了编译后的字节码缓存文件 |
| __pycache__/test_rule_language_matrix.cpython-314-pytest-9.0.2.pyc | - 更新了编译后的字节码缓存文件 |
| __pycache__/test_rule_productization.cpython-314-pytest-9.0.2.pyc | - 更新了编译后的字节码缓存文件 |
| data/baselines.json | - 更新或新增了测试数据和运行记录 |
| data/export_507b2f6b-47be-40c4-8c80-d841c9ad6baf.json | - 更新或新增了测试数据和运行记录 |
| data/export_59b715b7-b904-4593-917c-e4e9ef0eb581.json | - 更新或新增了测试数据和运行记录 |
| data/export_a4d49b93-e4c1-4556-9fb8-69f821dbf2d5.json | - 更新或新增了测试数据和运行记录 |
| data/exports.json | - 更新或新增了测试数据和运行记录 |
| data/issue_aggregates.json | - 更新或新增了测试数据和运行记录 |
| data/recognitions.json | - 更新或新增了测试数据和运行记录 |
| data/reviews.json | - 更新或新增了测试数据和运行记录 |
| data/run_diffs.json | - 更新或新增了测试数据和运行记录 |
| data/run_executions.json | - 更新或新增了测试数据和运行记录 |
| data/run_statistics.json | - 更新或新增了测试数据和运行记录 |
| data/run_summaries.json | - 更新或新增了测试数据和运行记录 |
| data/samples/test.xlsx | - 更新或归档了 Excel 测试样本文件 |
| data/samples/test_advanced_data.xlsx | - 更新或归档了 Excel 测试样本文件 |
| data/samples/test_config_driven_data.xlsx | - 更新或归档了 Excel 测试样本文件 |
| data/samples/test_network_data.xlsx | - 更新或归档了 Excel 测试样本文件 |
| data/samples/test_network_data_v2.xlsx | - 更新或归档了 Excel 测试样本文件 |
| data/tasks.json | - 更新或新增了测试数据和运行记录 |
| docs/ARCHITECTURE_STATUS.md | - 更新了分层架构的状态描述<br>- 补充了结果交付和交叉功能的变更说明 |
| docs/CLI_USAGE.md | - 补充了 run 命令的新增高级参数及使用示例（结果格式化、剪贴板复制、IDE打开等） |
| docs/DIP_AND_STRUCTURE_REFACTOR.md | - 新增 DIP 解耦与目录结构整理的架构设计报告 |
| docs/DIRECTORY_GUIDE.md | - 更新了目录结构指南以反映表现层和交叉层的新增模块 |
| docs/ENGINEERING_P0_FIX.md | - 新增工程治理 P0 修复报告，包含依赖清单、硬编码路径修复及测试基线说明 |
| docs/RESULT_DELIVERY.md | - 新增结果交付模块的设计规范与测试说明 |
| pytest.ini | - 新增 pytest 配置文件以规范自动化测试路径和规则 |
| requirements.txt | - 新增项目依赖清单文件 |
| scripts/generate_advanced_data.py | - 归档或更新了数据生成脚本 |
| scripts/generate_config_driven_data.py | - 归档或更新了数据生成脚本 |
| scripts/generate_modified_data.py | - 归档或更新了数据生成脚本 |
| scripts/generate_test_data.py | - 归档或更新了数据生成脚本 |
| scripts/manual/README.md | - 新增说明文档，明确 manual 目录下脚本的用途为手动测试 |
| scripts/manual/debug.py | - 归档或更新了手动测试脚本 |
| scripts/manual/debug2.py | - 归档或更新了手动测试脚本 |
| scripts/manual/test_acceptance.py | - 归档或更新了手动测试脚本 |
| scripts/manual/test_advanced_rules.sh | - 归档或更新了手动测试脚本 |
| scripts/manual/test_analysis.sh | - 归档或更新了手动测试脚本 |
| scripts/manual/test_config_driven_rules.sh | - 归档或更新了手动测试脚本 |
| scripts/manual/test_diff.sh | - 归档或更新了手动测试脚本 |
| scripts/manual/test_engine.py | - 归档或更新了手动测试脚本 |
| scripts/manual/test_engine2.py | - 归档或更新了手动测试脚本 |
| scripts/manual/test_flow.sh | - 归档或更新了手动测试脚本 |
| scripts/manual/test_pipeline.sh | - 归档或更新了手动测试脚本 |
| scripts/manual/test_rule_compiler.py | - 归档或更新了手动测试脚本 |
| scripts/manual/test_rule_editor.py | - 归档或更新了手动测试脚本 |
| scripts/manual/test_rule_governance.py | - 归档或更新了手动测试脚本 |
| scripts/manual/test_rule_language_hardening.py | - 归档或更新了手动测试脚本 |
| scripts/manual/test_rule_language_matrix.py | - 归档或更新了手动测试脚本 |
| scripts/manual/test_rule_productization.py | - 归档或更新了手动测试脚本 |
| src/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/__pycache__/dto_models.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/__pycache__/query_services.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/__pycache__/rule_editor_service.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/__pycache__/rule_governance_service.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/baseline_services/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/baseline_services/__pycache__/baseline_service.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/baseline_services/baseline_service.py | - 重构了初始化方法以支持依赖注入，解耦具体的基础设施层实现 |
| src/application/check_run_services/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/check_run_services/__pycache__/check_run_service.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/check_run_services/check_run_service.py | - 重构了初始化方法以支持依赖注入，解耦具体的基础设施层实现 |
| src/application/export_services/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/export_services/__pycache__/export_service.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/export_services/export_service.py | - 重构了初始化方法以支持依赖注入，解耦具体的基础设施层实现 |
| src/application/normalization_services/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/normalization_services/__pycache__/normalization_service.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/query_services.py | - 重构了初始化方法以支持注入任务和结果仓储接口 |
| src/application/recheck_services/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/recheck_services/__pycache__/recheck_service.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/recheck_services/recheck_service.py | - 重构了初始化方法以支持依赖注入，解耦具体的基础设施层实现 |
| src/application/recognition_services/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/recognition_services/__pycache__/recognition_service.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/recognition_services/recognition_service.py | - 重构了初始化方法以支持依赖注入，解耦具体的基础设施层实现 |
| src/application/result_query_services/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/result_query_services/__pycache__/result_query_service.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/result_query_services/result_query_service.py | - 重构了初始化方法以支持依赖注入，解耦具体的基础设施层实现 |
| src/application/review_services/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/review_services/__pycache__/review_service.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/review_services/review_service.py | - 重构了初始化方法以支持依赖注入，解耦具体的基础设施层实现 |
| src/application/rule_editor_service.py | - 重构了初始化方法以支持注入 IBaselineRepository 接口 |
| src/application/rule_governance_service.py | - 重构了初始化方法以支持注入 IBaselineRepository 接口 |
| src/application/task_services/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/task_services/__pycache__/task_service.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/application/task_services/task_service.py | - 重构了初始化方法以支持依赖注入，解耦具体的基础设施层实现 |
| src/crosscutting/__init__.py | - 新增包初始化文件，标记 crosscutting 为模块 |
| src/crosscutting/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/crosscutting/__pycache__/clipboard.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/crosscutting/__pycache__/ide_launcher.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/crosscutting/__pycache__/temp_files.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/crosscutting/clipboard.py | - 新增跨平台剪贴板复制工具功能 |
| src/crosscutting/config/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/crosscutting/config/__pycache__/settings.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/crosscutting/config/settings.py | - 修复了硬编码的绝对路径，改为动态推导 BASE_DIR |
| src/crosscutting/errors/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/crosscutting/errors/__pycache__/exceptions.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/crosscutting/ide_launcher.py | - 新增了自动启动 IDE（如 PyCharm）或系统默认编辑器查看文件的功能 |
| src/crosscutting/ids/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/crosscutting/ids/__pycache__/generator.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/crosscutting/logging/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/crosscutting/logging/__pycache__/logger.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/crosscutting/temp_files.py | - 新增了生成带时间戳的安全临时文件功能 |
| src/crosscutting/time/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/crosscutting/time/__pycache__/clock.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/domain/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/domain/__pycache__/baseline_model.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/domain/__pycache__/fact_model.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/domain/__pycache__/interfaces.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/domain/__pycache__/result_model.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/domain/__pycache__/rule_compiler.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/domain/__pycache__/rule_engine.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/domain/__pycache__/task_model.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/domain/executors/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/domain/executors/__pycache__/base_executor.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/domain/executors/__pycache__/group_consistency_executor.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/domain/executors/__pycache__/single_fact_executor.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/domain/executors/__pycache__/threshold_executor.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/domain/executors/__pycache__/topology_executor.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/domain/interfaces.py | - 新增了领域层接口定义以实现依赖反转（DIP）解耦 |
| src/infrastructure/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/infrastructure/__pycache__/excel_reader.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/infrastructure/__pycache__/repository.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/infrastructure/repository.py | - 调整了仓储实现以适配新的接口约定 |
| src/presentation/__init__.py | - 新增包初始化文件，标记 presentation 为模块 |
| src/presentation/__pycache__/__init__.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/presentation/__pycache__/result_delivery.cpython-314.pyc | - 更新了编译后的字节码缓存文件 |
| src/presentation/cli/main.py | - 增加了依赖注入的组装逻辑<br>- 扩展了 run 命令支持结果格式化、剪贴板复制及 IDE 查看功能 |
| src/presentation/local_web/main.py | - 实现了仓储接口的具体实例化并注入到服务中以完成物理解耦 |
| src/presentation/result_delivery.py | - 新增了结果交付服务，负责将执行结果格式化并传递给剪贴板或 IDE |
| test.xlsx | - 移除了根目录下的冗余测试样本文件 |
| tests/__pycache__/test_result_delivery.cpython-314-pytest-9.0.2.pyc | - 更新了编译后的字节码缓存文件 |
| tests/__pycache__/test_smoke.cpython-314-pytest-9.0.2.pyc | - 更新了编译后的字节码缓存文件 |
| tests/test_result_delivery.py | - 新增了结果交付模块的自动化单元测试 |
| tests/test_smoke.py | - 新增了冒烟测试脚本，校验路径解析与领域层可用性 |
