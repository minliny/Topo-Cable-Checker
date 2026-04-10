from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
import os
import json
from src.application.query_services import QueryService
from src.application.recognition_services.recognition_service import RecognitionService
from src.application.rule_governance_service import RuleGovernanceService
from src.application.rule_editor_service import RuleEditorService
from src.infrastructure.repository import TaskRepository, BaselineRepository, ResultRepository
from src.infrastructure.excel_reader import ExcelReader

app = FastAPI(title="CheckTool Local UI")
templates = Jinja2Templates(directory="src/presentation/local_web/templates")

# Initialize repositories (Composition Root)
task_repo = TaskRepository()
baseline_repo = BaselineRepository()
result_repo = ResultRepository()
excel_reader = ExcelReader()

# Initialize services with injected dependencies
query_service = QueryService(task_repo=task_repo, result_repo=result_repo)
recognition_service = RecognitionService(task_repo=task_repo, result_repo=result_repo, excel_reader=excel_reader)
rule_governance = RuleGovernanceService(baseline_repo=baseline_repo)
rule_editor = RuleEditorService(repo=baseline_repo)

@app.get("/")
async def task_list(request: Request):
    tasks = query_service.get_task_list()
    return templates.TemplateResponse(request=request, name="task_list.html", context={"tasks": tasks})

@app.get("/task/{task_id}")
async def task_detail(request: Request, task_id: str):
    task = query_service.get_task_summary(task_id)
    rec = query_service.get_recognition_summary(task_id)
    return templates.TemplateResponse(request=request, name="task_detail.html", context={"task": task, "recognition": rec})

@app.post("/task/{task_id}/confirm")
async def confirm_recognition(request: Request, task_id: str):
    recognition_service.confirm_recognition(task_id)
    return RedirectResponse(url=f"/task/{task_id}", status_code=303)

@app.get("/run/{run_id}")
async def run_overview(request: Request, run_id: str, severity: str = None, rule_id: str = None, device_name: str = None):
    overview = query_service.get_run_overview(run_id)
    
    filters = {}
    if severity: filters["severity"] = severity
    if rule_id: filters["rule_id"] = rule_id
    if device_name: filters["device_name"] = device_name
    
    issues_result = query_service.list_issue_items(run_id, filters)
    exports = query_service.list_export_artifacts(run_id)
    
    return templates.TemplateResponse(
        request=request, 
        name="run_overview.html", 
        context={
            "overview": overview, 
            "issues": issues_result.items,
            "before_count": issues_result.before_count,
            "after_count": issues_result.after_count,
            "filters": filters,
            "exports": exports
        }
    )

@app.get("/download/{run_id}/{fmt}")
async def download_export(run_id: str, fmt: str):
    artifact = query_service.get_export_artifact(run_id, fmt)
    if artifact:
        file_path = os.path.join("data", artifact.filename)
        if os.path.exists(file_path):
            return FileResponse(file_path, filename=artifact.filename)
    return {"error": "File not found"}

@app.get("/review/{run_id}/{device_name}")
async def device_review(request: Request, run_id: str, device_name: str):
    review = query_service.get_device_review(run_id, device_name)
    return templates.TemplateResponse(request=request, name="device_review.html", context={"review": review})

@app.get("/diff/{diff_id}")
async def diff_summary(request: Request, diff_id: str):
    diff = query_service.get_recheck_diff(diff_id)
    return templates.TemplateResponse(request=request, name="diff_summary.html", context={"diff": diff})

# --- Governance Routes ---

@app.get("/rules")
async def rules_list(request: Request, baseline_id: str = "B001"):
    # Using a default baseline_id for demonstration if none provided
    rules = rule_governance.list_rule_definitions(baseline_id)
    errors = {e.rule_id: e for e in rule_governance.list_compile_errors(baseline_id)}
    return templates.TemplateResponse(request=request, name="rules_list.html", context={"rules": rules, "errors": errors, "baseline_id": baseline_id})

@app.get("/rules/{baseline_id}/{rule_id}")
async def rule_detail(request: Request, baseline_id: str, rule_id: str):
    definition = rule_governance.get_rule_definition(baseline_id, rule_id)
    compiled = rule_governance.get_compiled_rule(baseline_id, rule_id)
    errors = rule_governance.list_compile_errors(baseline_id)
    error = next((e for e in errors if e.rule_id == rule_id), None)
    
    return templates.TemplateResponse(request=request, name="rule_detail.html", context={
        "definition": definition,
        "compiled": compiled,
        "error": error,
        "baseline_id": baseline_id
    })

