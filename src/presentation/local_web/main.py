from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
import os
from src.application.query_services import QueryService
from src.application.recognition_services.recognition_service import RecognitionService

app = FastAPI(title="CheckTool Local UI")
templates = Jinja2Templates(directory="src/presentation/local_web/templates")
query_service = QueryService()
recognition_service = RecognitionService()

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
