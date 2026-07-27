from datetime import datetime

from sqlmodel import Session, select

from backend.models import Category, Task, TaskStatus


def create_task(session: Session, task: Task) -> Task:
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def get_task(session: Session, task_id: int) -> Task | None:
    return session.get(Task, task_id)


def list_tasks(
    session: Session,
    status: TaskStatus | None = None,
    category_id: int | None = None,
    due_before: datetime | None = None,
    due_after: datetime | None = None,
    tag: str | None = None,
) -> list[Task]:
    query = select(Task)
    if status is not None:
        query = query.where(Task.status == status)
    if category_id is not None:
        query = query.where(Task.category_id == category_id)
    if due_before is not None:
        query = query.where(Task.due_datetime <= due_before)
    if due_after is not None:
        query = query.where(Task.due_datetime >= due_after)
    tasks = list(session.exec(query))
    if tag is not None:
        tasks = [t for t in tasks if tag in (t.tags or [])]
    return tasks


def save_task(session: Session, task: Task) -> Task:
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task(session: Session, task: Task) -> None:
    session.delete(task)
    session.commit()


def create_category(session: Session, category: Category) -> Category:
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def get_category(session: Session, category_id: int) -> Category | None:
    return session.get(Category, category_id)


def list_categories(session: Session) -> list[Category]:
    return list(session.exec(select(Category)))


def delete_category(session: Session, category: Category) -> None:
    session.delete(category)
    session.commit()
