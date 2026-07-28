from datetime import datetime

from sqlmodel import Session

from backend.ai import categorize as ai_categorize
from backend.ai import parse_task as ai_parse_task
from backend.models import Category, Task, TaskPriority, TaskStatus
from backend.schemas import CategoryCreate, TaskCreate, TaskUpdate
from backend.services import task_service


def _task_dict(task: Task) -> dict:
    return task.model_dump(mode="json")


def _category_dict(category: Category) -> dict:
    return category.model_dump(mode="json")


def list_tasks(
    session: Session,
    status: TaskStatus | None = None,
    category_id: int | None = None,
    due_before: datetime | None = None,
    due_after: datetime | None = None,
    tag: str | None = None,
) -> list[dict]:
    tasks = task_service.list_tasks(
        session,
        status=status,
        category_id=category_id,
        due_before=due_before,
        due_after=due_after,
        tag=tag,
    )
    return [_task_dict(t) for t in tasks]


def get_task(session: Session, task_id: int) -> dict:
    task = task_service.get_task(session, task_id)
    if task is None:
        raise ValueError(f"Task {task_id} not found")
    return _task_dict(task)


def create_task(
    session: Session,
    title: str,
    description: str | None = None,
    due_datetime: datetime | None = None,
    priority: TaskPriority = TaskPriority.medium,
    category_id: int | None = None,
    tags: list[str] | None = None,
    recurrence_rule: str | None = None,
) -> dict:
    data = TaskCreate(
        title=title,
        description=description,
        due_datetime=due_datetime,
        priority=priority,
        category_id=category_id,
        tags=tags or [],
        recurrence_rule=recurrence_rule,
    )
    return _task_dict(task_service.create_task(session, data))


def update_task(
    session: Session,
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    clear_description: bool = False,
    due_datetime: datetime | None = None,
    clear_due_datetime: bool = False,
    priority: TaskPriority | None = None,
    status: TaskStatus | None = None,
    category_id: int | None = None,
    clear_category: bool = False,
    tags: list[str] | None = None,
    recurrence_rule: str | None = None,
    clear_recurrence_rule: bool = False,
) -> dict:
    fields: dict = {}
    if title is not None:
        fields["title"] = title
    if description is not None:
        fields["description"] = description
    elif clear_description:
        fields["description"] = None
    if due_datetime is not None:
        fields["due_datetime"] = due_datetime
    elif clear_due_datetime:
        fields["due_datetime"] = None
    if priority is not None:
        fields["priority"] = priority
    if status is not None:
        fields["status"] = status
    if category_id is not None:
        fields["category_id"] = category_id
    elif clear_category:
        fields["category_id"] = None
    if tags is not None:
        fields["tags"] = tags
    if recurrence_rule is not None:
        fields["recurrence_rule"] = recurrence_rule
    elif clear_recurrence_rule:
        fields["recurrence_rule"] = None

    task = task_service.update_task(session, task_id, TaskUpdate(**fields))
    if task is None:
        raise ValueError(f"Task {task_id} not found")
    return _task_dict(task)


def delete_task(session: Session, task_id: int) -> dict:
    if not task_service.delete_task(session, task_id):
        raise ValueError(f"Task {task_id} not found")
    return {"deleted": True, "task_id": task_id}


def complete_task(session: Session, task_id: int) -> dict:
    task = task_service.complete_task(session, task_id)
    if task is None:
        raise ValueError(f"Task {task_id} not found")
    return _task_dict(task)


def snooze_task(session: Session, task_id: int, until: datetime) -> dict:
    task = task_service.snooze_task(session, task_id, until)
    if task is None:
        raise ValueError(f"Task {task_id} not found")
    return _task_dict(task)


def list_categories(session: Session) -> list[dict]:
    return [_category_dict(c) for c in task_service.list_categories(session)]


def create_category(session: Session, name: str, color: str | None = None) -> dict:
    category = task_service.create_category(session, CategoryCreate(name=name, color=color))
    return _category_dict(category)


def delete_category(session: Session, category_id: int) -> dict:
    if not task_service.delete_category(session, category_id):
        raise ValueError(f"Category {category_id} not found")
    return {"deleted": True, "category_id": category_id}


def parse_task_text(text: str) -> dict:
    return ai_parse_task.parse_task_text(text)


def categorize_task(session: Session, task_id: int, apply: bool = False) -> dict:
    task = task_service.get_task(session, task_id)
    if task is None:
        raise ValueError(f"Task {task_id} not found")

    categories = task_service.list_categories(session)
    category_names = [c.name for c in categories]
    suggestion = ai_categorize.categorize_task(task.title, task.description, category_names)

    if apply:
        matched = next((c for c in categories if c.name == suggestion["category"]), None)
        update = TaskUpdate(
            priority=suggestion["priority"],
            category_id=matched.id if matched else task.category_id,
        )
        task_service.update_task(session, task_id, update)

    return suggestion
