from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    archived = "archived"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskSource(str, Enum):
    manual = "manual"
    ai_parsed = "ai_parsed"


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    color: str | None = None
    created_at: datetime = Field(default_factory=utcnow)


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None = None
    due_datetime: datetime | None = Field(default=None, index=True)
    priority: TaskPriority = Field(default=TaskPriority.medium)
    status: TaskStatus = Field(default=TaskStatus.pending, index=True)
    category_id: int | None = Field(default=None, foreign_key="category.id")
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    recurrence_rule: str | None = None
    recurrence_parent_id: int | None = Field(default=None, foreign_key="task.id")

    snooze_until: datetime | None = None
    snooze_count: int = Field(default=0)

    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    completed_at: datetime | None = None

    # Populated by later phases (Calendar sync, AI parsing, escalation agent);
    # present now so the schema never needs a migration to add them.
    google_event_id: str | None = None
    source: TaskSource = Field(default=TaskSource.manual)
    ai_confidence: float | None = None
    last_nudged_at: datetime | None = None
    is_flagged: bool = Field(default=False)
