from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from backend.ai.categorize import categorize_task
from backend.ai.client import AIUnavailableError
from backend.ai.parse_task import parse_task_text
from backend.db import get_session
from backend.schemas import CategorySuggestion, ParseRequest, TaskProposal, TaskUpdate
from backend.services import task_service

router = APIRouter(prefix="/tasks", tags=["ai"])


@router.post("/parse", response_model=TaskProposal)
def parse_task(data: ParseRequest):
    try:
        return parse_task_text(data.text)
    except AIUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/{task_id}/categorize", response_model=CategorySuggestion)
def categorize_existing_task(
    task_id: int,
    apply: bool = Query(False),
    session: Session = Depends(get_session),
):
    task = task_service.get_task(session, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    categories = task_service.list_categories(session)
    category_names = [c.name for c in categories]

    try:
        suggestion = categorize_task(task.title, task.description, category_names)
    except AIUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if apply:
        matched = next((c for c in categories if c.name == suggestion["category"]), None)
        update = TaskUpdate(
            priority=suggestion["priority"],
            category_id=matched.id if matched else task.category_id,
        )
        task_service.update_task(session, task_id, update)

    return suggestion
