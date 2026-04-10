import argparse
import sys
import json

from src.application.baseline_services.baseline_service import BaselineService
from src.application.task_services.task_service import TaskService
from src.application.recognition_services.recognition_service import RecognitionService
from src.application.check_run_services.check_run_service import CheckRunService
from src.application.result_query_services.result_query_service import ResultQueryService
from src.application.review_services.review_service import ReviewService
from src.application.recheck_services.recheck_service import RecheckService
from src.application.export_services.export_service import ExportService
from src.crosscutting.errors.exceptions import CheckToolBaseError
from src.infrastructure.repository import TaskRepository, BaselineRepository, ResultRepository
from src.infrastructure.excel_reader import ExcelReader

def get_services():
    task_repo = TaskRepository()
    baseline_repo = BaselineRepository()
    result_repo = ResultRepository()
    excel_reader = ExcelReader()
    
    return {
        "baseline_service": BaselineService(baseline_repo),
        "task_service": TaskService(task_repo, baseline_repo),
        "recognition_service": RecognitionService(task_repo, result_repo, excel_reader),
        "check_run_service": CheckRunService(task_repo, baseline_repo, result_repo),
        "result_query_service": ResultQueryService(result_repo),
        "review_service": ReviewService(result_repo, task_repo),
        "recheck_service": RecheckService(result_repo),
        "export_service": ExportService(result_repo),
    }

