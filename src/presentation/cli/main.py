import argparse
import sys

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

    # summary
    summary_parser = subparsers.add_parser("summary", help="View summary")
    summary_parser.add_argument("--run", required=True, help="Run ID")

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

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    print(f"Executing command: {args.command}")

if __name__ == "__main__":
    main()