@app.get("/templates")
async def templates_list(request: Request):
    registry = rule_governance.list_template_registry()
    return templates.TemplateResponse(request=request, name="templates_list.html", context={"registry": registry})

# --- Rule Editor Routes ---

@app.get("/rule-editor/{baseline_id}")
async def rule_editor_list(request: Request, baseline_id: str):
    baseline = rule_editor.get_editor_baseline(baseline_id)
    rules = rule_editor.list_editor_rules(baseline_id)
    return templates.TemplateResponse(request=request, name="rule_editor_list.html", context={"baseline": baseline, "rules": rules})

@app.get("/rule-editor/{baseline_id}/{rule_id}")
async def rule_editor_detail(request: Request, baseline_id: str, rule_id: str):
    draft = rule_editor.get_editor_rule(baseline_id, rule_id)
    if not draft:
        return {"error": "Draft not found"}
    raw_json = json.dumps(draft.raw_definition, indent=2)
    return templates.TemplateResponse(request=request, name="rule_editor_detail.html", context={"draft": draft, "baseline_id": baseline_id, "raw_json": raw_json})

@app.post("/rule-editor/{baseline_id}/save-draft")
async def save_rule_draft(request: Request, baseline_id: str):
    form_data = await request.form()
    action = form_data.get("action")
    rule_id = form_data.get("rule_id")
    raw_json = form_data.get("raw_definition_json")
    
    try:
        rule_def = json.loads(raw_json)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format"}
        
    rule_def["language_version"] = form_data.get("language_version")
    rule_def["target_type"] = form_data.get("target_type")
    rule_def["severity"] = form_data.get("severity")
    rule_def["enabled"] = form_data.get("enabled") == "on"

    rule_editor.save_rule_draft(baseline_id, rule_id, rule_def)
    
    draft = rule_editor.get_editor_rule(baseline_id, rule_id)
    context = {"draft": draft, "baseline_id": baseline_id, "raw_json": json.dumps(rule_def, indent=2)}

    if action == "validate":
        validation = rule_editor.validate_rule_draft(rule_id, rule_def)
        context["validation_result"] = validation
    elif action == "preview":
        preview = rule_editor.compile_rule_preview(rule_id, rule_def)
        context["compile_preview"] = preview

    return templates.TemplateResponse(request=request, name="rule_editor_detail.html", context=context)

@app.post("/rule-editor/{baseline_id}/publish")
async def publish_baseline(request: Request, baseline_id: str):
    success, new_version, count, msg = rule_editor.publish_baseline_version(baseline_id, "Publish from UI")
    
    if success:
        return RedirectResponse(url=f"/rule-editor/{baseline_id}", status_code=303)
    else:
        baseline = rule_editor.get_editor_baseline(baseline_id)
        rules = rule_editor.list_editor_rules(baseline_id)
        return templates.TemplateResponse(request=request, name="rule_editor_list.html", context={"baseline": baseline, "rules": rules, "publish_error": msg})

# --- Baseline History & Diff Routes ---

@app.get("/baselines")
async def baselines_list(request: Request, baseline_id: str = "B001"):
    versions = rule_editor.list_baseline_versions(baseline_id)
    return templates.TemplateResponse(request=request, name="baselines_list.html", context={"versions": versions, "baseline_id": baseline_id})

@app.post("/baselines/rollback")
async def rollback_baseline(request: Request, baseline_id: str = Form(...), version: str = Form(...)):
    success, new_ver, msg = rule_editor.rollback_to_version(baseline_id, version)
    if success:
        return RedirectResponse(url=f"/rule-editor/{baseline_id}", status_code=303)
    return {"error": f"Rollback failed: {msg}"}

@app.get("/baselines/{version}")
async def baseline_version_detail(request: Request, version: str, baseline_id: str = "B001"):
    # Reusing rule_governance list_rule_definitions would need adaptation to read historical versions.
    # For MVP, we will use a quick list representation.
    baseline = baseline_repo.get_by_id(baseline_id)
    rules_dict = rule_editor._get_rule_set_for_version(baseline, version)
    return templates.TemplateResponse(request=request, name="baseline_version_detail.html", context={"version": version, "rules": rules_dict, "baseline_id": baseline_id})

@app.get("/baselines/{baseline_id}/diff")
async def baseline_diff_view(request: Request, baseline_id: str, v1: str, v2: str):
    diff = rule_editor.get_baseline_diff(baseline_id, v1, v2)
    return templates.TemplateResponse(request=request, name="baseline_diff.html", context={"diff": diff})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
