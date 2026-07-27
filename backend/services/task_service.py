from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from sqlmodel import Session

from backend import crud
from backend.models import Category, Task, TaskStatus, utcnow
from backend.schemas import CategoryCreate, TaskCreate, TaskUpdate


def compute_next_due(current: datetime, rule: str) -> datetime:
    """rule grammar: '<daily|weekly|monthly>[:<interval>]', e.g. 'weekly:2'."""
    parts = rule.strip().lower().split(":")
    base = parts[0]
    interval = int(parts[1]) if len(parts) > 1 else 1

    if base == "daily":
        return current + timedelta(days=interval)
    if base == "weekly":
        return current + timedelta(weeks=interval)
    if base == "monthly":
        return current + relativedelta(months=interval)
    raise ValueError(f"Unknown recurrence rule: {rule}")


def create_task(session: Session, data: TaskCreate) -> Task:
    task = Task(**data.model_dump())
    return crud.create_task(session, task)


def list_tasks(
    session: Session,
    status: TaskStatus | None = None,
    category_id: int | None = None,
    due_before: datetime | None = None,
    due_after: datetime | None = None,
    tag: str | None = None,
) -> list[Task]:
    return crud.list_tasks(
        session,
        status=status,
        category_id=category_id,
        due_before=due_before,
        due_after=due_after,
        tag=tag,
    )


def get_task(session: Session, task_id: int) -> Task | None:
    return crud.get_task(session, task_id)


def update_task(session: Session, task_id: int, data: TaskUpdate) -> Task | None:
    task = crud.get_task(session, task_id)
    if task is None:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    task.updated_at = utcnow()
    return crud.save_task(session, task)


def delete_task(session: Session, task_id: int) -> bool:
    task = crud.get_task(session, task_id)
    if task is None:
        return False
    crud.delete_task(session, task)
    return True


def complete_task(session: Session, task_id: int) -> Task | None:
    task = crud.get_task(session, task_id)
    if task is None:
        return None

    task.status = TaskStatus.completed
    task.completed_at = utcnow()
    task.updated_at = utcnow()
    crud.save_task(session, task)

    if task.recurrence_rule and task.due_datetime:
        next_due = compute_next_due(task.due_datetime, task.recurrence_rule)
        sibling = Task(
            title=task.title,
            description=task.description,
            due_datetime=next_due,
            priority=task.priority,
            category_id=task.category_id,
            tags=list(task.tags or []),
            recurrence_rule=task.recurrence_rule,
            recurrence_parent_id=task.recurrence_parent_id or task.id,
            source=task.source,
        )
        crud.create_task(session, sibling)

    return task


def snooze_task(session: Session, task_id: int, until: datetime) -> Task | None:
    task = crud.get_task(session, task_id)
    if task is None:
        return None
    task.snooze_until = until
    task.snooze_count += 1
    task.updated_at = utcnow()
    return crud.save_task(session, task)


def create_category(session: Session, data: CategoryCreate) -> Category:
    category = Category(**data.model_dump())
    return crud.create_category(session, category)


def list_categories(session: Session) -> list[Category]:
    return crud.list_categories(session)


def delete_category(session: Session, category_id: int) -> bool:
    category = crud.get_category(session, category_id)
    if category is None:
        return False
    crud.delete_category(session, category)
    return True