def main():
    parser = argparse.ArgumentParser(prog="checktool", description="CheckTool CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # baseline list
    baseline_parser = subparsers.add_parser("baseline", help="Baseline management")
    baseline_parser.add_argument("action", choices=["list"], help="Action to perform")

    # task create
    task_parser = subparsers.add_parser("task", help="Task management")
    task_parser.add_argument("action", choices=["create"], help="Action to perform")
    task_parser.add_argument("--baseline", required=True, help="Baseline ID")
    task_parser.add_argument("--file", required=True, help="Source file path")

    # recognize
    recognize_parser = subparsers.add_parser("recognize", help="Recognize data")
    recognize_parser.add_argument("--task", required=True, help="Task ID")

    # confirm-recognition
    confirm_parser = subparsers.add_parser("confirm-recognition", help="Confirm recognition")
    confirm_parser.add_argument("--task", required=True, help="Task ID")

    # run
    run_parser = subparsers.add_parser("run", help="Run checks")
    run_parser.add_argument("--task", required=True, help="Task ID")
    run_parser.add_argument("--copy", dest="copy", action="store_true", help="Copy result to clipboard")
    run_parser.add_argument("--open", dest="open", action="store_true", help="Open result file in IDE")
    run_parser.add_argument("--result-format", default="markdown", choices=["markdown", "text"], help="Output result format")
    run_parser.add_argument("--max-issues", type=int, default=20, help="Max number of issues to display")

    # summary
    summary_parser = subparsers.add_parser("summary", help="View summary")
    summary_parser.add_argument("--run", required=True, help="Run ID")

    # statistics
    stats_parser = subparsers.add_parser("statistics", help="View statistics")
    stats_parser.add_argument("--run", required=True, help="Run ID")

    # issues
    issues_parser = subparsers.add_parser("issues", help="View issues")
    issues_parser.add_argument("--run", required=True, help="Run ID")

    # review
    review_parser = subparsers.add_parser("review", help="Review issues")
    review_parser.add_argument("--run", required=True, help="Run ID")
    review_parser.add_argument("--device", required=True, help="Device name")

    # diff
    diff_parser = subparsers.add_parser("diff", help="View diff")
    diff_parser.add_argument("--task", required=True, help="Task ID")
    diff_parser.add_argument("--prev", required=True, help="Previous run ID")
    diff_parser.add_argument("--curr", required=True, help="Current run ID")

    # export
    export_parser = subparsers.add_parser("export", help="Export results")
    export_parser.add_argument("--run", required=True, help="Run ID")
    export_parser.add_argument("--format", default="json", help="Export format")
    
    # task status helper (not explicitly required but useful for testing)
    status_parser = subparsers.add_parser("status", help="Get task status")
    status_parser.add_argument("--task", required=True, help="Task ID")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    try:
        services = get_services()
        
        if args.command == "baseline":
            svc = services["baseline_service"]
            res = svc.list_baselines()
            print("Baselines:")
            for b in res:
                print(f" - {b.baseline_id} (version: {b.baseline_version})")

        elif args.command == "task":
            svc = services["task_service"]
            task_id = svc.create_task(args.baseline, args.file)
            print(f"Task created: {task_id}")

        elif args.command == "recognize":
            svc = services["recognition_service"]
            res = svc.recognize_data(args.task)
            print(f"Recognized: {res}")

        elif args.command == "confirm-recognition":
            svc = services["recognition_service"]
            res = svc.confirm_recognition(args.task)
            print(f"Confirmed: {res}")

        elif args.command == "run":
            svc = services["check_run_service"]
            run_id = svc.run_checks(args.task)
            print(f"Run completed. Run ID: {run_id}")

            # Optional Result Delivery Integration
            if getattr(args, "copy", False) or getattr(args, "open", False):
                try:
                    # Fetch details for result delivery
                    query_svc = services["result_query_service"]
                    summary = query_svc.get_summary(run_id)
                    stats = query_svc.get_statistics(run_id)
                    issues = query_svc.get_issues(run_id)

                    print("ResultDelivery triggered")
                    from src.presentation.result_delivery import ResultDeliveryService
                    delivery_svc = ResultDeliveryService()
                    formatted = delivery_svc.format_output(
                        task_id=args.task,
                        run_id=run_id,
                        summary=summary,
                        stats=stats,
                        issues=issues,
                        max_issues=args.max_issues,
                        fmt=args.result_format
                    )

                    delivery_svc.deliver_result(
                        formatted,
                        copy=args.copy,
                        open_ide=args.open,
                        fmt=args.result_format
                    )
                except Exception as e:
                    print(f"Warning: Optional ResultDelivery failed: {e}")

        elif args.command == "summary":
            svc = services["result_query_service"]
            summary = svc.get_summary(args.run)
            if summary:
                print(f"Summary for {args.run}: {summary.summary}")
            else:
                print("Summary not found.")

        elif args.command == "statistics":
            svc = services["result_query_service"]
            stats = svc.get_statistics(args.run)
            if stats:
                print(f"Statistics for {args.run}:")
                print(f"  total_devices: {stats.total_devices}")
                print(f"  total_ports: {stats.total_ports}")
                print(f"  total_links: {stats.total_links}")
                print(f"  device_type_distribution: {stats.device_type_distribution}")
            else:
                print("Statistics not found.")

        elif args.command == "issues":
            svc = services["result_query_service"]
            issues = svc.get_issues(args.run)
            if issues:
                print(f"Issues for {args.run}: {len(issues.issues)}")
                print(f"  by_device: {issues.by_device}")
                print(f"  by_rule: {issues.by_rule}")
                print(f"  by_severity: {issues.by_severity}")
            else:
                print("Issues not found.")

        elif args.command == "review":
            svc = services["review_service"]
            ctx = svc.review_issues(args.run, args.device)
            print(f"Review context for {args.device}:")
            print(f"  connected_devices: {ctx.connected_devices}")
            print(f"  related_ports: {len(ctx.related_ports)}")
            print(f"  related_links: {len(ctx.related_links)}")
            print(f"  related_issues: {len(ctx.related_issues)}")

        elif args.command == "diff":
            svc = services["recheck_service"]
            diff = svc.generate_diff(args.task, args.prev, args.curr)
            print(f"Diff Summary:")
            print(f"  new: {diff.diff_data['new']}")
            print(f"  resolved: {diff.diff_data['resolved']}")
            print(f"  persistent: {diff.diff_data['persistent']}")
            print(f"  changed: {diff.diff_data['changed']}")
            print(f"\nRisk Trend:")
            print(f"  total_issues_diff: {diff.risk_trend['total_issues_diff']}")
            print(f"  severity_diff: {diff.risk_trend['severity_diff']}")
            print(f"  per_device_diff: {diff.risk_trend['per_device_diff']}")

        elif args.command == "export":
            svc = services["export_service"]
            art = svc.export(args.run, args.format)
            print(f"Exported artifact for {args.run}, format {art.format}")
            
        elif args.command == "status":
            svc = services["task_service"]
            status = svc.get_task_status(args.task)
            print(f"Task {args.task} status: {status}")

    except CheckToolBaseError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
