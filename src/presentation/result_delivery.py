import logging
from typing import Dict, Any, List
from src.crosscutting.clipboard import copy_to_clipboard
from src.crosscutting.ide_launcher import open_in_ide
from src.crosscutting.temp_files import create_temp_result_file

logger = logging.getLogger(__name__)

class ResultDeliveryService:
    def format_markdown(self, task_id: str, run_id: str, summary: Any, stats: Any, issues: Any, max_issues: int = 20) -> str:
        """Formats the result data into a markdown string."""
        
        md_lines = []
        md_lines.append("# 检查执行结果\n")
        
        # Basic Info
        md_lines.append("## 基本信息\n")
        md_lines.append(f"- **任务ID**: {task_id}")
        md_lines.append(f"- **运行ID**: {run_id}")
        md_lines.append("")
        
        # Execution Summary
        md_lines.append("## 执行摘要\n")
        
        pass_count = stats.total_devices * stats.total_ports - issues.total_issues if stats else 0
        total_rules = 10 # Mock or pass real rules count
        
        md_lines.append(f"- **问题总数**: {issues.total_issues if issues else 0}")
        if issues and hasattr(issues, "by_severity"):
            for sev, count in issues.by_severity.items():
                md_lines.append(f"  - {sev}: {count}")
        md_lines.append("")
        
        # Overview Summary
        md_lines.append("## 总览摘要\n")
        if summary:
            md_lines.append(f"{summary.summary}\n")
            
        # Issues List
        md_lines.append("## 问题清单\n")
        if issues and hasattr(issues, "issues") and issues.issues:
            display_issues = issues.issues[:max_issues]
            md_lines.append(f"**显示前 {len(display_issues)} 条，共 {len(issues.issues)} 条问题**\n")
            
            for i, issue in enumerate(display_issues, 1):
                md_lines.append(f"### {i}. [{issue.severity}] {issue.rule_id}")
                md_lines.append(f"- **设备名称**: {issue.device_name}")
                md_lines.append(f"- **实际值**: {issue.actual_value}")
                md_lines.append("")
        else:
            md_lines.append("没有发现问题。\n")
            
        import datetime
        md_lines.append("---")
        md_lines.append(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(md_lines)

    def deliver_result(self, formatted_text: str, copy: bool = True, open_ide: bool = True, fmt: str = "markdown"):
        """Delivers the formatted text according to requested options."""
        ext = "md" if fmt == "markdown" else "txt"
        
        if copy:
            success = copy_to_clipboard(formatted_text)
            if success:
                logger.info("Result copied to clipboard successfully.")
            else:
                logger.warning("Failed to copy result to clipboard.")
                
        if open_ide:
            temp_file = create_temp_result_file(formatted_text, ext)
            if temp_file:
                logger.info(f"Temporary result file created at: {temp_file}")
                success = open_in_ide(temp_file)
                if not success:
                    logger.warning("Failed to open IDE.")
            else:
                logger.warning("Failed to create temporary result file.")
