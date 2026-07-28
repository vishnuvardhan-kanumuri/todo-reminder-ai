import asyncio
from datetime import datetime

import pytest

from backend.ai.client import AIUnavailableError
from backend.mcp_server import tools
from backend.mcp_server.server import mcp
from backend.models import TaskPriority, TaskStatus
from backend.schemas import CategoryCreate, TaskCreate


def test_create_and_get_task(session):
    created = tools.create_task(session, "Buy milk", tags=["errand"])
    assert created["title"] == "Buy milk"
    assert created["tags"] == ["errand"]

    fetched = tools.get_task(session, created["id"])
    assert fetched == created


def test_get_task_not_found_raises(session):
    with pytest.raises(ValueError, match="Task 999 not found"):
        tools.get_task(session, 999)


def test_list_tasks_filters_by_status(session):
    a = tools.create_task(session, "A")
    tools.create_task(session, "B")
    tools.complete_task(session, a["id"])

    pending = tools.list_tasks(session, status=TaskStatus.pending)
    completed = tools.list_tasks(session, status=TaskStatus.completed)
    assert [t["title"] for t in pending] == ["B"]
    assert [t["title"] for t in completed] == ["A"]


def test_update_task_sets_fields(session):
    task = tools.create_task(session, "Draft")
    updated = tools.update_task(session, task["id"], title="Final", priority=TaskPriority.high)
    assert updated["title"] == "Final"
    assert updated["priority"] == "high"


def test_update_task_clear_flags(session):
    task = tools.create_task(
        session,
        "Has extras",
        description="detail",
        due_datetime=datetime(2026, 8, 1),
        recurrence_rule="weekly",
    )

    cleared = tools.update_task(
        session,
        task["id"],
        clear_description=True,
        clear_due_datetime=True,
        clear_recurrence_rule=True,
    )
    assert cleared["description"] is None
    assert cleared["due_datetime"] is None
    assert cleared["recurrence_rule"] is None


def test_update_task_clear_category(session):
    category = tools.create_category(session, "Work")
    task = tools.create_task(session, "Report", category_id=category["id"])
    assert task["category_id"] == category["id"]

    cleared = tools.update_task(session, task["id"], clear_category=True)
    assert cleared["category_id"] is None


def test_update_task_not_found_raises(session):
    with pytest.raises(ValueError, match="Task 999 not found"):
        tools.update_task(session, 999, title="x")


def test_delete_task(session):
    task = tools.create_task(session, "Temp")
    assert tools.delete_task(session, task["id"]) == {"deleted": True, "task_id": task["id"]}
    with pytest.raises(ValueError):
        tools.delete_task(session, task["id"])


def test_complete_recurring_task_generates_next_instance(session):
    due = datetime(2026, 7, 20, 9, 0)
    task = tools.create_task(session, "Water plants", due_datetime=due, recurrence_rule="weekly")
    tools.complete_task(session, task["id"])

    pending = tools.list_tasks(session, status=TaskStatus.pending)
    assert len(pending) == 1
    assert pending[0]["title"] == "Water plants"
    assert pending[0]["recurrence_parent_id"] == task["id"]


def test_complete_task_not_found_raises(session):
    with pytest.raises(ValueError, match="Task 999 not found"):
        tools.complete_task(session, 999)


def test_snooze_task_increments_count(session):
    task = tools.create_task(session, "Call bank")
    until = datetime(2026, 8, 1)
    snoozed = tools.snooze_task(session, task["id"], until)
    assert snoozed["snooze_count"] == 1

    snoozed_again = tools.snooze_task(session, task["id"], until)
    assert snoozed_again["snooze_count"] == 2


def test_snooze_task_not_found_raises(session):
    with pytest.raises(ValueError, match="Task 999 not found"):
        tools.snooze_task(session, 999, datetime(2026, 8, 1))


def test_category_crud(session):
    category = tools.create_category(session, "Work", color="#ff0000")
    assert category["name"] == "Work"
    assert tools.list_categories(session) == [category]
    assert tools.delete_category(session, category["id"]) == {
        "deleted": True,
        "category_id": category["id"],
    }
    assert tools.list_categories(session) == []


def test_delete_category_not_found_raises(session):
    with pytest.raises(ValueError, match="Category 999 not found"):
        tools.delete_category(session, 999)


def test_parse_task_text_raises_when_ai_unavailable(monkeypatch):
    monkeypatch.setattr("backend.ai.parse_task.get_client", lambda: None)
    with pytest.raises(AIUnavailableError):
        tools.parse_task_text("remind me to call mom Sunday evening")


def test_categorize_task_raises_when_ai_unavailable(session, monkeypatch):
    task = tools.create_task(session, "Submit report")
    monkeypatch.setattr("backend.ai.categorize.get_client", lambda: None)
    with pytest.raises(AIUnavailableError):
        tools.categorize_task(session, task["id"])


def test_categorize_task_not_found_raises(session):
    with pytest.raises(ValueError, match="Task 999 not found"):
        tools.categorize_task(session, 999)


# --- MCP tool registration / schema smoke tests -----------------------------


def test_all_tools_registered():
    registered = {t.name for t in asyncio.run(mcp.list_tools())}
    assert registered == {
        "list_tasks",
        "get_task",
        "create_task",
        "update_task",
        "delete_task",
        "complete_task",
        "snooze_task",
        "list_categories",
        "create_category",
        "delete_category",
        "parse_task_text",
        "categorize_task",
    }


def test_create_task_schema_has_priority_enum():
    tool = next(t for t in asyncio.run(mcp.list_tools()) if t.name == "create_task")
    schema = tool.input_schema
    priority_schema = schema["properties"]["priority"]
    ref = priority_schema.get("$ref") or priority_schema.get("allOf", [{}])[0].get("$ref")
    assert ref is not None
    def_name = ref.rsplit("/", 1)[-1]
    assert schema["$defs"][def_name]["enum"] == ["low", "medium", "high"]
    assert schema["required"] == ["title"]
