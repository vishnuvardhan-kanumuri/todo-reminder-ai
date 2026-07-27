from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.db import get_session
from backend.models import Task, TaskStatus
from backend.schemas import SnoozeRequest, TaskCreate, TaskUpdate
from backend.services import task_service

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("", response_model=list[Task])
def list_tasks(
    status: TaskStatus | None = None,
    category_id: int | None = None,
    due_before: datetime | None = None,
    due_after: datetime | None = None,
    tag: str | None = None,
    session: Session = Depends(get_session),
):
    return task_service.list_tasks(
        session,
        status=status,
        category_id=category_id,
        due_before=due_before,
        due_after=due_after,
        tag=tag,
    )


@router.post("", response_model=Task, status_code=201)
def create_task(data: TaskCreate, session: Session = Depends(get_session)):
    return task_service.create_task(session, data)


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = task_service.get_task(session, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=Task)
def update_task(task_id: int, data: TaskUpdate, session: Session = Depends(get_session)):
    task = task_service.update_task(session, task_id, data)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    deleted = task_service.delete_task(session, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")


@router.post("/{task_id}/complete", response_model=Task)
def complete_task(task_id: int, session: Session = Depends(get_session)):
    task = task_service.complete_task(session, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/{task_id}/snooze", response_model=Task)
def snooze_task(task_id: int, data: SnoozeRequest, session: Session = Depends(get_session)):
    task = task_service.snooze_task(session, task_id, data.until)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
