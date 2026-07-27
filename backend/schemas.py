from datetime import datetime

from pydantic import BaseModel

from backend.models import TaskPriority, TaskStatus


class CategoryCreate(BaseModel):
    name: str
    color: str | None = None


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    due_datetime: datetime | None = None
    priority: TaskPriority = TaskPriority.medium
    category_id: int | None = None
    tags: list[str] = []
    recurrence_rule: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_datetime: datetime | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    category_id: int | None = None
    tags: list[str] | None = None
    recurrence_rule: str | None = None


class SnoozeRequest(BaseModel):
    until: datetime
