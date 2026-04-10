import logging
from typing import Dict, Any, List
from src.crosscutting.clipboard import copy_to_clipboard
from src.crosscutting.ide_launcher import open_in_ide
from src.crosscutting.temp_files import create_temp_result_file

logger = logging.getLogger(__name__)

class ResultDeliveryService:
    def format_output(self, task_id: str, run_id: str, summary: Any, stats: Any, issues: Any, max_issues: int = 20, fmt: str = "markdown") -> str:
        """Formats the result data into a string (markdown or text)."""
        
        # Boundary handling for max_issues
        if max_issues < 0:
            max_issues = 0

        lines = []
        is_md = (fmt == "markdown")
        
        h1 = "# " if is_md else ""
        h2 = "## " if is_md else ""
        h3 = "### " if is_md else ""
        bold = "**" if is_md else ""
        list_item = "- "
        
        lines.append(f"{h1}检查执行结果\n")
        
        # Basic Info
        lines.append(f"{h2}基本信息\n")
        lines.append(f"{list_item}{bold}任务ID{bold}: {task_id}")
        lines.append(f"{list_item}{bold}运行ID{bold}: {run_id}")
        lines.append("")
        
        # Execution Summary
        lines.append(f"{h2}执行摘要\n")
        
        total_issues = issues.total_issues if issues and hasattr(issues, 'total_issues') else 0
        lines.append(f"{list_item}{bold}问题总数{bold}: {total_issues}")
        
        if issues and hasattr(issues, "by_severity") and issues.by_severity:
            for sev, count in issues.by_severity.items():
                lines.append(f"  {list_item}{sev}: {count}")
        lines.append("")
        
        # Overview Summary
        lines.append(f"{h2}总览摘要\n")
        if summary and hasattr(summary, "summary"):
            lines.append(f"{summary.summary}\n")
        else:
            lines.append("无总览信息\n")
            
        # Issues List
        lines.append(f"{h2}问题清单\n")
        if issues and hasattr(issues, "issues") and issues.issues and max_issues > 0:
            display_issues = issues.issues[:max_issues]
            lines.append(f"{bold}显示前 {len(display_issues)} 条，共 {len(issues.issues)} 条问题{bold}\n")
            
            for i, issue in enumerate(display_issues, 1):
                rule_id = getattr(issue, 'rule_id', 'Unknown')
                severity = getattr(issue, 'severity', 'Unknown')
                device_name = getattr(issue, 'device_name', 'Unknown')
                actual_value = getattr(issue, 'actual_value', 'Unknown')
                
                lines.append(f"{h3}{i}. [{severity}] {rule_id}")
                lines.append(f"{list_item}{bold}设备名称{bold}: {device_name}")
                lines.append(f"{list_item}{bold}实际值{bold}: {actual_value}")
                lines.append("")
        elif max_issues == 0:
            lines.append("问题显示被禁用 (max_issues=0)。\n")
        else:
            lines.append("没有发现问题。\n")
            
        import datetime
        if is_md:
            lines.append("---")
        else:
            lines.append("-" * 20)
        lines.append(f"生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(lines)

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
