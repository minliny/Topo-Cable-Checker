from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import os
from src.application.query_services import QueryService

app = FastAPI(title="CheckTool Local UI")
templates = Jinja2Templates(directory="src/presentation/local_web/templates")
query_service = QueryService()

@app.get("/")
async def task_list(request: Request):
    tasks = query_service.get_task_list()
    return templates.TemplateResponse(request=request, name="task_list.html", context={"tasks": tasks})

@app.get("/task/{task_id}")
async def task_detail(request: Request, task_id: str):
    task = query_service.get_task_summary(task_id)
    rec = query_service.get_recognition_summary(task_id)
    return templates.TemplateResponse(request=request, name="task_detail.html", context={"task": task, "recognition": rec})

@app.get("/run/{run_id}")
async def run_overview(request: Request, run_id: str):
    overview = query_service.get_run_overview(run_id)
    issues = query_service.list_issue_items(run_id)
    return templates.TemplateResponse(request=request, name="run_overview.html", context={"overview": overview, "issues": issues})

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
