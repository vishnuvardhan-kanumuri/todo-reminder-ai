from datetime import datetime

from backend.models import TaskStatus
from backend.schemas import CategoryCreate, TaskCreate, TaskUpdate
from backend.services import task_service


def test_create_and_get_task(session):
    task = task_service.create_task(session, TaskCreate(title="Buy milk"))
    fetched = task_service.get_task(session, task.id)
    assert fetched is not None
    assert fetched.title == "Buy milk"
    assert fetched.status == TaskStatus.pending


def test_update_task(session):
    task = task_service.create_task(session, TaskCreate(title="Draft"))
    updated = task_service.update_task(session, task.id, TaskUpdate(title="Final"))
    assert updated.title == "Final"


def test_delete_task(session):
    task = task_service.create_task(session, TaskCreate(title="Temp"))
    assert task_service.delete_task(session, task.id) is True
    assert task_service.get_task(session, task.id) is None
    assert task_service.delete_task(session, task.id) is False


def test_complete_task_marks_status_and_timestamp(session):
    task = task_service.create_task(session, TaskCreate(title="One-off"))
    completed = task_service.complete_task(session, task.id)
    assert completed.status == TaskStatus.completed
    assert completed.completed_at is not None


def test_complete_recurring_task_generates_next_instance(session):
    due = datetime(2026, 7, 20, 9, 0)
    task = task_service.create_task(
        session,
        TaskCreate(title="Water plants", due_datetime=due, recurrence_rule="weekly"),
    )
    task_service.complete_task(session, task.id)

    pending = task_service.list_tasks(session, status=TaskStatus.pending)
    assert len(pending) == 1
    sibling = pending[0]
    assert sibling.title == "Water plants"
    assert sibling.due_datetime == datetime(2026, 7, 27, 9, 0)
    assert sibling.recurrence_parent_id == task.id


def test_snooze_task_increments_count(session):
    task = task_service.create_task(session, TaskCreate(title="Call bank"))
    until = datetime(2026, 8, 1)
    snoozed = task_service.snooze_task(session, task.id, until)
    assert snoozed.snooze_count == 1
    assert snoozed.snooze_until == until

    snoozed_again = task_service.snooze_task(session, task.id, until)
    assert snoozed_again.snooze_count == 2


def test_category_crud(session):
    category = task_service.create_category(session, CategoryCreate(name="Work", color="#ff0000"))
    assert category.id is not None
    assert task_service.list_categories(session) == [category]
    assert task_service.delete_category(session, category.id) is True
    assert task_service.list_categories(session) == []


def test_list_tasks_filters_by_status(session):
    a = task_service.create_task(session, TaskCreate(title="A"))
    task_service.create_task(session, TaskCreate(title="B"))
    task_service.complete_task(session, a.id)

    pending = task_service.list_tasks(session, status=TaskStatus.pending)
    completed = task_service.list_tasks(session, status=TaskStatus.completed)
    assert [t.title for t in pending] == ["B"]
    assert [t.title for t in completed] == ["A"]
